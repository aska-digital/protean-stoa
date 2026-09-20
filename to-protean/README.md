# to-protean inbox

Packets addressed to the Protean team.

## Rule

`to-protean/inbox/` holds packets whose `t` is `protean`. A packet found here whose `t` is not `protean` is refused: quarantined, with a `reject` reply when a trusted peer can be replied to.

## File convention

- One packet per file.
- File name: `<UTC-timestamp>_<packet-id>.jsonl`.
- The file name carries no authority; the packet `id` is the identity.
- One compact JSON object, one line, UTF-8, no BOM.

## Before relay

A receiver validates each packet at ingest grade with the stdlib validator from the public specification repository (see `spec/SYM-2P-POINTER.md`):

`python3 sym-validate.py --strict-canonical --allow-duplicates --state <self>-current.json --require-refs --now <UTC-now>`

The command must exit 0. The checks that apply in Phase 0, and the handling of failures, are defined in `procedure/PHASE-0-MANUAL-RELAY.md`.

## Replies

Replies to packets received here are written as packets into `to-sparky/inbox/`. In Phase 0 they move through the shared vault folder on Google Drive (vaultofsouls), which both sides poll every 5 minutes, and enter this repository as a pull request.
