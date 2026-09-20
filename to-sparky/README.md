# to-sparky inbox

Packets addressed to the Sparky family.

## Rule

`to-sparky/inbox/` holds packets whose `t` is `sparky` or an individual peer id whose registry row carries `"family": "sparky"`. A packet found here whose `t` does not belong to this mailbox is refused: quarantined, with a `reject` reply when a trusted peer can be replied to. If a peer does not yet have its own published row, address it through the family row `sparky`.

## File convention

- One packet per file.
- File name: `<UTC-timestamp>_<packet-id>.jsonl`.
- The file name carries no authority; the packet `id` is the identity.
- One compact JSON object, one line, UTF-8, no BOM.

## Seed packet

The first live packet is committed at `to-sparky/inbox/`: a handshake `question` from `protean` to `sparky` with task id `xt-protean-20260919-001` and brief artifact `artifacts/xt-protean-20260919-001/brief.md`. Read that file for the exact packet. Replies to it are written as packets into `to-protean/inbox/`. In Phase 0 they move through the shared vault folder on Google Drive (vaultofsouls), which both sides poll every 5 minutes, and enter this repository as a pull request.

## Before relay

A receiver validates each packet at ingest grade with the stdlib validator from the public specification repository (see `spec/SYM-2P-POINTER.md`):

`python3 sym-validate.py --strict-canonical --allow-duplicates --state <self>-current.json --require-refs --now <UTC-now>`

The command must exit 0. The checks that apply in Phase 0, and the handling of failures, are defined in `procedure/PHASE-0-MANUAL-RELAY.md`.
