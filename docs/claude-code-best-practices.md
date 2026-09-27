# Claude Code Plugin Best Practices (September 2026)

Research notes behind the 5.0.0 overhaul of the `ce` plugin. Everything here comes from Anthropic's published docs as of 2026-09-27. Re-check the linked pages before relying on a detail; the schemas move.

## Skills

Source: https://code.claude.com/docs/en/skills

- Custom commands have been merged into skills. `commands/deploy.md` and `skills/deploy/SKILL.md` both create `/deploy`, and by default both the user and the model can invoke a skill. Command files still work, but the plugin reference says to prefer `skills/` for new plugins.
- Every frontmatter field is optional in Claude Code. `name` defaults to the directory name; `description` is recommended because it is the only thing the model sees when deciding whether to load the skill.
- Supported fields: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`.
- `description` plus `when_to_use` are truncated at 1,536 characters in the skill listing.
- Invalid YAML makes the skill load with no fields and no error, so a broken frontmatter block fails silently.
- After compaction, the first 5k tokens of each loaded skill are re-attached, within a 25k combined budget. Use `${CLAUDE_SKILL_DIR}` for paths to bundled files.
- `synced` and the `anthropic-skills` namespace are reserved for skills synced from a claude.ai account.

The cross-product Agent Skills spec is stricter, and following it keeps skills portable to the API and claude.ai. Sources: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview and https://agentskills.io/specification

- `name` is required: at most 64 characters, lowercase letters, digits and hyphens. It can't start or end with a hyphen or contain `--`, can't use the words "anthropic" or "claude", and must match the directory.
- `description` is required: at most 1,024 characters, with no XML tags.

## Authoring

Source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

- Keep the SKILL.md body under 500 lines (roughly 5k tokens). Move detail into reference files that the body links to.
- Keep references one level deep. When a reference links to another reference, the second one often gets only a partial read.
- Give reference files over 100 lines a table of contents at the top.
- Scripts are executed, not loaded, so only their output costs context. Say whether Claude should run a script or read it.
- Write descriptions in the third person, covering what the skill does and when to use it, with the terms a user would actually type. Claude picks among 100+ skills on this field alone.
- Prefer gerund names (`writing-tests`) and avoid `helper` or `utils`.
- Only add what Claude doesn't already know. Restating general knowledge costs tokens on every load and adds nothing.

## Plugins and marketplaces

Sources: https://code.claude.com/docs/en/plugins-reference, https://code.claude.com/docs/en/plugins/marketplace-reference, https://code.claude.com/docs/en/plugins/host-marketplace

plugin.json:

- `name` is the only required key.
- Optional keys: `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, and a few others. Unknown keys are stripped with a warning.
- Components are auto-discovered from `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json` and `output-styles/`.
- A `skills` path array adds to the default scan. A `commands` or `agents` array replaces the default directory for that component.

marketplace.json:

- Required: `name`, `owner` (with `owner.name`) and `plugins`.
- Each plugin entry needs `name` and `source`, and can carry any plugin.json field plus `category`, `tags` and `strict`.
- `strict` defaults to true: plugin.json is the authority, and component fields in the entry are appended to it.

Versioning:

- Resolution order is plugin.json, then the marketplace entry, then the git SHA.
- Don't set `version` in both places; `validate` warns when you do.
- Bump the version on every release. A version that never changes means installed copies never update.

Validation (https://code.claude.com/docs/en/plugins/cli-reference):

- Run `claude plugin validate <path> [--strict]`. Pointed at a marketplace, it does not open each plugin's skill, agent and hook files, so validate the plugin directory separately too.

## Subagents

Source: https://code.claude.com/docs/en/sub-agents

- Frontmatter fields: `name` and `description` (required), then `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`.
- `model` accepts `sonnet`, `opus`, `haiku`, `fable`, a full model ID, or `inherit`.
- `skills` preloads each listed skill's full content into the agent on every run, so keep that list short.
- Plugin agents ignore `hooks`, `mcpServers`, `permissionMode` and `initialPrompt`.
- `tools` is a comma-separated string.
- Delegation depends on the description. A long `<example>` block isn't required.

## Hooks

Source: https://code.claude.com/docs/en/hooks

- Shape: `{"hooks": {"<Event>": [{"matcher": "...", "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/..."}]}]}}`.
- `${CLAUDE_PLUGIN_ROOT}` is the versioned cache directory. Durable state belongs in `${CLAUDE_PLUGIN_DATA}`.
- A plugin with no hooks doesn't need a `hooks/` directory, since the file is auto-discovered only when present.

## Prompting current models

Sources: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5, https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5, https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

- Aggressive language now over-triggers. Replace "CRITICAL: You MUST use this tool when..." with "Use this tool when...". Lines like "if in doubt, use X" have the same problem.
- Explain why an instruction exists instead of issuing a bare rule. The model generalizes from the reason.
- Skills written for earlier models are often too prescriptive for current ones and can lower output quality. A short instruction steers better than an exhaustive list of cases.
- Opus 5 guidance:
  - Remove explicit "verify" and "double-check" steps, because they cause over-verification.
  - The model delegates readily, so say when delegation is appropriate rather than nudging it toward subagents.
  - It takes reporting thresholds such as "only report high-severity issues" literally, so a review prompt that wants coverage has to ask for it.
- Opus 5.5 guidance:
  - Effort defaults to `medium`. Lower effort, rather than adding prompt text, to get less thinking.
  - For frontend work, name the specific patterns to avoid. "Avoid a generic look" just swaps one default style for another.
- Examples help when they are relevant and varied. Positive examples work better than "don't" lists.
