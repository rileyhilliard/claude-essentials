# Schema

Read when defining schemas, decoding or encoding data, modeling optional fields, transforming representations, or generating JSON Schema. Schema is part of `effect`; there is no `@effect/schema` in Effect 4. Basics: `ai-docs/src/01_effect/02_schema/10_schema-basics.ts`.

## Types and names

A schema and its type share a name: `const User = Schema.Struct({...}); type User = typeof User.Type`. `.Type` is the decoded value and `.Encoded` the wire shape; they differ as soon as a field transforms (a date from a string, a number from a string). Write both sides when a value crosses a boundary, and derive types from schemas rather than keeping parallel interfaces.

Use `Schema.Struct` for plain data and `Schema.Class` or `TaggedClass` when methods or class identity help. Brand ids with `.pipe(Schema.brand("UserId"))` when mixing two kinds of id would be a real bug.

## Optional fields

| Constructor | Key absent | Key present as `undefined` |
| --- | --- | --- |
| `Schema.optionalKey(S)` | accepted | rejected |
| `Schema.optional(S)` | accepted | accepted |

Under `exactOptionalPropertyTypes`, build objects so an absent value omits the key (`...(x === undefined ? {} : { x })`) instead of setting it to `undefined`. Defaults on decode or construction come from `Schema.withDecodingDefault` and `withConstructorDefault`.

## Checks and transformations

Refinements are checks: `.check(Schema.isInt(), Schema.isMinLength(1))` or a custom `.check(Schema.makeFilter((value) => ...))`. A union is `Schema.Union([a, b])`; literals are `Schema.Literals(["a", "b"])`.

A representation change is `From.pipe(Schema.decodeTo(To, { decode: SchemaGetter.transform(f), encode: SchemaGetter.transform(g) }))`. JSON text is `Schema.fromJsonString(S)`.

## Decoding and encoding

Pick the decoder by where you are:

| Where | Use | Failure |
| --- | --- | --- |
| Effect code | `Schema.decodeUnknownEffect(S)(input)` | typed `SchemaError` |
| Pure code | `decodeUnknownResult`, `decodeUnknownExit`, `decodeUnknownOption` | a value |
| Trusted construction (module constants, values the program built itself) | `decodeUnknownSync`, `encodeSync` | a throw, which inside Effect code is a defect |

Encode output through the schema (`encodeEffect`, `encodeSync`) so the wire form is the declared one.

Decoding ignores unknown keys by default. Pass `{ onExcessProperty: "error" }` to the decoder (or set it where the framework allows, such as HttpApi parse options) when extra keys must fail.

## JSON Schema and annotations

`Schema.toJsonSchemaDocument(S, options)` returns `{ schema, definitions }`. Objects are open (`additionalProperties: true`) unless you pass `onExcessProperty: "error"`. Closing the generated document does not change runtime decoding, and the reverse; configure and test each consumer separately.

An `identifier` annotation turns a node into a `$ref` into the definitions. Some consumers (LLM tool schemas, simple validators) don't resolve refs; leave identifiers off schemas they read. `.annotate` describes a node; `.annotateKey` describes a struct field's key (its description and docs in the parent object). Framework metadata such as HttpApi status codes lives in annotations too, so after adding checks or transformations, confirm the consumer still sees it on the final node.

`Schema.toStandardSchemaV1(S)` adapts a schema for libraries that accept Standard Schema.

## Property tests

`@effect/vitest`'s `it.prop` and `it.effect.prop` accept schemas as generators. Spend them on invariants such as encode-then-decode round trips of transformed schemas, not on restating field declarations.
