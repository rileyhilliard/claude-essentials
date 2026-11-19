"""Behavior tests for plan_graph.py: each test drives the CLI entry point on real files and a real git repo."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_graph  # noqa: E402

EXAMPLE = os.path.join(HERE, "testdata", "example-plan.md")
COLUMNS = "| Lane | Owns files | Tests | Status | Branch |\n| --- | --- | --- | --- | --- |\n"


def run_cli(*argv):
    """Run the CLI in-process; returns (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = plan_graph.main([str(a) for a in argv])
        except SystemExit as exit_:
            code = exit_.code
    return code, out.getvalue(), err.getvalue()


def phase(number, rows, directives="", level="###"):
    """Markdown for one phase with a lane table; rows are (lane, owns, status[, tests, branch])."""
    body = ""
    for row in rows:
        lane, owns, status, *rest = row
        tests, branch = (rest + ["", ""])[:2]
        body += f"| {lane} | {owns} | {tests} | {status} | {branch} |\n"
    return f"{level} Phase {number}: title\n\n{directives}{COLUMNS}{body}\n"


class TempDirTestCase(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.dir = holder.name

    def write_plan(self, text, name="plan.md"):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        return path

    def read(self, path):
        with open(path, encoding="utf-8", newline="") as handle:
            return handle.read()


class ValidateTests(TempDirTestCase):
    def problems(self, text):
        code, out, _ = run_cli("validate", self.write_plan(text))
        self.assertEqual(code, 1, out)
        return out.splitlines()

    def test_example_plan_is_ok(self):
        self.assertEqual(run_cli("validate", EXAMPLE), (0, "ok\n", ""))

    def test_reports_every_problem_not_just_the_first(self):
        text = (
            phase(1, [("a", "src/*.ts", "done"), ("a", "/etc/x", "pending"), ("b", "../x", "pending")])
            + phase(1, [("a", "src/ok.ts", "pending")], directives="Depends on: phase 9\n")
        )
        lines = self.problems(text)
        joined = "\n".join(lines)
        self.assertIn("phase 1 lane a: status 'done' is not one of pending, running, merged, cut", joined)
        self.assertIn("phase 1 lane a: src/*.ts contains a glob character", joined)
        self.assertIn("phase 1 lane a: lane id appears more than once", joined)
        self.assertIn("phase 1 lane b: ../x contains '..'", joined)
        self.assertIn("phase 1: heading appears more than once", joined)
        self.assertIn("phase 1: Depends on phase 9, which does not exist", joined)

    def test_absolute_path_is_reported(self):
        lines = self.problems(phase(1, [("a", "/etc/x", "pending")]))
        self.assertEqual(len(lines), 1)
        self.assertIn("phase 1 lane a: /etc/x is an absolute path", lines[0])

    def test_missing_required_column_is_reported(self):
        text = "### Phase 1: x\n\n| Lane | Status | Branch |\n| --- | --- | --- |\n| a | pending | |\n"
        lines = self.problems(text)
        self.assertEqual(len(lines), 1)
        self.assertIn("phase 1: lane table is missing required column(s) owns files", lines[0])

    def test_columns_match_by_name_in_any_order_and_unknown_columns_are_ignored(self):
        text = (
            "### Phase 1: x\n\n| Branch | Extra | status | OWNS FILES | lane |\n| - | - | - | - | - |\n"
            "| b1 | z | pending | src/a.ts | a |\n"
        )
        self.assertEqual(run_cli("validate", self.write_plan(text)), (0, "ok\n", ""))

    def test_cycle_names_the_phases(self):
        text = (
            phase(1, [], directives="Depends on: phase 3\n")
            + phase(2, [], directives="Depends on: 1\n")
            + phase(3, [], directives="Depends on: phase 2\n")
        )
        self.assertEqual(self.problems(text), ["dependency cycle: phase 1 -> phase 3 -> phase 2 -> phase 1"])

    def test_directory_overlap_in_same_phase_is_reported_with_both_lanes(self):
        lines = self.problems(phase(1, [("a", "src/a/", "pending"), ("b", "src/a/x.ts", "pending")]))
        self.assertEqual(
            lines,
            ["phase 1 lane b: owns src/a/x.ts, also owned by phase 1 lane a (overlaps src/a/)"],
        )

    def test_directory_does_not_cover_a_sibling_sharing_a_name_prefix(self):
        text = phase(1, [("a", "src/a/", "pending"), ("b", "src/ab.ts", "pending")])
        self.assertEqual(run_cli("validate", self.write_plan(text)), (0, "ok\n", ""))

    def test_dot_slash_is_normalized_before_comparing(self):
        lines = self.problems(phase(1, [("a", "./src/x.ts", "pending"), ("b", "`src/x.ts`", "pending")]))
        self.assertEqual(lines, ["phase 1 lane b: owns src/x.ts, also owned by phase 1 lane a"])

    def test_same_file_in_two_phases_that_depend_only_on_phase_one_is_reported(self):
        text = (
            phase(1, [("a", "src/p1.ts", "merged")])
            + phase(2, [("a", "src/x.ts", "pending")], directives="Depends on: phase 1\n")
            + phase(3, [("a", "src/x.ts", "pending")], directives="Depends on: phase 1\n")
        )
        self.assertEqual(
            self.problems(text), ["phase 3 lane a: owns src/x.ts, also owned by phase 2 lane a"]
        )

    def test_same_file_is_fine_when_a_later_phase_transitively_depends_on_the_other(self):
        text = (
            phase(1, [("a", "src/x.ts", "merged")])
            + phase(2, [("a", "src/y.ts", "merged")], directives="Depends on: phase 1\n")
            + phase(3, [("a", "src/x.ts", "pending")], directives="Depends on: phase 2\n")
        )
        self.assertEqual(run_cli("validate", self.write_plan(text)), (0, "ok\n", ""))

    def test_cut_lanes_are_ignored_for_overlap(self):
        text = phase(1, [("a", "src/x.ts", "cut"), ("b", "src/x.ts", "pending")])
        self.assertEqual(run_cli("validate", self.write_plan(text)), (0, "ok\n", ""))

    def test_empty_owns_is_ok_without_scaffold_or_when_cut_but_not_otherwise(self):
        self.assertEqual(run_cli("validate", self.write_plan(phase(1, [("a", "", "pending")]))), (0, "ok\n", ""))
        scaffolded = "Scaffold: abc123\n"
        cut = phase(1, [("a", "", "cut")], directives=scaffolded)
        self.assertEqual(run_cli("validate", self.write_plan(cut)), (0, "ok\n", ""))
        lines = self.problems(phase(1, [("a", "", "pending")], directives=scaffolded))
        self.assertEqual(len(lines), 1)
        self.assertIn("phase 1 lane a: Owns files is empty but the phase has a Scaffold line", lines[0])

    def test_phase_ends_at_a_non_phase_heading_of_same_or_higher_level(self):
        text = phase(1, [("a", "src/x.ts", "pending")]) + "## Log\n\nScaffold: abc\n" + phase(
            2, [("a", "src/x.ts", "pending")], level="##"
        )
        # Phase 1 has no scaffold (the Scaffold line sits under ## Log), so ready would not pick it up.
        self.assertEqual(self.problems(text)[0][:7], "phase 2")

    def test_unreadable_plan_is_exit_2_on_stderr(self):
        code, out, err = run_cli("validate", os.path.join(self.dir, "missing.md"))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("cannot read plan file", err)


class ReadyTests(TempDirTestCase):
    def ready(self, text):
        code, out, _ = run_cli("ready", self.write_plan(text))
        self.assertEqual(code, 0, out)
        return out.splitlines()

    def test_example_has_nothing_ready(self):
        self.assertEqual(run_cli("ready", EXAMPLE), (0, "", ""))

    def test_dependency_gating_requires_tagged_dependencies(self):
        scaffold = "Scaffold: abc\n"
        untagged = phase(1, [("a", "src/a.ts", "merged")], directives=scaffold) + phase(
            2, [("a", "src/b.ts", "pending")], directives=scaffold + "Depends on: phase 1\n"
        )
        self.assertEqual(self.ready(untagged), [])
        tagged = untagged.replace("Scaffold: abc\n", "Scaffold: abc\nTag: t1\n", 1)
        self.assertEqual(self.ready(tagged), ["2/a"])

    def test_phase_without_scaffold_is_not_ready(self):
        self.assertEqual(self.ready(phase(1, [("a", "src/a.ts", "pending")])), [])

    def test_tagged_phase_is_excluded(self):
        text = phase(1, [("a", "src/a.ts", "pending")], directives="Scaffold: abc\nTag: t1\n")
        self.assertEqual(self.ready(text), [])

    def test_only_pending_lanes_are_listed_in_phase_then_table_order(self):
        text = phase(
            1,
            [("b", "src/b.ts", "pending"), ("c", "src/c.ts", "running"), ("a", "src/a.ts", "pending")],
            directives="Scaffold: abc\n",
        )
        self.assertEqual(self.ready(text), ["1/b", "1/a"])

    def test_running_lanes_anywhere_reduce_the_cap(self):
        pending = [(f"p{i}", f"src/p{i}.ts", "pending") for i in range(6)]
        running = [("r1", "src/r1.ts", "running"), ("r2", "src/r2.ts", "running")]
        text = phase(1, pending, directives="Scaffold: abc\n") + phase(2, running)
        self.assertEqual(self.ready(text), ["1/p0", "1/p1"])

    def test_cap_never_goes_negative(self):
        running = [(f"r{i}", f"src/r{i}.ts", "running") for i in range(5)]
        text = phase(1, running) + phase(2, [("a", "src/a.ts", "pending")], directives="Scaffold: abc\n")
        self.assertEqual(self.ready(text), [])

    def test_validation_failure_prints_problems_and_exits_1(self):
        text = phase(1, [("a", "src/x.ts", "pending"), ("b", "src/x.ts", "pending")], directives="Scaffold: abc\n")
        code, out, _ = run_cli("ready", self.write_plan(text))
        self.assertEqual((code, out), (1, "phase 1 lane b: owns src/x.ts, also owned by phase 1 lane a\n"))


class GitTestCase(TempDirTestCase):
    """A real repo with a base commit on `main`; helpers build lane branches off it."""

    BASE_FILES = {
        "src/a/one.ts": "".join(f"line{i}\n" for i in range(1, 11)),
        "src/b.ts": "b\n",
        "src/b.test.ts": "test\n",
        "package.json": "{}\n",
    }

    def setUp(self):
        super().setUp()
        self.repo = os.path.join(self.dir, "repo")
        os.mkdir(self.repo)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "commit.gpgsign", "false")
        for path, content in self.BASE_FILES.items():
            self.put(path, content)
        self.commit("base")
        self.git("checkout", "-q", "-b", "build/x-1a")

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", self.repo, *args], check=True, capture_output=True, text=True
        ).stdout

    def put(self, path, content):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(content)

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def plan(self, branch="build/x-1a", header=""):
        return self.write_plan(
            header
            + "# Build\n\n"
            + phase(
                1,
                [
                    ("a", "src/a/", "running", "src/a.test.ts", branch),
                    ("b", "src/b.ts", "pending", "src/b.test.ts", ""),
                ],
            )
        )

    def check(self, **kwargs):
        plan = kwargs.get("plan") or self.plan()
        return run_cli("check-lane", plan, "1/a", "main", "--repo", self.repo)


class CheckLaneTests(GitTestCase):
    def test_clean_lane_is_ok(self):
        self.put("src/a/one.ts", "changed\n")
        self.put("src/a/new.ts", "new\n")
        self.commit("work")
        self.assertEqual(self.check(), (0, "ok\n", ""))

    def test_edit_outside_ownership_is_reported(self):
        self.put("src/b.ts", "edited\n")
        self.commit("work")
        code, out, _ = self.check()
        self.assertEqual(
            (code, out), (1, "phase 1 lane a: changed src/b.ts, which is not in its Owns files\n")
        )

    def test_edit_to_another_lanes_test_file_is_reported(self):
        self.put("src/b.test.ts", "weakened\n")
        self.commit("work")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(out, "phase 1 lane a: changed src/b.test.ts, which is not in its Owns files\n")

    def test_rename_out_of_owned_directory_is_reported(self):
        self.git("mv", "src/a/one.ts", "src/moved.ts")
        self.commit("work")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(out, "phase 1 lane a: changed src/moved.ts, which is not in its Owns files\n")

    def test_lockfile_change_is_reported_even_when_owned(self):
        plan = self.write_plan(
            "# Build\n\n" + phase(1, [("a", "src/a/, package.json", "running", "", "build/x-1a")])
        )
        self.put("package.json", '{"x": 1}\n')
        self.commit("work")
        code, out, _ = self.check(plan=plan)
        self.assertEqual(code, 1)
        self.assertIn("changed package.json, a dependency manifest or lockfile", out)
        self.assertNotIn("not in its Owns files", out)

    def test_requirements_variant_counts_as_manifest(self):
        plan = self.write_plan(
            "# Build\n\n" + phase(1, [("a", "requirements-dev.txt", "running", "", "build/x-1a")])
        )
        self.put("requirements-dev.txt", "x\n")
        self.commit("work")
        self.assertIn("a dependency manifest", self.check(plan=plan)[1])

    def test_header_manifests_are_honored(self):
        plan = self.write_plan(
            "# Build\nManifests: `deno.json`\n\n"
            + phase(1, [("a", "deno.json", "running", "", "build/x-1a")])
        )
        self.put("deno.json", "{}\n")
        self.commit("work")
        self.assertIn("changed deno.json, a dependency manifest", self.check(plan=plan)[1])

    def test_added_only_call_is_reported_with_new_file_line_number(self):
        self.put("src/a/one.ts", "one\ntwo\nit.only('x', () => {})\nfour\n")
        self.commit("work")
        code, out, _ = self.check()
        self.assertEqual((code, out), (1, 'src/a/one.ts:3: added ".only("\n'))

    def test_line_numbers_follow_separate_hunks(self):
        lines = [f"line{i}\n" for i in range(1, 11)]
        self.put("src/a/one.ts", "".join(lines[:3] + ["x # noqa\n"] + lines[3:] + ["foo.skip(1)\n"]))
        self.commit("work")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(
            out.splitlines(), ['src/a/one.ts:4: added "# noqa"', 'src/a/one.ts:12: added ".skip("']
        )

    def test_header_suppressions_are_honored(self):
        plan = self.plan(header="Suppressions: `@SuppressWarnings`, `# nosec`\n")
        self.put("src/a/one.ts", "@SuppressWarnings(x)\n")
        self.commit("work")
        code, out, _ = self.check(plan=plan)
        self.assertEqual((code, out), (1, 'src/a/one.ts:1: added "@SuppressWarnings"\n'))

    def test_removed_skip_line_is_not_reported(self):
        self.git("checkout", "-q", "main")
        self.put("src/a/one.ts", "keep\ndescribe.skip('x')\n")
        self.commit("main has a skip")
        self.git("checkout", "-q", "-B", "build/x-1a")
        self.put("src/a/one.ts", "keep\n")
        self.commit("remove it")
        self.assertEqual(self.check(), (0, "ok\n", ""))

    def test_empty_branch_cell_is_exit_2(self):
        code, out, err = run_cli("check-lane", self.plan(), "1/b", "main", "--repo", self.repo)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("lane 1/b has an empty Branch cell", err)

    def test_unknown_branch_is_a_git_failure_exit_2(self):
        code, out, err = run_cli(
            "check-lane", self.plan(branch="build/missing"), "1/a", "main", "--repo", self.repo
        )
        self.assertEqual((code, out), (2, ""))
        self.assertIn("git diff", err)

    def test_unknown_lane_is_exit_2(self):
        code, _, err = run_cli("check-lane", self.plan(), "1/zz", "main", "--repo", self.repo)
        self.assertEqual(code, 2)
        self.assertIn("no lane 1/zz", err)


class MarkTests(TempDirTestCase):
    PLAN = (
        "# Build\n\nSome prose.\n\n### Phase 1: x\n\n"
        "| Lane | Owns files | Status |   Branch   | Done when |\n"
        "| ---- | ---------- | ------ | ---------- | --------- |\n"
        "| a    | src/a.ts   | pending| build/x-1a | tests     |\n"
        "| b    | src/b.ts   | pending|            | tests     |\n"
        "\n## Log\n\ntrailing"
    )

    def test_mark_rewrites_only_the_status_cell(self):
        path = self.write_plan(self.PLAN)
        self.assertEqual(run_cli("mark", path, "1/a", "running"), (0, "", ""))
        self.assertEqual(self.read(path), self.PLAN.replace("pending| build/x-1a", "running| build/x-1a"))

    def test_mark_with_branch_fills_an_empty_branch_cell(self):
        path = self.write_plan(self.PLAN)
        run_cli("mark", path, "1/b", "running", "--branch", "build/x-1b")
        self.assertEqual(
            self.read(path), self.PLAN.replace("pending|            | tests", "running| build/x-1b | tests")
        )

    def test_mark_with_branch_replaces_an_existing_branch(self):
        path = self.write_plan(self.PLAN)
        run_cli("mark", path, "1/a", "merged", "--branch", "new")
        self.assertEqual(self.read(path), self.PLAN.replace("pending| build/x-1a |", "merged| new |"))

    def test_mark_preserves_crlf_line_endings(self):
        crlf = self.PLAN.replace("\n", "\r\n")
        path = self.write_plan(crlf)
        run_cli("mark", path, "1/a", "cut")
        self.assertEqual(self.read(path), crlf.replace("pending| build/x-1a", "cut| build/x-1a"))

    def test_mark_unknown_lane_and_bad_status_are_exit_2_and_leave_file_alone(self):
        path = self.write_plan(self.PLAN)
        code, _, err = run_cli("mark", path, "1/zz", "running")
        self.assertEqual(code, 2)
        self.assertIn("no lane 1/zz", err)
        code, _, err = run_cli("mark", path, "1/a", "done")
        self.assertEqual(code, 2)
        self.assertIn("is not one of pending, running, merged, cut", err)
        self.assertEqual(self.read(path), self.PLAN)

    def test_mark_leaves_no_temp_files_behind(self):
        path = self.write_plan(self.PLAN)
        run_cli("mark", path, "1/a", "running")
        self.assertEqual(os.listdir(self.dir), ["plan.md"])


class TagTests(TempDirTestCase):
    def test_tag_goes_right_after_scaffold(self):
        text = "# B\n\n### Phase 1: x\n\nDemo: y\nScaffold: abc\n\nprose\n\n### Phase 2: z\n\nScaffold: def\n"
        path = self.write_plan(text)
        self.assertEqual(run_cli("tag", path, "1", "phase-1"), (0, "", ""))
        self.assertEqual(
            self.read(path),
            "# B\n\n### Phase 1: x\n\nDemo: y\nScaffold: abc\nTag: phase-1\n\nprose\n\n### Phase 2: z\n\nScaffold: def\n",
        )

    def test_tag_without_scaffold_goes_after_the_blank_line_following_the_heading(self):
        text = "### Phase 1: x\n\nDepends on: none\n| Lane |\n"
        path = self.write_plan(text)
        run_cli("tag", path, "1", "t")
        self.assertEqual(self.read(path), "### Phase 1: x\n\nTag: t\nDepends on: none\n| Lane |\n")

    def test_tag_replaces_an_existing_tag_line(self):
        text = "### Phase 1: x\n\nScaffold: abc\nTag: old\nmore\n"
        path = self.write_plan(text)
        run_cli("tag", path, "1", "new")
        self.assertEqual(self.read(path), "### Phase 1: x\n\nScaffold: abc\nTag: new\nmore\n")

    def test_tag_on_last_unterminated_line_and_crlf(self):
        path = self.write_plan("### Phase 1: x\r\nScaffold: abc")
        run_cli("tag", path, "1", "t")
        self.assertEqual(self.read(path), "### Phase 1: x\r\nScaffold: abc\nTag: t\n")

    def test_tag_unknown_phase_is_exit_2(self):
        path = self.write_plan("### Phase 1: x\n")
        code, _, err = run_cli("tag", path, "7", "t")
        self.assertEqual(code, 2)
        self.assertIn("no phase 7", err)

    def test_tagged_phase_then_unlocks_dependents_in_ready(self):
        text = phase(1, [("a", "src/a.ts", "merged")], directives="Scaffold: abc\n") + phase(
            2, [("a", "src/b.ts", "pending")], directives="Scaffold: def\nDepends on: 1\n"
        )
        path = self.write_plan(text)
        self.assertEqual(run_cli("ready", path)[1], "")
        run_cli("tag", path, "1", "phase-1")
        self.assertEqual(run_cli("ready", path), (0, "2/a\n", ""))


class HelpTests(unittest.TestCase):
    def test_help_describes_the_plan_format(self):
        code, out, _ = run_cli("-h")
        self.assertEqual(code, 0)
        self.assertIn("Suppressions", out)
        self.assertIn("check-lane", out)


if __name__ == "__main__":
    unittest.main()
