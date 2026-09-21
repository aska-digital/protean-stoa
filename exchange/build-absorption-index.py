#!/usr/bin/env python3
"""Build absorption-index.json from absorption-ledger.jsonl.

Reads the ledger, keeps the highest rev per source_id, and outputs
an index mapping source_id -> latest state, receipt_id, rev, lane,
ts_utc, and target.

Usage:
    python3 build-absorption-index.py [ledger.jsonl] [output.json]
    Defaults: exchange/absorption-ledger.jsonl, exchange/absorption-index.json
"""
import json
import sys
import os
import hashlib

DEFAULT_LEDGER = "exchange/absorption-ledger.jsonl"
DEFAULT_INDEX = "exchange/absorption-index.json"


def state_rank(state):
    """Rank states by progression (higher = more terminal)."""
    ranks = {"shipped": 0, "received": 1, "filed": 2, "claimed": 3,
             "absorbed": 4, "integrated": 5, "reviewed": 6,
             "rejected": 7, "deferred": 7}
    return ranks.get(state, -1)


def build_index(ledger_path):
    """Build index from ledger, keeping the most advanced state per source_id.

    Preference order: (1) highest state rank (more terminal wins),
    (2) highest rev (newer wins within same rank). This ensures a re-ship
    at higher rev does not overwrite a reviewed entry.
    """
    index = {}

    if not os.path.exists(ledger_path):
        return index

    with open(ledger_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            source_id = obj.get("source_id")
            rev = obj.get("rev", 0)
            state = obj.get("state", "")
            if not source_id:
                continue

            existing = index.get(source_id)
            if existing is None:
                index[source_id] = _entry(obj)
            else:
                cur_rank = state_rank(existing.get("state", ""))
                new_rank = state_rank(state)
                # Prefer higher state rank; within same rank, prefer higher rev
                if (new_rank > cur_rank or
                    (new_rank == cur_rank and rev > existing.get("rev", 0))):
                    index[source_id] = _entry(obj)

    return index


def _entry(obj):
    return {
        "state": obj.get("state"),
        "receipt_id": obj.get("receipt_id"),
        "rev": obj.get("rev", 0),
        "lane": obj.get("lane"),
        "ts_utc": obj.get("ts_utc"),
        "target": obj.get("target"),
        "actor": obj.get("actor"),
        "verdict": obj.get("verdict"),
        "reason": obj.get("reason"),
        "reviewer": obj.get("reviewer"),
        "qa": obj.get("qa"),
    }


def compute_ledger_head(ledger_path):
    """Compute sha256 of the full ledger file for staleness detection."""
    if not os.path.exists(ledger_path):
        return None
    h = hashlib.sha256()
    with open(ledger_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ledger_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LEDGER
    index_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_INDEX

    index = build_index(ledger_path)
    head = compute_ledger_head(ledger_path)

    output = {
        "schema": "absorption-index/1",
        "ledger_head_sha": head,
        "entry_count": len(index),
        "entries": index
    }

    with open(index_path, "w") as f:
        json.dump(output, f, indent=2, sort_keys=True)

    print(f"Index built: {len(index)} entries from {ledger_path}", file=sys.stderr)
    print(f"Ledger head: {head}", file=sys.stderr)


if __name__ == "__main__":
    main()
