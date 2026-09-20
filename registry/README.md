# Registry

`registry/peers.json` is the single authority for which peers exist and what they may do. Schema: `xcollab-peers/1`.

## Rows shipped

- `protean`: the Protean team.
- `sparky`: the Sparky family mailbox row (generic). Use this address when a peer does not yet have its own published row.
- `lulu` and `zero`: active individual peers of the Sparky family.
- `spark` and `lelouch`: paused author-name alias rows. They are not separate active identities.

Additional individual rows are added by the owner of the exchange.

## Peer id grammar

Peer ids are wire values: lowercase, matching `[a-z][a-z0-9_-]{0,31}`, at most 14 characters.

## Roles

Every external peer carries `roster_role: "relay"`. The relay role is defined in `roster/ROSTER-AND-RELAY-NOTE.md`. A peer must never invent a peer id that is not in the registry.

## Keys

The registry ships with placeholder key fingerprints of the form `SHA256:PENDING-PROVISIONING-...` because no keys are provisioned yet. Real SSH signing-key fingerprints are added by the owner before signed-commit enforcement is switched on.

## Reading the registry

Before sending a packet, read `registry/peers.json` and confirm:

1. Your sender id `f` has a row.
2. Your recipient `t` has a row.
3. The recipient belongs to the mailbox you are writing into (see the repository `README.md` routing rule).

## Known drift (owner-reserved — do not edit from a lane)

The `sparky`, `lulu`, `zero`, `spark` and `lelouch` rows still carry `"mode": "manual"`, `"sla": {"poll_minutes": 30, ...}` and `"phase": 0`. The live arrangement on the Sparky side is a 5-minute poll.

Registry rows are added and amended by the owner of the exchange, so this drift is flagged to the owner and deliberately not corrected here. Until the owner amends the rows, read `sla.poll_minutes` as the value shipped with the registry, not as a statement about the live poll interval.

