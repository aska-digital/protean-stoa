# Examples

`spec/examples/` carries two packets that pass the validator at `--strict-canonical` and at ingest grade:

- `assign.protean-to-sparky.jsonl`: a task assignment from `protean` to `sparky`. It shows the required packet fields, canonical key order, the `assign` act, and a hash-pinned brief artifact reference.
- `done.sparky-to-protean.jsonl`: a completion report from a Sparky peer to `protean`. It shows the `done` act with its mandatory `st` summary and hash-pinned evidence references.

Read the files themselves for the exact packets. No packet JSON is repeated here.

## Four defects corrected from an earlier draft

An earlier draft of this bridge carried four defects. Both example packets correct them:

1. Uppercase and digit-leading identifiers that break the ID grammar. Identifiers are lowercase `ID := [a-z][a-z0-9_-]{0,31}`.
2. A completion packet with no `st`. `done` needs `st`.
3. A progress packet specification that omitted the mandatory `base` and `ops`. `update` needs `base` and a non-empty `ops`.
4. A duplicate-detection key of bare `id` instead of the pair `(f,id)`. Identity is scoped to the sender.

Validate either file with the command in `spec/SYM-2P-POINTER.md`. Either must exit 0.
