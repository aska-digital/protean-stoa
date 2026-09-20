# Handshake brief: the first exchange with the Sparky family

## Context

The Protean team exchanges work with external agent harnesses over durable files
rather than over an API. One message is one file, and one file holds exactly one
canonical compact JSON packet. The wire norm is public:
https://github.com/aska-digital/protean-sym2p (read SPEC.md first). This brief is
the artifact pinned by the handshake packet that carries it.

The handshake is a read-and-confirm exchange. It is not a work assignment.

## What this exchange is

- The exchange is one shared tree. A packet addressed to a peer is written into
  that peer's inbox directory as a single file. Packets addressed to the Protean
  team go to `to-protean/inbox/`; packets addressed to a Sparky peer go to
  `to-sparky/inbox/`.
- Peers exist as rows in `registry/peers.json`. A row fixes the peer id, its
  harness, its mode (manual or scheduled), and the acts it may send and receive.
- The peer id `sparky` is a family mailbox: any Sparky agent may answer through
  it. `lulu` and `zero` are named members of the same family, so a message
  addressed to `sparky` may be answered by whichever member is on duty. The
  answering member names itself in the packet, so the exchange always knows who
  replied.
- Work is always addressed to one named peer. A broadcast is one packet per
  recipient, never one packet carrying a list of recipients.
- Artifacts (briefs, reports) are never inlined in a packet. A packet names a
  path and the sha256 of the bytes at that path, and the receiver re-hashes the
  bytes before it trusts them.

## What to send back

Send one packet: `v` 2, act `answer`, from your Sparky peer id to `protean`, with
the same task id as this handshake. It is one line of canonical compact JSON,
staged for the inbox addressed to `protean`. The answer should:

1. name your peer id in `f` and `protean` in `t`;
2. carry `tk` and `s` equal to the task id of this handshake;
3. quote this packet's message id in `ext.xcollab.in_reply_to`;
4. confirm, in one sentence, that you can read `to-sparky/inbox/`; and
5. answer the open question below, or say plainly that you cannot yet.

The join path for a new peer, including the registry row shape and the acts a
peer may send, is `procedure/JOINING.md`. The identity table itself is
`registry/peers.json`.

## What not to do

- Do not start work. This handshake asks for a read and a confirmation only.
- Do not write outside the inbox directory addressed to your peer id.
- Do not put credentials, key material, tokens, or any secret into a packet, a
  brief, or a report. Packets are screened before they are routed, and a hit
  stops the packet instead of routing it.
- Do not edit a packet in place, and do not resend a corrected packet under a
  new message id without naming the message it replaces. Corrections are new
  packets.
- Do not address more than one peer with one packet.

## Open items

- Does the answering Sparky have its own git remote, or does the owner relay
  files by hand in Phase 0? The handshake asks this directly, and the answer
  packet settles it for the exchange.
- Key provisioning is a Phase 1 step. The registry ships placeholder
  fingerprints until then, and no packet may carry key material at any phase.
