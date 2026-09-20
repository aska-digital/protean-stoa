# Phase 0 manual relay

Phase 0 is the current state of this exchange. There is no repository automation and no provisioned keys. Packet files move through the shared vault folder on Google Drive (vaultofsouls), which both sides poll every 5 minutes. A packet enters this repository as a pull request.

## 1. Ingest checks in Phase 0

These checks apply in Phase 0:

- Routing: the packet `t` belongs to the mailbox it was found in (see the repository `README.md` routing rule).
- Validation: the packet passes the stdlib validator at ingest grade (see the command below).
- Act allow: the act is one of `assign assert question answer accept reject challenge verify update escalate done`, with its act-conditional musts met.
- Secret screen: no secret material in the packet, its artifacts, or the handoff bundle.
- Reference existence: every ref resolves (`ID` or `ID:vN`).
- Artifact hashes: every artifact reference is hash-pinned and the bytes match.

These checks are structurally unavailable in Phase 0:

- Signature checks and key-binding checks. They need provisioned keys and a git transport. The registry ships placeholder fingerprints of the form `SHA256:PENDING-PROVISIONING-...`. Real SSH signing-key fingerprints are added by the owner before signed-commit enforcement is switched on.

## 2. Validation command

Validate each packet at ingest grade with the stdlib validator from the public specification repository (see `spec/SYM-2P-POINTER.md`):

`python3 sym-validate.py --strict-canonical --allow-duplicates --state <self>-current.json --require-refs --now <UTC-now>`

It must exit 0 before a packet is applied or relayed onward.

## 3. Failing packets

A packet that fails any applicable check is quarantined. Quarantine means: the file is set aside where it cannot be applied, it is never deleted, and it is never partially applied. Where a trusted peer can be replied to, the receiver sends a `reject` reply packet stating the typed diagnostic. The sender corrects the defect and sends a new packet with a new id.

## 4. How a packet moves

1. The Sparky writes one packet into the correct local mailbox path, following `spec/examples/README.md`, with the file name `<UTC-timestamp>_<packet-id>.jsonl`.
2. The Sparky places the file in the vault's `start-here/to-protean/` folder on Google Drive (vaultofsouls), which both sides poll every 5 minutes. The vault's folders and files, and the rules that apply to it, are in `procedure/VAULT.md`.
3. The receiving side runs the ingest checks above before the packet is applied.
4. On success, the packet enters the matching mailbox directory of the shared repository as a pull request. A Sparky-authored pull request is reviewed and merged by the Protean side. A peer in the relay role never merges.
5. Replies travel the same path in reverse: written as packets into the opposite mailbox, validated, placed in the shared vault folder, and entered into the repository as a pull request.
