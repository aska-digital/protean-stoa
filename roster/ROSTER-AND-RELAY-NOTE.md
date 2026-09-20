# Roster and relay note

Every external peer in `registry/peers.json` carries `roster_role: "relay"`.

## Allowed

An external peer in the relay role may:

- Accept or decline a delegated task.
- Ask clarifying questions.
- Return results and evidence.
- Escalate to the human.

## Forbidden

An external peer in the relay role must not:

- Merge, deploy, or delete.
- Spend, use credentials, or approve on the Protean team behalf.

A peer authority comes from its role, never from its harness or vendor.

## Intake boundary

The intake boundary of this exchange is the orchestrator of the Protean team (the Director). Outside work enters there. Packets are the only surface; there is no side channel that grants authority.

## The rule that matters most

No secret material ever travels in a packet, in an artifact, or in a handoff bundle. The secret screen in `procedure/PHASE-0-MANUAL-RELAY.md` applies to every packet in Phase 0.
