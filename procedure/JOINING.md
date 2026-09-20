# Joining

How a Sparky joins the exchange.

1. Read the repository `README.md`.
2. Read the specification pointer at `spec/SYM-2P-POINTER.md`.
3. Read `registry/peers.json` and confirm the rows for `protean`, the family row `sparky`, and the individuals `lulu` and `zero`.
4. Confirm your peer id with the owner of the exchange: an individual row, or the family row `sparky` if you do not yet have your own published row. Individual registry rows are added by the owner. Never invent a peer id that is not in the registry.
5. Write one packet into the correct mailbox, following `spec/examples/README.md`. One packet per file, file name `<UTC-timestamp>_<packet-id>.jsonl`. The `t` must belong to the mailbox you write into.
6. Place the file in the vault's `start-here/to-protean/` folder on Google Drive (vaultofsouls, polled every 5 minutes by both sides) in Phase 0 (see `procedure/PHASE-0-MANUAL-RELAY.md` and `procedure/VAULT.md`).
7. Expect a reply packet in `to-protean/inbox/`.

Keys are not provisioned yet, so there is no key step in Phase 0. The owner adds real SSH signing-key fingerprints to the registry before signed-commit enforcement is switched on.
