#!/bin/sh
set -eu
cd "$(dirname "$0")"
export PYTHONHASHSEED=91
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
if grep -En '(^|[^[:alnum:]_])(sorry|admit|native_decide|sorryAx)([^[:alnum:]_]|$)' proof/*.lean; then
    echo 'Proof contains an admission/escape token' >&2
    exit 2
fi
"${LEAN:-lean}" -DwarningAsError=true proof/Reversible.lean > "$tmp/audit"
cmp "$tmp/audit" proof/lean-audit.txt
for test in fibers schedule; do
    python3 -O -B "empirical/$test.py" > "$tmp/$test.json"
    cmp "$tmp/$test.json" "empirical/$test.json"
done
python3 -O -B empirical/tensor_bridge.py --check
echo 'Lean and all empirical receipts match'
