#!/usr/bin/env bash
# SessionStart hook for injecting skills awareness
# Skills are loaded on-demand via the Skill tool (progressive disclosure pattern)
# Note: ~/.claude/CLAUDE.md is automatically loaded by Claude Code - no need to handle it here

set -euo pipefail

# Extract name and truncated description from SKILL.md YAML frontmatter
parse_skill() {
    local skill_file="$1"
    local in_frontmatter=false
    local name=""
    local desc=""

    while IFS= read -r line; do
        if [[ "$line" == "---" ]]; then
            if $in_frontmatter; then
                break  # End of frontmatter
            fi
            in_frontmatter=true
            continue
        fi
        if $in_frontmatter; then
            if [[ "$line" =~ ^name:\ *(.+)$ ]]; then
                name="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^description:\ *(.+)$ ]]; then
                desc="${BASH_REMATCH[1]}"
            fi
        fi
    done < "$skill_file"

    if [[ -n "$name" && -n "$desc" ]]; then
        # Truncate description to ~100 chars at word boundary
        if [[ ${#desc} -gt 100 ]]; then
            desc="${desc:0:100}"
            desc="${desc% *}..."  # Cut at last space, add ellipsis
        fi
        echo "- ce:${name} - ${desc}"
    fi
}

# Build dynamic skills list from SKILL.md files
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SKILLS_DIR="${PLUGIN_ROOT}/skills"
SKILLS_LIST=""

if [ -d "$SKILLS_DIR" ]; then
    for skill_dir in "$SKILLS_DIR"/*/; do
        skill_file="${skill_dir}SKILL.md"
        if [ -f "$skill_file" ]; then
            skill_line=$(parse_skill "$skill_file")
            if [ -n "$skill_line" ]; then
                SKILLS_LIST="${SKILLS_LIST}${skill_line}\n"
            fi
        fi
    done
fi

# Output context injection as JSON if skills were found
if [ -n "$SKILLS_LIST" ]; then
    additional_context="## Available Skills\n\nConsider using these skills when they match your task (invoke via Skill tool):\n\n${SKILLS_LIST}"
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${additional_context}"
  }
}
EOF
fi

exit 0
