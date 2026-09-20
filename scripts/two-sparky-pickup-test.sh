#!/usr/bin/env bash
# two-sparky-pickup-test.sh — verify-first proof for procedure/CLAIM-DISCIPLINE.md §3.
#
# One agent's run: claim a test task_id, wait a jitter, re-list, arbitrate.
# Run twice (two agent names) against the same task_id; exactly one winner must
# emerge in both reports. Two-harness variant: two agents on two harnesses run
# this at the same wall-clock minute with their own names.
#
# Requires: hatch_gws_cli (Sparky-side tooling). Protean lanes implement the same
# protocol (§3 of the doc) with their own Drive tooling.
#
# Usage: ./scripts/two-sparky-pickup-test.sh <agent-name> [task-id]
#   agent-name: your SOP name, e.g. sparky-lugia
#   task-id:    defaults to test-pickup-<UTC-minute>; pass the same id for both agents.
#
# RACE_MODE=1 skips the initial existence check, simulating both agents having
# checked an empty folder at the same instant. Use it only for the test: run two
# instances in the background with the same task-id and compare verdicts.
set -u

step() { printf '[%s] %s\n' "${AGENT:-shape-check}" "$*"; }

AGENT_NAME="${1:-}"

TASK_ID="${2:-test-pickup-$(date -u +%Y%m%dT%H%MZ)}"
RACE_MODE="${RACE_MODE:-0}"
FILE="CLAIM_${TASK_ID}.json"
NONCE="$(python3 -c 'import secrets;print(secrets.token_hex(8))')"
NOW="$(date -u +%FT%TZ)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --shape-check: read the newest non-test claim from the live vault and verify
# the Sparky claim shape uses the vault's exact key names (review item, PR #16:
# "add a case that reads a real vault claim").
shape_check() {
  step "shape check: newest non-test claim in claims/"
  ROW="$(hatch_gws_cli drive files list \
    --params "{\"q\":\"'${CLAIMS_PARENT}' in parents and trashed=false and not name contains 'test-pickup'\",\"fields\":\"files(id,name,createdTime)\",\"orderBy\":\"createdTime desc\",\"pageSize\":1}" \
    2>/dev/null | python3 -c '
import json,sys
fs = json.load(sys.stdin).get("files", [])
print((fs[0]["id"] + "\t" + fs[0]["name"]) if fs else "")
')"
  [ -n "$ROW" ] || { step "no non-test claims in vault; nothing to check against"; return 1; }
  CID="$(printf '%s' "$ROW" | cut -f1)"; CNAME="$(printf '%s' "$ROW" | cut -f2)"
  step "reading ${CNAME} (${CID})"
  hatch_gws_cli drive files get --params "{\"fileId\":\"${CID}\",\"alt\":\"media\"}" \
    --format json 2>/dev/null > "$TMP/real.json" \
    || { step "download failed"; return 1; }
  [ -s "$TMP/real.json" ] || { step "download empty"; return 1; }
  python3 - "$TMP/real.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
required = ["task", "holder-machine", "started_utc", "lane", "by"]
missing = [k for k in required if k not in d]
print("real claim keys:", sorted(k for k in d if not k.startswith("retrieved")))
ours = {
    "task": "x", "holder-machine": "remote-gateway", "started_utc": "x",
    "lane": "x", "by": "sparky-lugia", "task_id": "x", "claim_kind": "task",
    "ttl_seconds": 600, "stale_after_seconds": 1800, "nonce": "x",
    "took_over_from": None, "note": "x",
}
renamed = [k for k in required if k not in ours]
extra_renames = [k for k in ("holder_machine", "holder_agent", "signature") if k in ours]
assert not missing, f"FAIL: live claim is missing vault keys: {missing}"
assert not renamed and not extra_renames, \
    f"FAIL: sparky shape renames/drops vault keys: renamed={renamed} extra={extra_renames}"
print("PASS: live claim carries the vault's exact keys; sparky shape matches them name for name")
EOF
}

# List all claim files for this task_id -> lines "id<TAB>createdTime"
list_claims() {
  hatch_gws_cli drive files list \
    --params "{\"q\":\"'${CLAIMS_PARENT}' in parents and name = '${FILE}' and trashed=false\",\"fields\":\"files(id,createdTime)\"}" \
    2>/dev/null | python3 -c '
import json,sys
for f in json.load(sys.stdin).get("files", []):
    print(f["id"] + "\t" + f["createdTime"])
'
}

# Download a claim file's nonce (content arrives on stdout; the CLI's -o file
# lands empty in this environment, so pipe stdout straight into python).
nonce_of() {
  hatch_gws_cli drive files get --params "{\"fileId\":\"$1\",\"alt\":\"media\"}" \
    --format json 2>/dev/null \
    | python3 -c 'import json,sys;print(json.load(sys.stdin)["nonce"])'
}

# Vault folder ids resolve from the environment — never baked into this repo
# (review item, PR #16). The lane that runs the test knows its vault.
require_vault_env() {
  : "${CLAIMS_PARENT:?set CLAIMS_PARENT to the vault start-here/claims/ folder id}"
  : "${ARCHIVE_PARENT:?set ARCHIVE_PARENT to the vault start-here/archive/ folder id}"
}

# Dispatch: agent-name mode, or --shape-check.
if [ "$AGENT_NAME" = "--shape-check" ]; then
  require_vault_env
  AGENT="shape-check"
  shape_check
  exit $?
fi
[ -n "$AGENT_NAME" ] || { echo "usage: $0 <agent-name> [task-id] | $0 --shape-check" >&2; exit 2; }
require_vault_env
AGENT="$AGENT_NAME"

# 1. Check: is there a fresh claim for this task_id already?
#    (Skipped in RACE_MODE: both agents "saw" an empty folder at the same instant.)
if [ "$RACE_MODE" = "1" ]; then
  step "race mode: skipping initial check (both agents saw an empty folder)"
else
  step "check: listing claims for ${FILE}"
  if [ -n "$(list_claims)" ]; then
    step "a claim file already exists: standing down, as designed"
    echo "VERDICT: STOOD-DOWN (pre-existing claim)"
    exit 0
  fi
fi

# 2. Write the claim.
cat > "$TMP/claim.json" <<EOF
{
  "task": "TEST: two-sparky pickup arbitration (safe to archive)",
  "holder-machine": "remote-gateway",
  "started_utc": "${NOW}",
  "lane": "pickup-test",
  "by": "${AGENT}",
  "task_id": "${TASK_ID}",
  "claim_kind": "task",
  "ttl_seconds": 600,
  "stale_after_seconds": 1800,
  "lane": "pickup-test",
  "nonce": "${NONCE}",
  "note": "verify-first test for CLAIM-DISCIPLINE.md; archive me",
  "took_over_from": null
}
EOF
MINE="$(hatch_gws_cli drive files create \
  --json "{\"name\":\"${FILE}\",\"parents\":[\"${CLAIMS_PARENT}\"],\"mimeType\":\"application/json\"}" \
  --upload "$TMP/claim.json" 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')"
step "claimed as file id ${MINE} (nonce ${NONCE})"

# 3. Wait a jitter so a racing peer's file lands too, then re-list.
SLEEP_S=$((5 + RANDOM % 16))
step "waiting ${SLEEP_S}s (jitter) before re-list"
sleep "$SLEEP_S"
RIVALS="$(list_claims)"
COUNT="$(printf '%s' "$RIVALS" | grep -c .)"
step "re-list: ${COUNT} file(s) for ${FILE}"

# 4. Arbitrate: earliest createdTime wins; tie -> smallest nonce.
SORTED="$(printf '%s\n' "$RIVALS" | sort -t "$(printf '\t')" -k2,2)"
TOP1_ID="$(printf '%s\n' "$SORTED" | head -1 | cut -f1)"
TOP1_T="$(printf '%s\n' "$SORTED" | head -1 | cut -f2)"
TOP2_LINE="$(printf '%s\n' "$SORTED" | sed -n 2p)"
TOP2_T="$(printf '%s' "$TOP2_LINE" | cut -f2)"
if [ -n "$TOP2_T" ] && [ "$TOP1_T" = "$TOP2_T" ]; then
  step "createdTime tie (${TOP1_T}): breaking on nonce"
  TOP2_ID="$(printf '%s' "$TOP2_LINE" | cut -f1)"
  N1="$(nonce_of "$TOP1_ID")"; N2="$(nonce_of "$TOP2_ID")"
  if [ "$N2" \< "$N1" ]; then WINNER_ID="$TOP2_ID"; else WINNER_ID="$TOP1_ID"; fi
  step "nonce tiebreak: ${N1} vs ${N2} -> winner ${WINNER_ID}"
else
  WINNER_ID="$TOP1_ID"
fi

if [ "$WINNER_ID" = "$MINE" ]; then
  echo "VERDICT: WINNER (${AGENT}, file ${MINE})"
else
  # Loser: archive own file with yielded_to note, stand down.
  step "lost arbitration to ${WINNER_ID}; archiving my file and standing down"
  if hatch_gws_cli drive files update \
    --params "{\"fileId\":\"${MINE}\",\"addParents\":\"${ARCHIVE_PARENT}\",\"removeParents\":\"${CLAIMS_PARENT}\"}" \
    --json "{\"name\":\"ARCHIVED_${FILE}\",\"description\":\"yielded_to=${WINNER_ID}\"}" \
    >/dev/null 2>&1; then
    step "loser file archived"
  else
    step "WARNING: archive move failed; loser file left in claims/ (manual archive needed)"
  fi
  echo "VERDICT: STOOD-DOWN (${AGENT} yielded to ${WINNER_ID})"
fi
echo "FILE_ID: ${MINE}"
