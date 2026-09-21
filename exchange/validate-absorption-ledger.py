#!/usr/bin/env python3
"""CI validator for absorption-ledger.jsonl.

Validates each line against the absorption-receipt/1 schema locked by Leo.
Exit codes: 0 = all valid, 1 = at least one invalid, 2 = usage/IO error.

Usage:
    python3 validate-absorption-ledger.py absorption-ledger.jsonl
    python3 validate-absorption-ledger.py --strict absorption-ledger.jsonl
"""
import json
import sys
import os

VALID_STATES = {"shipped", "received", "filed", "claimed", "absorbed",
                "integrated", "reviewed", "rejected", "deferred"}

# Transitions that are legal (from -> set of possible to)
LEGAL_TRANSITIONS = {
    "shipped":    {"received", "shipped"},  # shipped→shipped = re-ship enrichment
    "received":   {"filed", "received"},
    "filed":      {"claimed", "rejected", "deferred", "filed"},
    "claimed":    {"absorbed", "filed", "rejected", "deferred", "claimed"},
    "absorbed":   {"integrated", "claimed", "rejected", "deferred", "absorbed"},
    "integrated": {"reviewed", "absorbed", "rejected", "deferred", "integrated"},
    "reviewed":   {"integrated", "reviewed"},
    "rejected":   {"filed", "rejected"},
    "deferred":   {"filed", "deferred"},
}

VALID_SOURCE_TYPES = {"url", "arxiv", "doi", "github", "youtube",
                      "rss-item", "file-blob", "inline-text"}

REQUIRED_ALWAYS = {"schema", "norm_rules_version", "receipt_id", "batch_id",
                   "packet_id", "source_id", "source_type", "state",
                   "prev_state", "actor", "ts_utc", "source_head", "verdict",
                   "rev"}


def err(line_num, code, field, msg):
    print(f"line {line_num}: {code}: {field}: {msg}", file=sys.stderr)
    return False


def validate_line(line_num, obj, prev_revs, strict=False):
    ok = True

    # Required fields
    for field in REQUIRED_ALWAYS:
        if field not in obj:
            ok &= err(line_num, "ERR:SYN", field, "required field missing")

    # Schema version
    if obj.get("schema") != "absorption-ledger/1":
        ok &= err(line_num, "ERR:SYN", "schema", f"expected 'absorption-ledger/1', got '{obj.get('schema')}'")
        return ok  # can't validate further without knowing schema

    # Rev must be positive integer
    rev = obj.get("rev")
    if not isinstance(rev, int) or rev < 1:
        ok &= err(line_num, "ERR:SYN", "rev", f"must be positive integer, got {rev}")

    # State validation
    state = obj.get("state")
    prev_state = obj.get("prev_state")
    if state not in VALID_STATES:
        ok &= err(line_num, "ERR:SYN", "state", f"invalid state '{state}'")
    if prev_state not in VALID_STATES:
        ok &= err(line_num, "ERR:SYN", "prev_state", f"invalid prev_state '{prev_state}'")

    # Transition legality
    if state in VALID_STATES and prev_state in VALID_STATES:
        legal_targets = LEGAL_TRANSITIONS.get(prev_state, set())
        if state not in legal_targets:
            ok &= err(line_num, "ERR:SEM", "state",
                      f"illegal transition {prev_state} -> {state}")

    # Source type
    source_type = obj.get("source_type")
    if source_type not in VALID_SOURCE_TYPES:
        ok &= err(line_num, "ERR:SYN", "source_type", f"invalid type '{source_type}'")

    # Source ID format (hex string)
    source_id = obj.get("source_id", "")
    if not isinstance(source_id, str) or len(source_id) < 8:
        ok &= err(line_num, "ERR:SYN", "source_id", "must be non-empty string")

    # Rev monotonicity per source_id
    if rev is not None and source_id:
        prev_rev = prev_revs.get(source_id, 0)
        if rev <= prev_rev:
            ok &= err(line_num, "ERR:VER", "rev",
                      f"rev {rev} <= previous {prev_rev} for source_id {source_id[:16]}...")
        prev_revs[source_id] = rev

    # Reviewed state: reviewer required and must != actor
    if state == "reviewed":
        reviewer = obj.get("reviewer")
        actor = obj.get("actor")
        if not reviewer:
            ok &= err(line_num, "ERR:SEM", "reviewer", "required when state=reviewed")
        elif reviewer == actor:
            ok &= err(line_num, "ERR:SEM", "reviewer",
                      f"reviewer '{reviewer}' must differ from actor '{actor}'")
        qa = obj.get("qa")
        if qa is None:
            ok &= err(line_num, "ERR:SEM", "qa", "required when state=reviewed")

    # Integrated/reviewed: target must be non-empty
    if state in ("integrated", "reviewed"):
        target = obj.get("target")
        if target is None:
            ok &= err(line_num, "ERR:SEM", "target",
                      f"target required when state={state}")
        elif isinstance(target, dict):
            has_any = any(target.get(k) for k in ("kb_id", "repo_commit", "artifact_path"))
            if not has_any:
                ok &= err(line_num, "ERR:SEM", "target",
                          f"at least one target field required when state={state}")

    # Rejected/deferred: reason required
    if state in ("rejected", "deferred"):
        reason = obj.get("reason")
        if not reason:
            ok &= err(line_num, "ERR:SEM", "reason",
                      f"reason required when state={state}")

    # Source head required
    if not obj.get("source_head"):
        ok &= err(line_num, "ERR:SEM", "source_head", "source_head is required")

    # Receipt ID format
    receipt_id = obj.get("receipt_id", "")
    if not isinstance(receipt_id, str) or not receipt_id.startswith("abs-"):
        ok &= err(line_num, "ERR:SYN", "receipt_id", "must start with 'abs-'")

    # Packet ID format
    packet_id = obj.get("packet_id", "")
    if not isinstance(packet_id, str) or len(packet_id) < 4:
        ok &= err(line_num, "ERR:SYN", "packet_id", "must be non-empty string")

    # Actor required
    if not obj.get("actor"):
        ok &= err(line_num, "ERR:SEM", "actor", "actor is required")

    # ts_utc format (basic RFC3339 check)
    ts = obj.get("ts_utc", "")
    if not isinstance(ts, str) or "T" not in ts:
        ok &= err(line_num, "ERR:SYN", "ts_utc", "must be RFC3339 UTC string")

    return ok


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)

    strict = False
    args = []
    for arg in sys.argv[1:]:
        if arg == "--strict":
            strict = True
        else:
            args.append(arg)

    if len(args) != 1:
        print("Usage: validate-absorption-ledger.py [--strict] <file.jsonl>",
              file=sys.stderr)
        sys.exit(2)

    path = args[0]
    if not os.path.exists(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    all_ok = True
    prev_revs = {}
    line_count = 0

    with open(path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            line_count += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                err(line_num, "ERR:SYN", "json", f"invalid JSON: {e}")
                all_ok = False
                continue
            if not validate_line(line_num, obj, prev_revs, strict):
                all_ok = False

    if line_count == 0:
        print("Empty ledger (0 lines) — valid.", file=sys.stderr)

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
