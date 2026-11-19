#!/usr/bin/env python3
"""Validate and drive a lane-DAG plan file (Markdown) for parallel subagent work.

Commands: validate, ready, check-lane, mark, tag. Run with -h for the plan format.
Exit codes: 0 success, 1 the check found problems (one line each on stdout),
2 usage error, unreadable plan, or git failure (message on stderr).
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field

# Each lane in flight is a diff the orchestrator checks by hand, so more than
# this many at once outruns careful review.
MAX_LANES_IN_FLIGHT = 4

STATUSES = ("pending", "running", "merged", "cut")
REQUIRED_COLUMNS = ("lane", "owns files", "status", "branch")

BUILTIN_MANIFESTS = frozenset(
    """package.json package-lock.json npm-shrinkwrap.json yarn.lock pnpm-lock.yaml
    bun.lockb bun.lock pyproject.toml poetry.lock uv.lock Pipfile Pipfile.lock
    requirements.txt go.mod go.sum Cargo.toml Cargo.lock Gemfile Gemfile.lock
    composer.json composer.lock""".split()
)
MANIFEST_GLOBS = ("requirements*.txt",)

BUILTIN_SUPPRESSIONS = (
    ".skip(", ".only(", ".todo(", "xit(", "xdescribe(", "fit(", "fdescribe(",
    "@pytest.mark.skip", "@pytest.mark.xfail", "t.Skip(", "@ts-ignore",
    "@ts-expect-error", "@ts-nocheck", "eslint-disable", "# type: ignore",
    "# noqa", "# pyright: ignore", "//nolint", "#[allow(", "@Disabled", "@Ignore",
)

PHASE_HEADING = re.compile(r"^(#{2,4}) Phase (\d+)\b")
ANY_HEADING = re.compile(r"^(#{1,6})\s")
HEADER_DIRECTIVE = re.compile(r"^\s*(Suppressions|Manifests):\s*(.*)$", re.I)
DEPENDS_DIRECTIVE = re.compile(r"^\s*Depends on:\s*(.*)$", re.I)
SCAFFOLD_DIRECTIVE = re.compile(r"^\s*Scaffold:\s*(\S+)", re.I)
TAG_DIRECTIVE = re.compile(r"^\s*Tag:\s*(\S+)", re.I)
DEPENDENCY_ITEM = re.compile(r"^(?:phase\s*)?(\d+)$", re.I)
SEPARATOR_CELL = re.compile(r"^:?-+:?$")
HUNK_HEADER = re.compile(r"^@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


class CommandError(Exception):
    """A usage, plan-reading or git failure; main() prints it to stderr and exits 2."""


# ---------------------------------------------------------------- data model


@dataclass
class Lane:
    """One row of a phase's lane table."""

    phase: int
    name: str
    status: str
    owns: list[str]
    tests: list[str]
    branch: str
    line_index: int

    @property
    def full_id(self) -> str:
        return f"{self.phase}/{self.name}"


@dataclass
class Phase:
    """One phase section: its directives, lane table layout and lanes."""

    number: int
    start: int
    end: int
    depends_on: list[int] = field(default_factory=list)
    scaffold: str | None = None
    scaffold_line: int | None = None
    tag: str | None = None
    tag_line: int | None = None
    columns: dict[str, int] = field(default_factory=dict)
    lanes: list[Lane] = field(default_factory=list)


@dataclass
class Plan:
    """A parsed plan file. `lines` keeps original text with line endings."""

    lines: list[str]
    suppressions: list[str]
    manifests: list[str]
    phases: list[Phase]
    problems: list[str]

    def find_phase(self, number: int) -> Phase | None:
        return next((p for p in self.phases if p.number == number), None)


# ------------------------------------------------------------------- parsing


def split_lines(text: str) -> list[str]:
    """Split on \\n only, keeping endings, so rewriting preserves every byte (including CRLF)."""
    return re.findall(r"[^\n]*\n|[^\n]+", text)


def content_of(line: str) -> str:
    """The line without its trailing line ending."""
    return line.rstrip("\r\n")


def ending_of(line: str) -> str:
    """The line ending of `line` ('' for an unterminated last line)."""
    return line[len(content_of(line)):]


def clean_item(item: str) -> str:
    """Trim whitespace and optional backticks around a list item."""
    return item.strip().strip("`").strip()


def split_list(cell: str) -> list[str]:
    """Split a comma-separated cell into cleaned, non-empty items."""
    return [i for i in (clean_item(p) for p in cell.split(",")) if i]


def cell_spans(line: str) -> list[tuple[int, int]]:
    """(start, end) offsets of each table cell's raw content, between unescaped pipes."""
    text = content_of(line)
    pipes = [i for i, c in enumerate(text) if c == "|" and (i == 0 or text[i - 1] != "\\")]
    spans = [(a + 1, b) for a, b in zip(pipes, pipes[1:])]
    if pipes and text[pipes[-1] + 1:].strip():
        spans.append((pipes[-1] + 1, len(text)))
    return spans


def row_cells(line: str) -> list[str]:
    """Stripped text of each cell in a table row."""
    text = content_of(line)
    return [text[a:b].strip() for a, b in cell_spans(line)]


def is_table_line(line: str) -> bool:
    return content_of(line).lstrip().startswith("|")


def is_separator_row(line: str) -> bool:
    """True for the `| --- | --- |` row under a table header."""
    cells = row_cells(line)
    return bool(cells) and all(SEPARATOR_CELL.match(c) for c in cells)


def normalize_path(raw: str) -> tuple[str | None, str | None]:
    """Return (path, error). A trailing '/' is kept to mean a directory."""
    path = raw
    while path.startswith("./"):
        path = path[2:]
    if path.startswith("/"):
        return None, f"{raw} is an absolute path; use a repo-relative path"
    if ".." in path.split("/"):
        return None, f"{raw} contains '..'; use a repo-relative path without '..'"
    if any(c in path for c in "*?["):
        return None, f"{raw} contains a glob character; list exact files or a directory ending in '/'"
    if not path.rstrip("/"):
        return None, f"{raw!r} is not a usable path"
    return path, None


def parse_paths(cell: str, label: str, problems: list[str]) -> list[str]:
    """Parse a path-list cell; bad paths are reported on `problems` and dropped."""
    paths = []
    for raw in split_list(cell):
        path, error = normalize_path(raw)
        if error:
            problems.append(f"{label}: {error}")
        else:
            paths.append(path)
    return paths


def find_phase_bounds(lines: list[str]) -> list[tuple[int, int, int]]:
    """(number, start, end) per phase heading; end is exclusive."""
    bounds = []
    current = None  # (number, level, start)
    for index, line in enumerate(lines):
        heading = ANY_HEADING.match(line)
        if not heading:
            continue
        phase = PHASE_HEADING.match(line)
        level = len(heading.group(1))
        if current and (phase or level <= current[1]):
            bounds.append((current[0], current[2], index))
            current = None
        if phase:
            current = (int(phase.group(2)), level, index)
    if current:
        bounds.append((current[0], current[2], len(lines)))
    return bounds


def parse_header(lines: list[str]) -> tuple[list[str], list[str]]:
    """Extra suppression patterns and manifest names from the header directives."""
    suppressions: list[str] = []
    manifests: list[str] = []
    for line in lines:
        match = HEADER_DIRECTIVE.match(content_of(line))
        if match:
            target = suppressions if match.group(1).lower() == "suppressions" else manifests
            target.extend(split_list(match.group(2)))
    return suppressions, manifests


def parse_dependencies(value: str, number: int, problems: list[str]) -> list[int]:
    """Parse the value of a `Depends on:` line."""
    deps = []
    for item in split_list(value):
        if item.lower() == "none":
            continue
        match = DEPENDENCY_ITEM.match(item)
        if match:
            deps.append(int(match.group(1)))
        else:
            problems.append(
                f"phase {number}: Depends on entry {item!r} is not 'phase <number>', a bare number or 'none'"
            )
    return deps


def parse_phase_directives(lines: list[str], phase: Phase, problems: list[str]) -> None:
    """Fill depends_on, scaffold and tag from the non-table lines of the phase."""
    for index in range(phase.start + 1, phase.end):
        if is_table_line(lines[index]):
            continue
        text = content_of(lines[index])
        if match := DEPENDS_DIRECTIVE.match(text):
            phase.depends_on.extend(parse_dependencies(match.group(1), phase.number, problems))
        elif (match := SCAFFOLD_DIRECTIVE.match(text)) and phase.scaffold is None:
            phase.scaffold, phase.scaffold_line = match.group(1), index
        elif (match := TAG_DIRECTIVE.match(text)) and phase.tag is None:
            phase.tag, phase.tag_line = match.group(1), index


def find_lane_table(lines: list[str], phase: Phase) -> tuple[int, int] | None:
    """Line range [header, end) of the first table whose header has a Lane column."""
    index = phase.start + 1
    while index < phase.end:
        if not is_table_line(lines[index]):
            index += 1
            continue
        block_end = index
        while block_end < phase.end and is_table_line(lines[block_end]):
            block_end += 1
        if "lane" in (c.lower() for c in row_cells(lines[index])):
            return index, block_end
        index = block_end
    return None


def parse_lane_row(
    lines: list[str], index: int, phase: Phase, problems: list[str]
) -> Lane | None:
    """Turn one table row into a Lane, reporting problems against the phase."""
    cells = row_cells(lines[index])

    def cell(column: str) -> str:
        position = phase.columns.get(column)
        return cells[position] if position is not None and position < len(cells) else ""

    name = clean_item(cell("lane"))
    if not name:
        problems.append(f"phase {phase.number}: table row on line {index + 1} has an empty Lane cell")
        return None
    label = f"phase {phase.number} lane {name}"
    status = clean_item(cell("status"))
    if status not in STATUSES:
        problems.append(f"{label}: status {status!r} is not one of {', '.join(STATUSES)}")
    owns = parse_paths(cell("owns files"), label, problems)
    tests = parse_paths(cell("tests"), label, problems)
    if not owns and status != "cut" and phase.scaffold is not None:
        problems.append(
            f"{label}: Owns files is empty but the phase has a Scaffold line; "
            "list the files this lane owns or set status to cut"
        )
    return Lane(phase.number, name, status, owns, tests, clean_item(cell("branch")), index)


def parse_lane_table(lines: list[str], phase: Phase, problems: list[str]) -> None:
    """Parse the phase's lane table, if any, into phase.lanes."""
    found = find_lane_table(lines, phase)
    if found is None:
        return
    header, end = found
    columns: dict[str, int] = {}
    for position, name in enumerate(row_cells(lines[header])):
        columns.setdefault(name.lower(), position)
    phase.columns = columns
    missing = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing:
        problems.append(
            f"phase {phase.number}: lane table is missing required column(s) "
            f"{', '.join(missing)}; required columns are Lane, Owns files, Status, Branch"
        )
        return
    seen: set[str] = set()
    for index in range(header + 1, end):
        if index == header + 1 and is_separator_row(lines[index]):
            continue
        lane = parse_lane_row(lines, index, phase, problems)
        if lane is None:
            continue
        if lane.name in seen:
            problems.append(f"phase {phase.number} lane {lane.name}: lane id appears more than once in the phase")
            continue
        seen.add(lane.name)
        phase.lanes.append(lane)


def parse_plan(text: str) -> Plan:
    """Parse plan text into a Plan; structural problems are collected in plan.problems."""
    lines = split_lines(text)
    bounds = find_phase_bounds(lines)
    first = bounds[0][1] if bounds else len(lines)
    suppressions, manifests = parse_header(lines[:first])
    problems: list[str] = []
    phases: list[Phase] = []
    first_heading: dict[int, int] = {}
    for number, start, end in bounds:
        if number in first_heading:
            problems.append(
                f"phase {number}: heading appears more than once "
                f"(lines {first_heading[number] + 1} and {start + 1}); phase numbers must be unique"
            )
        first_heading.setdefault(number, start)
        phase = Phase(number, start, end)
        parse_phase_directives(lines, phase, problems)
        parse_lane_table(lines, phase, problems)
        phases.append(phase)
    return Plan(lines, suppressions, manifests, phases, problems)


def read_plan(path: str) -> Plan:
    """Read and parse the plan file; an unreadable file is a CommandError."""
    try:
        with open(path, encoding="utf-8", newline="") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as error:
        raise CommandError(f"cannot read plan file {path}: {error}") from error
    return parse_plan(text)


# --------------------------------------------------------------- graph checks


def dependency_graph(plan: Plan) -> dict[int, set[int]]:
    """Phase number to the set of phase numbers it directly depends on."""
    graph: dict[int, set[int]] = {}
    for phase in plan.phases:
        graph.setdefault(phase.number, set()).update(phase.depends_on)
    return graph


def check_dependency_targets(plan: Plan) -> list[str]:
    """Report Depends on entries that name a phase that doesn't exist."""
    known = {p.number for p in plan.phases}
    return [
        f"phase {phase.number}: Depends on phase {dep}, which does not exist"
        for phase in plan.phases
        for dep in phase.depends_on
        if dep not in known
    ]


def find_cycles(graph: dict[int, set[int]]) -> list[list[int]]:
    """Each dependency cycle once, as a list of phase numbers in order."""
    cycles: list[list[int]] = []
    seen_cycles: set[frozenset[int]] = set()
    done: set[int] = set()

    def visit(node: int, stack: list[int]) -> None:
        if node in stack:
            cycle = stack[stack.index(node):]
            if frozenset(cycle) not in seen_cycles:
                seen_cycles.add(frozenset(cycle))
                cycles.append(cycle)
            return
        if node in done:
            return
        for dep in sorted(graph.get(node, ())):
            if dep in graph:
                visit(dep, stack + [node])
        done.add(node)

    for node in sorted(graph):
        visit(node, [])
    return cycles


def check_cycles(plan: Plan) -> list[str]:
    """Report dependency cycles, naming the phases in each."""
    return [
        "dependency cycle: " + " -> ".join(f"phase {n}" for n in cycle + [cycle[0]])
        for cycle in find_cycles(dependency_graph(plan))
    ]


def transitive_dependencies(graph: dict[int, set[int]], start: int) -> set[int]:
    """Every phase `start` depends on directly or indirectly (tolerates cycles)."""
    found: set[int] = set()
    pending = list(graph.get(start, ()))
    while pending:
        node = pending.pop()
        if node not in found:
            found.add(node)
            pending.extend(graph.get(node, ()))
    return found


def paths_overlap(a: str, b: str) -> bool:
    """True if equal, or one is a directory ('x/') whose segments prefix the other."""
    segments_a, segments_b = a.rstrip("/").split("/"), b.rstrip("/").split("/")
    short, long_, short_is_dir = (
        (segments_a, segments_b, a.endswith("/"))
        if len(segments_a) <= len(segments_b)
        else (segments_b, segments_a, b.endswith("/"))
    )
    if long_[: len(short)] != short:
        return False
    return len(short) == len(long_) or short_is_dir


def first_overlap(a: Lane, b: Lane) -> tuple[str, str] | None:
    """The first pair of owned paths of `a` and `b` that overlap."""
    for path_a in a.owns:
        for path_b in b.owns:
            if paths_overlap(path_a, path_b):
                return path_a, path_b
    return None


def check_ownership(plan: Plan) -> list[str]:
    """Report overlapping ownership between non-cut lanes that can run concurrently."""
    graph = dependency_graph(plan)
    lanes = [lane for phase in plan.phases for lane in phase.lanes if lane.status != "cut"]
    problems = []
    for later_index, later in enumerate(lanes):
        for earlier in lanes[:later_index]:
            if later.phase != earlier.phase and (
                earlier.phase in transitive_dependencies(graph, later.phase)
                or later.phase in transitive_dependencies(graph, earlier.phase)
            ):
                continue
            overlap = first_overlap(later, earlier)
            if overlap:
                via = "" if overlap[0] == overlap[1] else f" (overlaps {overlap[1]})"
                problems.append(
                    f"phase {later.phase} lane {later.name}: owns {overlap[0]}, "
                    f"also owned by phase {earlier.phase} lane {earlier.name}{via}"
                )
    return problems


def validate_plan(plan: Plan) -> list[str]:
    """Every problem in the plan: parse problems, bad dependencies, cycles, overlaps."""
    return plan.problems + check_dependency_targets(plan) + check_cycles(plan) + check_ownership(plan)


def ready_lanes(plan: Plan) -> list[Lane]:
    """Pending lanes that may start now, capped by MAX_LANES_IN_FLIGHT minus running lanes."""
    running = sum(1 for p in plan.phases for lane in p.lanes if lane.status == "running")
    room = max(0, MAX_LANES_IN_FLIGHT - running)
    tagged = {p.number for p in plan.phases if p.tag is not None}
    eligible = [
        lane
        for phase in plan.phases
        if phase.scaffold is not None
        and phase.tag is None
        and all(dep in tagged for dep in phase.depends_on)
        for lane in phase.lanes
        if lane.status == "pending"
    ]
    return eligible[:room]


# ------------------------------------------------------------------------ git


def run_git(repo: str, *args: str) -> str:
    """Run git in `repo` and return stdout; failures become CommandError with git's message."""
    try:
        result = subprocess.run(
            ["git", "-C", repo, "-c", "core.quotepath=off", *args],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
    except OSError as error:
        raise CommandError(f"cannot run git in {repo}: {error}") from error
    if result.returncode != 0:
        raise CommandError(
            f"git {' '.join(args)} failed in {repo}: {result.stderr.strip()}. "
            "Check that --repo is a git repository and that the base and branch names exist."
        )
    return result.stdout


def changed_paths(repo: str, base: str, branch: str) -> list[str]:
    """Paths changed on `branch` since `base`; renames count as a delete plus an add."""
    out = run_git(repo, "diff", "--name-only", "--no-renames", "-z", f"{base}...{branch}")
    return [p for p in out.split("\0") if p]


def added_lines(diff: str) -> list[tuple[str, int, str]]:
    """(file, new line number, text) for every added line of a `git diff -U0` output."""
    result = []
    path = None
    new_line = 0
    remaining_old = remaining_new = 0
    for line in diff.split("\n"):
        if remaining_old or remaining_new:
            if line.startswith("+"):
                result.append((path, new_line, line[1:]))
                new_line += 1
                remaining_new -= 1
            elif line.startswith("-"):
                remaining_old -= 1
            continue
        if line.startswith("+++ "):
            target = line[4:].split("\t")[0]
            path = target[2:] if target.startswith("b/") else None
        elif match := HUNK_HEADER.match(line):
            remaining_old = int(match.group(1) if match.group(1) is not None else 1)
            new_line = int(match.group(2))
            remaining_new = int(match.group(3) if match.group(3) is not None else 1)
    return result


def is_manifest(path: str, extra: list[str]) -> bool:
    """True if the path's basename (or full path) is a built-in or header-listed manifest."""
    base = path.rsplit("/", 1)[-1]
    return (
        base in BUILTIN_MANIFESTS
        or any(fnmatch.fnmatchcase(base, g) for g in MANIFEST_GLOBS)
        or base in extra
        or path in extra
    )


def is_owned(path: str, owns: list[str]) -> bool:
    """True if `path` equals an owned file or sits under an owned directory."""
    return any(path == o or (o.endswith("/") and path.startswith(o)) for o in owns)


def lane_violations(plan: Plan, lane: Lane, paths: list[str], diff: str) -> list[str]:
    """All mechanical violations for a lane's diff, as printable lines."""
    label = f"phase {lane.phase} lane {lane.name}"
    problems = []
    for path in paths:
        if not is_owned(path, lane.owns):
            problems.append(f"{label}: changed {path}, which is not in its Owns files")
        if is_manifest(path, plan.manifests):
            problems.append(
                f"{label}: changed {path}, a dependency manifest or lockfile; lanes must not edit these"
            )
    patterns = list(BUILTIN_SUPPRESSIONS) + plan.suppressions
    for path, number, text in added_lines(diff):
        for pattern in patterns:
            if pattern in text:
                problems.append(f'{path}:{number}: added "{pattern}"')
    return problems


# ------------------------------------------------------------- file rewriting


def write_atomically(path: str, text: str) -> None:
    """Replace `path` with `text` via a temp file in the same directory and os.replace."""
    directory = os.path.dirname(os.path.abspath(path))
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=directory, delete=False, prefix=".plan-", suffix=".tmp"
    )
    try:
        with handle:
            handle.write(text)
        shutil.copymode(path, handle.name)
        os.replace(handle.name, path)
    except BaseException:
        os.unlink(handle.name)
        raise


def replace_cell(line: str, span: tuple[int, int], value: str) -> str:
    """Swap the text of one cell, keeping its surrounding padding; empty cells get one space each side."""
    start, end = span
    raw = line[start:end]
    if not raw.strip():
        return line[:start] + f" {value} " + line[end:]
    lead = raw[: len(raw) - len(raw.lstrip())]
    trail = raw[len(raw.rstrip()):]
    return line[:start] + lead + value + trail + line[end:]


def rewrite_lane_cells(plan: Plan, lane: Lane, cells: dict[str, str]) -> str:
    """Plan text with the named cells ('status', 'branch') of the lane's row replaced."""
    phase = plan.find_phase(lane.phase)
    spans = cell_spans(plan.lines[lane.line_index])
    line = plan.lines[lane.line_index]
    # Replace right-to-left so earlier offsets stay valid.
    for column, value in sorted(cells.items(), key=lambda kv: -phase.columns[kv[0]]):
        position = phase.columns[column]
        if position >= len(spans):
            raise CommandError(
                f"phase {lane.phase} lane {lane.name}: row has no {column} cell to update; "
                "add the missing cells to the row first"
            )
        line = replace_cell(line, spans[position], value)
    lines = list(plan.lines)
    lines[lane.line_index] = line
    return "".join(lines)


def tag_insert_position(plan: Plan, phase: Phase) -> int:
    """Line index at which a new Tag line goes: after Scaffold, else after the heading's blank line."""
    if phase.scaffold_line is not None:
        return phase.scaffold_line + 1
    after_heading = phase.start + 1
    if after_heading < phase.end and not content_of(plan.lines[after_heading]).strip():
        return after_heading + 1
    return after_heading


def rewrite_tag(plan: Plan, phase: Phase, tag: str) -> str:
    """Plan text with the phase's Tag line added or replaced."""
    lines = list(plan.lines)
    if phase.tag_line is not None:
        lines[phase.tag_line] = f"Tag: {tag}" + ending_of(lines[phase.tag_line])
        return "".join(lines)
    position = tag_insert_position(plan, phase)
    anchor = lines[position - 1]
    ending = ending_of(anchor) or "\n"
    if not ending_of(anchor):
        lines[position - 1] = anchor + ending
    lines.insert(position, f"Tag: {tag}{ending}")
    return "".join(lines)


# ------------------------------------------------------------------- commands


def parse_lane_id(text: str) -> tuple[int, str]:
    """Split '<phase>/<lane>' into its parts."""
    phase, _, lane = text.partition("/")
    if not phase.isdigit() or not lane:
        raise CommandError(f"lane id {text!r} must look like <phase>/<lane>, for example 2/a")
    return int(phase), lane


def lookup_lane(plan: Plan, lane_id: str) -> Lane:
    """Find a lane by full id, or raise CommandError listing the known ids."""
    number, name = parse_lane_id(lane_id)
    phase = plan.find_phase(number)
    lane = next((candidate for candidate in phase.lanes if candidate.name == name), None) if phase else None
    if lane is None:
        known = ", ".join(l.full_id for p in plan.phases for l in p.lanes) or "none"
        raise CommandError(
            f"no lane {lane_id} in the plan (known lanes: {known}). "
            "If the phase's lane table lacks a required column, run validate."
        )
    return lane


def report(problems: list[str]) -> int:
    """Print problems one per line and return exit code 1."""
    for problem in problems:
        print(problem)
    return 1


def cmd_validate(args: argparse.Namespace) -> int:
    problems = validate_plan(read_plan(args.plan))
    if problems:
        return report(problems)
    print("ok")
    return 0


def cmd_ready(args: argparse.Namespace) -> int:
    plan = read_plan(args.plan)
    problems = validate_plan(plan)
    if problems:
        return report(problems)
    for lane in ready_lanes(plan):
        print(lane.full_id)
    return 0


def cmd_check_lane(args: argparse.Namespace) -> int:
    plan = read_plan(args.plan)
    lane = lookup_lane(plan, args.lane)
    if not lane.branch:
        raise CommandError(
            f"lane {lane.full_id} has an empty Branch cell; set it with "
            f"`mark {args.plan} {lane.full_id} {lane.status or 'running'} --branch NAME` first"
        )
    range_spec = f"{args.base}...{lane.branch}"
    paths = changed_paths(args.repo, args.base, lane.branch)
    diff = run_git(args.repo, "diff", "-U0", "--no-renames", "--no-color", "--no-ext-diff",
                   "--src-prefix=a/", "--dst-prefix=b/", range_spec)
    problems = lane_violations(plan, lane, paths, diff)
    if problems:
        return report(problems)
    print("ok")
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    if args.status not in STATUSES:
        raise CommandError(f"status {args.status!r} is not one of {', '.join(STATUSES)}")
    plan = read_plan(args.plan)
    lane = lookup_lane(plan, args.lane)
    cells = {"status": args.status}
    if args.branch is not None:
        cells["branch"] = args.branch
    write_atomically(args.plan, rewrite_lane_cells(plan, lane, cells))
    return 0


def cmd_tag(args: argparse.Namespace) -> int:
    if not args.tag.strip() or "\n" in args.tag:
        raise CommandError(f"tag {args.tag!r} must be a non-empty single line")
    plan = read_plan(args.plan)
    phase = plan.find_phase(args.phase)
    if phase is None:
        known = ", ".join(str(p.number) for p in plan.phases) or "none"
        raise CommandError(f"no phase {args.phase} in the plan (known phases: {known})")
    write_atomically(args.plan, rewrite_tag(plan, phase, args.tag.strip()))
    return 0


# ------------------------------------------------------------------------ cli

DESCRIPTION = (
    "Validate and drive a Markdown plan of phased parallel work. A phase starts at a heading "
    "like '### Phase 2: pricing' and may carry 'Depends on: phase 1', 'Scaffold: <sha>' and "
    "'Tag: <tag>' lines, plus a table with columns Lane, Owns files, Status, Branch (and optionally "
    "Tests, Size, Reads, Model, Done when). Lane ids are written <phase>/<lane>, for example 2/a. "
    "Status is pending, running, merged or cut. Header lines 'Suppressions:' and 'Manifests:' "
    "extend the built-in lists used by check-lane. Exit 0 means success, 1 means problems were "
    "printed on stdout, 2 means a usage, plan-file or git error (message on stderr)."
)


def build_parser() -> argparse.ArgumentParser:
    """The argparse parser with one subcommand per operation."""
    parser = argparse.ArgumentParser(prog="plan_graph.py", description=DESCRIPTION)
    commands = parser.add_subparsers(dest="command", required=True)

    def add(name: str, handler, help_text: str) -> argparse.ArgumentParser:
        sub = commands.add_parser(name, help=help_text, description=help_text)
        sub.add_argument("plan", help="path to the plan Markdown file")
        sub.set_defaults(handler=handler)
        return sub

    add("validate", cmd_validate, "Report every problem in the plan, or print ok.")
    add("ready", cmd_ready, "Print the ids of pending lanes that may start now.")
    check = add("check-lane", cmd_check_lane, "Check a lane's git diff against its ownership and rules.")
    check.add_argument("lane", help="lane id, <phase>/<lane>")
    check.add_argument("base", help="base ref the lane branched from")
    check.add_argument("--repo", default=".", help="git repository directory (default: cwd)")
    mark = add("mark", cmd_mark, "Set a lane's Status (and optionally Branch) cell in place.")
    mark.add_argument("lane", help="lane id, <phase>/<lane>")
    mark.add_argument("status", help="pending, running, merged or cut")
    mark.add_argument("--branch", help="also set the lane's Branch cell")
    tag = add("tag", cmd_tag, "Add or replace a phase's Tag line.")
    tag.add_argument("phase", type=int, help="phase number")
    tag.add_argument("tag", help="tag name")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point; returns the process exit code."""
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except CommandError as error:
        print(error, file=sys.stderr)
        return 2
    except OSError as error:
        print(f"file error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
