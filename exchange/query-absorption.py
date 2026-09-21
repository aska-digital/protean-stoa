#!/usr/bin/env python3
"""Query absorption status by URL, source_id, or batch.

Usage:
    python3 query-absorption.py --url "https://example.com/article"
    python3 query-absorption.py --source-id "abc123..."
    python3 query-absorption.py --batch "batch-20260921-sparky118-a"
    python3 query-absorption.py --url "..." --raw   # machine-readable JSON

Exit codes: 0 = found, 1 = not found / unverified, 2 = usage error.
"""
import json
import sys
import os
import hashlib
import re
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

DEFAULT_INDEX = "exchange/absorption-index.json"
DEFAULT_LEDGER = "exchange/absorption-ledger.jsonl"
DEFAULT_BATCH_DIR = "exchange/absorption-batches"

# Tracking params to strip
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "mc_cid", "mc_eid", "igshid", "vero_id", "vero_conv",
    "ref", "ref_src", "ref_url", "_ga", "_gl", "mc_eid",
}

# State descriptions for human-readable output
STATE_DESCRIPTIONS = {
    "shipped": "Shipped by Sparky — not yet received",
    "received": "Received by vault ingress",
    "filed": "Filed into processing queue",
    "claimed": "Claimed for processing by a Protean lane",
    "absorbed": "Absorbed into a Protean lane",
    "integrated": "Integrated into a durable artifact",
    "reviewed": "Independently reviewed and verified",
    "rejected": "Rejected",
    "deferred": "Deferred for later processing",
}

# Read-back verdicts
def read_back_verdict(state):
    if state is None:
        return "NEW — not yet in the pipeline"
    if state in ("shipped", "received", "filed"):
        return "NEW-ish — in pipeline, not yet absorbed"
    if state == "claimed":
        return "IN PROGRESS — claimed for processing"
    if state == "absorbed":
        return "IN PROGRESS — absorbed, integration pending"
    if state == "integrated":
        return "ABSORBED — integrated into artifact"
    if state == "reviewed":
        return "ABSORBED-VERIFIED — fully processed and reviewed"
    if state in ("rejected", "deferred"):
        return "NOT ABSORBED"
    return "UNKNOWN"


def normalize_url(raw_url):
    """Simplified URL normalization per Leo's rules §2."""
    try:
        parsed = urlparse(raw_url)
    except Exception:
        return None

    # Scheme: lowercase
    scheme = parsed.scheme.lower() if parsed.scheme else "https"

    # Host: lowercase, strip www.
    host = parsed.hostname.lower() if parsed.hostname else ""
    host = re.sub(r"^www\.", "", host)
    host = host.rstrip(".")

    # Path: strip trailing / unless root, strip /index.html
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    if path.endswith("/index.html"):
        path = path[:-len("index.html")]
        if not path:
            path = "/"

    # Query: strip tracking params, sort remaining
    query = ""
    if parsed.query:
        params = parse_qs(parsed.query, keep_blank_values=True)
        filtered = {k: v for k, v in params.items()
                    if k.lower() not in TRACKING_PARAMS}
        if filtered:
            # Sort and reconstruct
            sorted_params = sorted(filtered.items())
            parts = []
            for k, vs in sorted_params:
                for v in vs:
                    parts.append(f"{k}={v}")
            query = "&".join(parts)

    # Fragment: drop entirely
    normalized = urlunparse((scheme, host, path, "", query, ""))
    return normalized


def compute_source_id(source_type, canonical_form, source_version=""):
    """Compute source_id per Leo's §2."""
    key = f"{source_type}|{canonical_form}|{source_version}"
    return hashlib.sha256(key.encode()).hexdigest()


def detect_source_type(url_or_id):
    """Detect source type from URL pattern."""
    if not url_or_id:
        return "url", url_or_id
    lower = url_or_id.lower()
    if "arxiv.org/" in lower:
        return "arxiv", url_or_id
    if lower.startswith("doi:") or "doi.org/" in lower:
        return "doi", url_or_id
    if "github.com/" in lower:
        return "github", url_or_id
    if "youtube.com/" in lower or "youtu.be/" in lower:
        return "youtube", url_or_id
    return "url", url_or_id


def query_by_source_id(index_data, source_id):
    """Look up source_id in index."""
    entries = index_data.get("entries", {})
    return entries.get(source_id)


def query_by_url(index_data, raw_url):
    """Normalize URL and look up in index."""
    source_type, _ = detect_source_type(raw_url)
    normalized = normalize_url(raw_url)
    if not normalized:
        return None, raw_url, None
    source_id = compute_source_id(source_type, normalized)
    result = query_by_source_id(index_data, source_id)
    return result, raw_url, source_id


def query_by_batch(ledger_path, batch_id):
    """Read all ledger lines for a batch."""
    results = []
    if not os.path.exists(ledger_path):
        return results
    with open(ledger_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("batch_id") == batch_id:
                results.append(obj)
    return results


def format_human(result, raw_query, source_id=None, batch_results=None):
    """Format human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("ABSORPTION STATUS QUERY")
    lines.append("=" * 60)

    if batch_results is not None:
        lines.append(f"Batch: {raw_query}")
        lines.append(f"Entries: {len(batch_results)}")
        states = {}
        for entry in batch_results:
            s = entry.get("state", "unknown")
            states[s] = states.get(s, 0) + 1
        lines.append("")
        lines.append("State distribution:")
        for state, count in sorted(states.items()):
            desc = STATE_DESCRIPTIONS.get(state, state)
            lines.append(f"  {state:15s} {count:4d}  ({desc})")
        lines.append("")
        # Show first few rejected/deferred
        rejections = [e for e in batch_results if e.get("state") in ("rejected", "deferred")]
        if rejections:
            lines.append(f"Rejected/deferred ({len(rejections)}):")
            for entry in rejections[:5]:
                sid = entry.get("source_id", "?")[:16]
                reason = entry.get("reason", "no reason")
                lines.append(f"  {sid}... — {reason}")
            if len(rejections) > 5:
                lines.append(f"  ... and {len(rejections) - 5} more")
        return "\n".join(lines)

    lines.append(f"Query: {raw_query}")
    if source_id:
        lines.append(f"Source ID: {source_id}")
    lines.append("")

    if result is None:
        verdict = read_back_verdict(None)
        lines.append(f"Verdict: {verdict}")
        lines.append("")
        lines.append("This source has not been seen in the pipeline.")
        lines.append("Safe to ship or process.")
    else:
        state = result.get("state")
        verdict = read_back_verdict(state)
        lines.append(f"Verdict: {verdict}")
        lines.append(f"State: {state} — {STATE_DESCRIPTIONS.get(state, state)}")
        lines.append(f"Receipt: {result.get('receipt_id', '?')}")
        lines.append(f"Rev: {result.get('rev', '?')}")
        if result.get("lane"):
            lines.append(f"Lane: {result['lane']}")
        if result.get("ts_utc"):
            lines.append(f"Last updated: {result['ts_utc']}")
        if result.get("actor"):
            lines.append(f"Actor: {result['actor']}")
        if result.get("target"):
            target = result["target"]
            if target.get("kb_id"):
                lines.append(f"KB ID: {target['kb_id']}")
            if target.get("repo_commit"):
                lines.append(f"Repo commit: {target['repo_commit']}")
            if target.get("artifact_path"):
                lines.append(f"Artifact: {target['artifact_path']}")
        if result.get("verdict") in ("rejected", "deferred") and result.get("reason"):
            lines.append(f"Reason: {result['reason']}")
        if result.get("reviewer"):
            lines.append(f"Reviewer: {result['reviewer']}")
        if result.get("qa"):
            qa = result["qa"]
            lines.append(f"QA: {qa.get('check', '?')} — {qa.get('detail', '')}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_raw(result, raw_query, source_id=None, batch_results=None):
    """Format machine-readable JSON output."""
    output = {
        "query": raw_query,
        "source_id": source_id,
        "ledger_head_sha": None,
    }
    if batch_results is not None:
        output["batch"] = True
        output["entry_count"] = len(batch_results)
        output["entries"] = batch_results
    elif result is not None:
        output["found"] = True
        output.update(result)
    else:
        output["found"] = False
        output["verdict"] = "NEW"
    return json.dumps(output, indent=2, sort_keys=True)


def main():
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:s:b:r",
                                   ["help", "url=", "source-id=", "batch=",
                                    "raw", "index=", "ledger="])
    except getopt.GetoptError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    raw_output = False
    url = None
    source_id = None
    batch = None
    index_path = DEFAULT_INDEX
    ledger_path = DEFAULT_LEDGER

    for opt, val in opts:
        if opt in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif opt in ("-u", "--url"):
            url = val
        elif opt in ("-s", "--source-id"):
            source_id = val
        elif opt in ("-b", "--batch"):
            batch = val
        elif opt in ("-r", "--raw"):
            raw_output = True
        elif opt == "--index":
            index_path = val
        elif opt == "--ledger":
            ledger_path = val

    if not url and not source_id and not batch:
        print("Error: specify --url, --source-id, or --batch", file=sys.stderr)
        sys.exit(2)

    # Load index
    index_data = {"entries": {}, "ledger_head_sha": None}
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            try:
                index_data = json.load(f)
            except json.JSONDecodeError:
                pass

    result = None
    raw_query = url or source_id or batch
    sid = source_id

    if batch:
        batch_results = query_by_batch(ledger_path, batch)
        if raw_output:
            print(format_raw(None, raw_query, None, batch_results))
        else:
            print(format_human(None, raw_query, None, batch_results))
        sys.exit(0 if batch_results else 1)

    if url:
        result, _, sid = query_by_url(index_data, url)
    elif source_id:
        result = query_by_source_id(index_data, source_id)

    if raw_output:
        print(format_raw(result, raw_query, sid))
    else:
        print(format_human(result, raw_query, sid))

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
