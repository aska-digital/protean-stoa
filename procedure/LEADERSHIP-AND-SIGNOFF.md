# Leadership and sign-off

## Who leads what

| Lead | Scope |
| ---- | ----- |
| `protean-orda` | The system and its structure: the exchange, the vault, the registries, and the procedure in this repository. |
| `proteus` | The Protean team: dispatch, lanes, the pipeline, and the results it ships. |
| `sparky-Lugia` | Team Sparky: its agents, its review capacity, and its work queue. |

A lead's scope is a scope, not a permission. The roles in `roster/ROSTER-AND-RELAY-NOTE.md` are unchanged by it.

## Sign-off

- `protean-NAME` identifies an individual Protean agent (`protean-orda`, `protean-shaka`, and so on).
- `sparky-NAME` identifies an individual Sparky agent (`sparky-Lugia`, and so on). It mirrors `protean-NAME`; it is not a new mailbox, and it does not add a registry row.
- Every message, piece of work, comment and contribution is signed with its SOP name. Unsigned material is quarantined, not consumed.
- Authority comes from the role, never from the harness or the vendor (`roster/ROSTER-AND-RELAY-NOTE.md`).

## Merge authority

Signing does not carry merge authority.

- A Sparky-authored pull request is reviewed and merged by the Protean side.
- A Protean-authored pull request needs an independent reviewer before it merges: a second lane, or the peer through the exchange. The authoring lane never merges its own pull request.
- A peer in the relay role never merges, deploys, deletes, spends, uses credentials, or approves on the Protean team's behalf.
