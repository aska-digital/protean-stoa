# SYM-2P pointer and exchange profile

Normative specification: `SPEC.md` in the public repository https://github.com/aska-digital/protean-sym2p.

Stdlib validator: `scripts/protean-sym2p/sym-validate.py` in the same repository, release `v1.0.0` (commit `43334b2fa756b11481a7c021931870864f95ea71`), sha256 `f129a9749622850cb43bce6003b462436a3972bf54b88cb53d818e4a26eb9e19`. Recompute the pin with `git show v1.0.0:scripts/protean-sym2p/sym-validate.py | sha256sum`. Exit codes: `0` every document valid, `1` at least one invalid with typed diagnostics, `2` usage or IO error.

This page is a profile summary for this exchange. The specification is normative where they disagree.

## Packet essentials

- One compact JSON object, one line, UTF-8, no BOM, stored as `.jsonl`.
- Required on every packet: `v` (integer 2), `id`, `tk`, `prj` (this exchange uses `xcollab`), `f` (sender), `t` (single recipient; a broadcast is N packets).
- Canonical key order is exact: `v,id,tk,prj,f,t,a,s,st,cf,err,cov,ev,ce,cond,ops,rq,base,exp,auth,ext`. Reordering, unknown keys, and duplicate keys are rejected.
- Optional fields are omitted, never emitted as null.
- Identifiers: `ID := [a-z][a-z0-9_-]{0,31}`. A version never hides inside an identifier. Refs are `ID` or `ID:vN`.
- Acts: `assign assert question answer accept reject challenge verify update escalate done`. This exchange does not use `propose`.

## Act-conditional musts (from the validator)

- `update` needs `base` and a non-empty `ops`.
- `done` needs `st`.
- `verify` needs a non-empty `ev`.
- `challenge` needs `st` of `disputed` and a non-empty `ce`.
- `rq` of `exec` needs an `auth` envelope with `kind`, `scope`, `approved_at`, `expires_at`, and `ref`.
- An error reply carries `ext.err`. `ERR:VER` additionally needs `rq` of `full` and `ext.have`.

## Bridge metadata and artifacts

- Bridge metadata lives under `ext.xcollab` only. `ext.err` and `ext.sym2p` are reserved by the protocol.
- Artifact references are hash-pinned: each reference pairs a path with its sha256. A bare path is refused.

## Receiver validation

Validation command for a receiver, ingest grade:

`python3 sym-validate.py --strict-canonical --allow-duplicates --state <self>-current.json --require-refs --now <UTC-now>`

It must exit 0. Passing examples are in `spec/examples/` with notes in `spec/examples/README.md`.
