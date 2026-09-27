#!/usr/bin/env python3
"""Extract a friction digest from Claude Code session transcripts.

Reads every *.jsonl transcript under the project's session directory and its
sibling roots (<slug>*: subdirectory sessions, worktrees, subagents) modified
since --since, and writes plain-text digests an agent can read for a
multi-session DX friction review.

Outputs (in --out):
  tool_errors.txt        each tool error with the call that caused it
  user_messages.txt      user prompts; lines starting with * look like corrections
  hook_events.txt        non-success hook events clustered, plus per-hook durations
  precommit_failures.txt pre-commit "....Failed" hook names with session counts
  edit_mismatch.txt      Edit "string not found" / "modified since read" by top-level path
  summary.txt            counts and slash-command usage

Counts come from regex matching, not hand labeling. Spot-check before quoting.
Standard library only.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CORRECTION = re.compile(
    r"\b(no|don't|dont|stop|wrong|why did|again|not what|instead|actually|"
    r"you (didn't|forgot|missed)|still|broke|revert)\b",
    re.I,
)
EDIT_MISMATCH = re.compile(r"String to replace not found|string not found|modified since (it was )?read", re.I)
PRECOMMIT_FAILED = re.compile(r"([A-Za-z0-9 _()\-/.]{3,60}?)\.{3,}(?:\x1b\[\d+m)?Failed")
SLASH_CMD = re.compile(r"<command-name>\s*(/[^<\s]+)\s*</command-name>")
HOOK_SCRIPT = re.compile(r"([\w.-]+\.(?:sh|py|js|mjs|ts))")
QUIET_HOOK_TYPES = {"hook_success", "hook_additional_context"}


def default_project_dir() -> Path:
    slug = os.getcwd().replace("/", "-")
    return Path.home() / ".claude" / "projects" / slug


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--project-dir", type=Path, default=None,
                   help="Session dir, e.g. ~/.claude/projects/<slug>. Siblings named <slug>* are included. "
                        "Default: derived from the cwd.")
    p.add_argument("--since", default=None, help="YYYY-MM-DD, by file mtime (default: 21 days ago)")
    p.add_argument("--out", type=Path, required=True, help="Output directory (created if missing)")
    return p.parse_args()


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for x in content:
            if not isinstance(x, dict):
                continue
            if x.get("type") == "text":
                parts.append(x.get("text", ""))
            elif x.get("type") == "tool_result":
                parts.append(text_of(x.get("content")))
        return " ".join(parts)
    return ""


def one_line(s: str, n: int) -> str:
    return " ".join(s.split())[:n]


def call_summary(inp: dict) -> str:
    for key in ("command", "file_path", "pattern", "path", "url", "prompt"):
        if inp.get(key):
            return str(inp[key])
    return json.dumps(inp)


def top_level_path(file_path: str, roots: list[str]) -> str:
    """Bucket a file path by its first component under the repo root (or worktree root)."""
    fp = file_path
    m = re.search(r"/\.claude/worktrees/[^/]+/(.*)", fp) or re.search(r"/\.worktrees/[^/]+/(.*)", fp)
    if m:
        fp = m.group(1)
    else:
        for r in roots:
            if fp.startswith(r + "/"):
                fp = fp[len(r) + 1:]
                break
    parts = [p for p in fp.split("/") if p]
    if not parts:
        return "?"
    if fp.startswith("/"):
        return "/" + "/".join(parts[:4]) + " (outside repo)"
    return parts[0] + ("/" if len(parts) > 1 else "")


def pct(values: list[int], q: float) -> int:
    v = sorted(values)
    return v[min(len(v) - 1, int(q * len(v)))]


def main():
    args = parse_args()
    project_dir = (args.project_dir or default_project_dir()).expanduser().resolve()
    since = (dt.datetime.strptime(args.since, "%Y-%m-%d") if args.since
             else dt.datetime.now() - dt.timedelta(days=21))
    cutoff = since.timestamp()
    if not project_dir.parent.is_dir():
        sys.exit(f"no such directory: {project_dir.parent}")

    roots = sorted(project_dir.parent.glob(project_dir.name + "*"))
    files = [f for r in roots if r.is_dir() for f in r.rglob("*.jsonl") if f.stat().st_mtime >= cutoff]
    if not files:
        sys.exit(f"no transcripts under {project_dir}* since {since:%Y-%m-%d}")
    # A real repo path for relative-path bucketing: the cwd recorded in transcripts.
    repo_roots: set[str] = set()

    tool_errors, user_msgs = [], []
    err_by_tool = Counter()
    hook_types = Counter()
    hook_clusters, hook_sessions, hook_examples = Counter(), defaultdict(set), {}
    hook_durations = defaultdict(list)
    pc_fail, pc_sessions = Counter(), defaultdict(set)
    edit_rows, edit_buckets = [], Counter()
    slash = Counter()
    sessions = set()
    corrections = 0

    for f in files:
        root_name = next((r.name for r in roots if r in f.parents), f.parent.name)
        label = root_name[len(project_dir.name):].lstrip("-") or "root"
        sid = f.stem[:12]
        session_key = f"{label}/{sid}"
        sessions.add(session_key)
        pending: dict[str, tuple[str, str, dict]] = {}
        try:
            fh = open(f, errors="ignore")
        except OSError as e:
            print(f"skip {f}: {e}", file=sys.stderr)
            continue
        with fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("cwd") and not d.get("isSidechain"):
                    repo_roots.add(d["cwd"])
                msg = d.get("message") or {}
                content = msg.get("content") if isinstance(msg, dict) else None
                kind = d.get("type")

                # Hook attachments
                att = d.get("attachment") or {}
                htype = att.get("type", "")
                if htype.startswith("hook"):
                    hook_types[htype] += 1
                    name = att.get("hookName") or att.get("hookEvent") or "?"
                    cmd = att.get("command") or ""
                    if isinstance(att.get("durationMs"), (int, float)) and cmd:
                        m = HOOK_SCRIPT.search(cmd)
                        hook_durations[f"{att.get('hookEvent', '?')} {m.group(1) if m else cmd[:60]}"].append(
                            int(att["durationMs"]))
                    quiet = htype in QUIET_HOOK_TYPES or (htype == "hook_cancelled" and not att.get("timedOut"))
                    if not quiet:
                        body = " ".join(str(att.get(k) or "") for k in ("stderr", "stdout", "content", "command"))
                        m = re.search(r"(BLOCKED[^\"\n]{0,70}|No such file[^\"\n]{0,40}|[\w.-]+\.sh[^\"\n]{0,50})", body)
                        detail = m.group(1) if m else one_line(body, 100)
                        if htype == "hook_cancelled":
                            m = HOOK_SCRIPT.search(cmd)
                            detail = f"timed out after {att.get('timeoutMs')}ms: {m.group(1) if m else cmd[-60:]}"
                        key = re.sub(r"\d+", "N", f"{htype} | {name} | {one_line(detail, 110)}")
                        hook_clusters[key] += 1
                        hook_sessions[key].add(session_key)
                        hook_examples.setdefault(key, one_line(json.dumps(att), 600))

                if kind == "assistant" and isinstance(content, list):
                    for x in content:
                        if isinstance(x, dict) and x.get("type") == "tool_use":
                            inp = x.get("input") or {}
                            pending[x.get("id")] = (x.get("name", "?"), call_summary(inp), inp)

                if kind != "user":
                    continue

                if isinstance(content, list) and any(
                        isinstance(x, dict) and x.get("type") == "tool_result" for x in content):
                    for x in content:
                        if not (isinstance(x, dict) and x.get("type") == "tool_result"):
                            continue
                        raw = text_of(x.get("content"))
                        for h in PRECOMMIT_FAILED.findall(raw):
                            h = h.strip()
                            pc_fail[h] += 1
                            pc_sessions[h].add(session_key)
                        if not x.get("is_error"):
                            continue
                        name, call, inp = pending.get(x.get("tool_use_id"), ("?", "", {}))
                        err = one_line(raw, 500)
                        err_by_tool[name] += 1
                        tool_errors.append(f"[{session_key}] {name}: {one_line(call, 300)}\n    -> {err}")
                        if name in ("Edit", "MultiEdit") and EDIT_MISMATCH.search(raw):
                            fp = inp.get("file_path", "")
                            edit_rows.append((fp, session_key, err[:160]))
                    continue

                text = text_of(content)
                for c in SLASH_CMD.findall(text):
                    slash[c] += 1
                if d.get("isMeta") or d.get("isSidechain"):
                    continue
                text = text.strip()
                if not text or text.startswith("<") or len(text) >= 2500 or "Caveat:" in text:
                    continue
                flagged = bool(CORRECTION.search(text[:400]))
                corrections += flagged
                user_msgs.append(f"{'*' if flagged else ' '}[{session_key}] {one_line(text, 700)}")

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    roots_for_paths = sorted(repo_roots, key=len, reverse=True)
    for fp, _, _ in edit_rows:
        edit_buckets[top_level_path(fp, roots_for_paths)] += 1

    (out / "tool_errors.txt").write_text("\n".join(tool_errors) + "\n")
    (out / "user_messages.txt").write_text(
        "# Lines starting with * matched a correction regex (no, stop, wrong, again, instead, ...).\n"
        + "\n".join(user_msgs) + "\n")

    lines = ["# Non-success hook events, clustered. Columns: hits, distinct sessions, cluster key", ""]
    for k, v in hook_clusters.most_common():
        lines.append(f"{v:6d} {len(hook_sessions[k]):4d}  {k}")
    lines += ["", "# Example payload per top cluster", ""]
    for k, _ in hook_clusters.most_common(15):
        lines += [k, "    " + hook_examples[k], ""]
    lines += ["# Per-hook duration (ms): runs, p50, p95, max", ""]
    for k, v in sorted(hook_durations.items(), key=lambda kv: -pct(kv[1], 0.95)):
        lines.append(f"{len(v):6d} {pct(v, .5):7d} {pct(v, .95):7d} {max(v):7d}  {k}")
    (out / "hook_events.txt").write_text("\n".join(lines) + "\n")

    lines = ["# Pre-commit hooks reported as Failed. Columns: hits, distinct sessions, hook name", ""]
    lines += [f"{v:6d} {len(pc_sessions[k]):4d}  {k}" for k, v in pc_fail.most_common()]
    (out / "precommit_failures.txt").write_text("\n".join(lines) + "\n")

    lines = ["# Edit string-not-found / modified-since-read errors by top-level path", ""]
    lines += [f"{v:6d}  {k}" for k, v in edit_buckets.most_common()]
    lines += ["", "# Individual errors", ""]
    lines += [f"[{s}] {fp}\n    -> {e}" for fp, s, e in edit_rows]
    (out / "edit_mismatch.txt").write_text("\n".join(lines) + "\n")

    summary = [
        f"project dir: {project_dir}",
        f"session roots: {len([r for r in roots if r.is_dir()])}",
        f"since: {since:%Y-%m-%d}",
        f"transcripts: {len(files)} ({len(sessions)} sessions incl. subagents)",
        f"tool errors: {len(tool_errors)}",
        "  by tool: " + ", ".join(f"{k} {v}" for k, v in err_by_tool.most_common(10)),
        f"user messages: {len(user_msgs)} ({corrections} correction-flagged)",
        "hook events by type: " + ", ".join(f"{k} {v}" for k, v in hook_types.most_common()),
        f"non-success hook clusters: {len(hook_clusters)} ({sum(hook_clusters.values())} events)",
        f"pre-commit Failed lines: {sum(pc_fail.values())} across {len(pc_fail)} hook names",
        f"edit mismatches: {len(edit_rows)}",
        "slash commands: " + (", ".join(f"{k} {v}" for k, v in slash.most_common(20)) or "none"),
        "",
        "Counts are regex matches, not hand labels. Spot-check a sample before quoting them.",
    ]
    (out / "summary.txt").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
