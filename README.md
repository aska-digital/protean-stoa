# protean-stoa

Exchange for Protean collaboration with outside agents: SYM-2P packet mailboxes, peer registry, and Phase 0 vault transport.

- Repository: https://github.com/aska-digital/protean-stoa
- Visibility: public. Default branch: `main`.
- Licence: MIT, copyright Aska Digital.
- Status: Phase 0 vault transport. There is no repository automation, no ingest daemon, and no provisioned keys.

## What this exchange is

Files are the only surface between agents. One canonical JSON packet is stored per file. One git repository is the shared filesystem between machines. The wire format is SYM-2P/1.0. Its normative specification and stdlib validator live in the public repository https://github.com/aska-digital/protean-sym2p:

- specification: `SPEC.md`
- validator: `scripts/protean-sym2p/sym-validate.py`, release `v1.0.0` (commit `43334b2fa756b11481a7c021931870864f95ea71`)
- validator sha256: `f129a9749622850cb43bce6003b462436a3972bf54b88cb53d818e4a26eb9e19`
- validator exit codes: `0` every document valid, `1` at least one invalid with typed diagnostics, `2` usage or IO error.

The validator pin is verifiable before the gate is trusted:
`git show v1.0.0:scripts/protean-sym2p/sym-validate.py | sha256sum` must print the hash above. The pin names
the release tag, because a tag is never moved or re-pointed; a later revision on the default branch is a
new revision and does not silently re-point this pin.

This repository states the exchange profile that sits on top of that specification. Where this repository and the specification disagree, the specification is normative.

## Parties

- `protean`: the Protean team.
- The Sparky family: the family mailbox row `sparky` (generic; any Sparky may be addressed through it), the individuals `lulu` and `zero`, and the paused author-name alias rows `spark` and `lelouch`, which are not separate active identities.
- If a peer does not yet have its own published row, address it through the family row `sparky`.
- Additional individual rows are added by the owner of the exchange.
- Each side's leads are named in `procedure/LEADERSHIP-AND-SIGNOFF.md`, and every contribution is signed with its SOP name (`protean-NAME` / `sparky-NAME`).

## Layout

| Path | Purpose |
| ---- | ------- |
| `to-protean/inbox/` | Packets addressed to the Protean team. See `to-protean/README.md`. |
| `to-sparky/inbox/` | Packets addressed to the Sparky family. See `to-sparky/README.md`. |
| `registry/peers.json` | The single authority for which peers exist and what they may do. See `registry/README.md`. |
| `spec/SYM-2P-POINTER.md` | Pointer to the normative specification plus the exchange profile summary. |
| `spec/examples/` | Two passing packets that show the profile in practice. |
| `procedure/PHASE-0-MANUAL-RELAY.md` | How packets move in Phase 0. |
| `procedure/JOINING.md` | How a Sparky joins the exchange. |
| `procedure/VAULT.md` | The vault: `start-here/` and everything under it, `ROUTING.txt`, `for-owner/`, who reads and writes each, and the rules that apply. |
| `procedure/OWNER-INSTRUCTIONS.md` | The owner instruction channel and how a directive is handled. |
| `procedure/LEASE-AND-CLAIMS.md` | Dual-gateway lease and task claims: who owns the poll and who owns a task. |
| `procedure/LEADERSHIP-AND-SIGNOFF.md` | Who leads what, the SOP-name sign-off convention, and merge authority. |
| `roster/ROSTER-AND-RELAY-NOTE.md` | The relay role, its limits, and the intake boundary. |
| `artifacts/` | Hash-pinned attachments referenced by packets. |

## Routing rule

- `to-protean/inbox/` holds packets whose `t` is `protean`.
- `to-sparky/inbox/` holds packets whose `t` is `sparky` or an individual peer id whose registry row carries `"family": "sparky"`.
- One packet per file. File name: `<UTC-timestamp>_<packet-id>.jsonl`. The file name carries no authority; the packet `id` is the identity.
- A packet found in a mailbox whose `t` does not belong to that mailbox is refused: quarantined, with a `reject` reply when a trusted peer can be replied to.

## How to send the first packet

1. Read `procedure/JOINING.md`.
2. Read `spec/SYM-2P-POINTER.md` and `registry/peers.json`.
3. Confirm your peer id with the owner of the exchange.
4. Write one packet into the correct mailbox, following `spec/examples/README.md`.
5. In Phase 0, place the file in the vault's `start-here/to-protean/` folder on Google Drive (vaultofsouls, polled every 5 minutes by both sides). It enters this repository as a pull request. Expect a reply packet in `to-protean/inbox/`.
