#!/bin/sh
# Fails when the Claude Code and Codex plugin manifests disagree on name or version.
set -eu
cd "$(dirname "$0")/.."
field() { node -p "require('./$1').$2"; }
claude=plugins/ce/.claude-plugin/plugin.json
codex=plugins/ce/.codex-plugin/plugin.json
status=0
for key in name version; do
  a=$(field "$claude" "$key")
  b=$(field "$codex" "$key")
  if [ "$a" != "$b" ]; then
    echo "$key differs: $claude has $a, $codex has $b" >&2
    status=1
  fi
done
exit "$status"
