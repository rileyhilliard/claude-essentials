---
name: reading-logs
description: Efficient log analysis using targeted search, filtering, and iterative refinement. Use when investigating errors, analyzing patterns, or debugging incidents through application logs.
---

# Reading Logs

Efficient log analysis through targeted search and progressive narrowing. The goal is to find the needle in the haystack without loading the entire haystack into memory.

**IRON LAW**: Filter first, then read.
Never open a large log file without narrowing it down first.

## When to Use

- Investigating specific errors or incidents
- Finding recurring patterns in application logs
- Debugging issues where logs are a primary evidence source
- Analyzing what happened during a particular time window
- Tracing request flows through correlation IDs

## Core Principles

1. **Filter first, then read**: Always search or filter logs before reading them. Never start by loading a whole multi-MB/GB file into context.

2. **Iterative narrowing**: Start broad (severity, keyword), then progressively refine with additional patterns, exclusions, and time ranges.

3. **Small context windows**: When you find interesting lines, fetch a small window of surrounding context (before/after) instead of entire files.

4. **Format-agnostic patterns**: Assume logs are generic text. Don't rely on specific frameworks or structures. Infer patterns from actual data.

5. **Summaries over raw dumps**: Present concise explanations, example snippets, and command patterns rather than long raw log output.

## Tool Strategy

### 1. Discovering Log Files (Glob)

Use `Glob` to locate likely log files before diving in:

```bash
# Common patterns
**/*.log
**/logs/**
**/*.log.*          # Rotated logs
**/var/log/**
```

Prefer smaller, rotated, or time-scoped files (e.g., `app.log.1`, `app-2025-12-04.log`) before touching giant archives.

### 2. Grep as Primary Lens

Use `Grep` as your main tool. Filter and locate relevant lines before using `Read`.

**Basic severity search:**

```bash
grep -i "error" path/to/log
grep -Ei "error|warn" path/to/log
```

**Exclude noisy patterns:**

```bash
grep -Ei "error|exception" path/to/log | grep -v "known-benign-pattern"
```

**Show context around matches:**

```bash
grep -C 5 "ERROR" path/to/log    # 5 lines before and after
grep -B 3 -A 10 "Exception" log  # 3 before, 10 after (for stack traces)
```

**Time-window filtering:**

```bash
grep "2025-12-04T11:0" app.log | grep "ERROR"
grep "Dec  4 11:" /var/log/syslog | grep -i "fail"
```

**Count occurrences:**

```bash
grep -c "connection refused" app.log
grep -i "ERROR" app.log | wc -l
```

### 3. Bash for Streaming and Chaining

Use `Bash` to combine tools while keeping data volume small:

**Recent activity only:**

```bash
tail -n 2000 app.log | grep -Ei "error|exception"
```

**Top recurring messages:**

```bash
grep -i "ERROR" app.log | sort | uniq -c | sort -nr | head -20
```

**Extract specific fields and count:**

```bash
grep "ERROR" app.log | awk '{print $5}' | sort | uniq -c | sort -nr
```

**Find unique error types:**

```bash
grep -oE 'Error: [^,]+' app.log | sort -u
```

### 4. Read Only What You Must

Use `Read` only after narrowing with `Grep` or `Bash`, and only on small sections.

When a `Grep` finds relevant lines, rerun with context flags (`-C`, `-A`, `-B`) or use `tail` to grab a targeted chunk, then `Read` the result.

Never `Read` an entire very large log file unless the user explicitly insists and the size is clearly manageable.

## Investigation Workflows

### A. Single-Incident Root Cause

Use when investigating a specific failure, error message, or timestamp.

**Steps:**

1. **Clarify the incident**: Get approximate time window, error text, request IDs, user IDs, or correlation IDs.

2. **Locate candidate files**: Use `Glob` to find logs covering that time or service.

3. **Time-window grep**: Filter by timestamp prefix combined with severity/keywords.

   ```bash
   grep "2025-12-04T11:" service.log | grep -i "timeout"
   ```

4. **ID-based tracing**: If there's a correlation/request ID, grep for it across all relevant logs.

   ```bash
   grep "req-abc123" *.log
   ```

5. **Expand context**: For relevant hits, use `grep -C N` (3-10 lines) to see surrounding events.

6. **Summarize**: Explain likely root cause, sequence of events, and supporting evidence.

### B. Recurring Errors and Patterns

Use when investigating "what's going wrong most often" or "what's noisy in the logs."

**Steps:**

1. **Filter by severity**: Search for ERROR, WARN, or similar keywords.

   ```bash
   grep -Ei "error|warn|fatal|critical" app.log
   ```

2. **Group and count**:

   ```bash
   grep -i "ERROR" app.log | sort | uniq -c | sort -nr | head
   ```

3. **Exclude noise**: Add `grep -v` filters for known benign patterns.

4. **Drill into top patterns**: For each high-frequency pattern, run focused grep with context.

5. **Report patterns**: List most frequent issues with counts and representative examples.

### C. Recent Activity

Use when debugging a fresh incident or "what just happened."

**Steps:**

1. **Tail recent lines**:

   ```bash
   tail -n 500 app.log
   tail -n 5000 app.log | grep -i "ERROR"
   ```

2. **Inline filter**: Pipe to grep with relevant keywords.

3. **Zoom in**: If interesting lines appear, grep for those exact messages or IDs across the full log set.

## Log Heuristics

Apply these format-agnostic patterns when working with unfamiliar logs:

**Timestamps**: Lines starting with date-like patterns are time anchors. Use them for range filtering.

- ISO: `2025-12-04T11:23:45`
- Syslog: `Dec  4 11:23:45`
- Epoch: `1733311425`

**Severity tokens**: Look for these common patterns (case-insensitive):

- `DEBUG`, `INFO`, `INF`, `WARN`, `WARNING`, `ERROR`, `ERR`, `FATAL`, `CRITICAL`

**IDs and tokens**: Repeated alphanumeric tokens are likely correlation or request IDs. Use them to join events across files.

- `req-123`, `trace-abc`, GUIDs, hex strings

**Stack traces**: Lines starting with whitespace or containing `at ...`, `Traceback`, `File "..."` belong to stack traces. Group them when summarizing.

## Utility Scripts

For complex operations, use the scripts in `@scripts/`:

**Parse JSON logs** (when logs are structured JSON):

```bash
bash scripts/parse-json-logs.sh app.log '.level == "error"'
```

**Extract and count stack traces**:

```bash
bash scripts/extract-stack-traces.sh app.log
```

**Aggregate errors by frequency**:

```bash
bash scripts/aggregate-errors.sh app.log "ERROR" 20
```

## Red Flags

Stop and reconsider if you're doing any of these:

- [ ] Opening a large file (>10MB) without filtering first
- [ ] Using `Read` before `Grep` on an unfamiliar log
- [ ] Dumping raw log output without summarizing
- [ ] Searching without time bounds on multi-day logs
- [ ] Loading entire log into context "just to see"

## Output Expectations

When reporting findings:

1. **State what you searched for**, which files, and which commands/patterns used
2. **Provide short snippets** that illustrate the issue, not long dumps
3. **Explain what likely happened**, why, and which evidence supports it
4. **Suggest next steps**: additional logging, monitoring, or areas to investigate

If logs are too noisy or incomplete, say so explicitly and suggest what additional logging would help.

## Integration

**Complementary skills:**

- `systematic-debugging` - Use reading-logs during evidence gathering phases
- `handling-errors` - Understand error logging patterns when investigating issues
