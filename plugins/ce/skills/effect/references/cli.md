# effect/cli

Read when adding or changing commands, arguments or flags, handling parser errors, or wiring a CLI entry point. The module is `effect/cli` (marked unstable). Example: `ai-docs/src/70_cli/10_basics.ts`.

`Command.make(name, config, handler)` builds a command; `Command.withSubcommands([...])` composes the tree and `Command.withSharedFlags` adds flags accepted before or after subcommands. Flag and argument constructors are capitalized (`Flag.String`, `Flag.Boolean`, `Flag.Int`, `Flag.Literals` for a fixed set of choices where Effect 3 had `Options.choice`, `Argument.String`). `Flag.Boolean("x")` is optional only with `Flag.withDefault(false)`.

Read parsed values from the handler's config, including shared flags (a parent command's config is yielded from the parent command itself). When parsing fails, the structured `CliError` variants carry what went wrong (`InvalidValue`, `MissingOption`, `MissingArgument`, `UnrecognizedOption`, `UnknownSubcommand`, `ShowHelp`, `DuplicateOption`); read their fields instead of re-parsing `process.argv` to recover the flag or value.

`Command.run`/`runWith` take the raw arguments and options such as `{ version }`; check the installed declaration for the error-rendering options before assuming the framework prints errors. Help and version output go through `Console`, so a program that owns its own output can capture or redirect them by providing a `Console`.

Run the program at the process entry point: the platform runner (`NodeRuntime.runMain`) handles signals and exit codes, unless the application has its own exit-code and signal policy, in which case that boundary stays.
