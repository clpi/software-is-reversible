#!/bin/sh
set -eu
cd "$(dirname "$0")"
LEAN="${LEAN:-lean}"
export LEAN_PATH=".:${LEAN_PATH:-}"
if grep -En '(^|[^[:alnum:]_])(sorry|admit|axiom|native_decide)([^[:alnum:]_]|$)' ./*.lean; then
  echo 'Prohibited proof escape hatch' >&2; exit 1
fi
"$LEAN" --version
out=$(mktemp)
trap 'rm -f "$out"' EXIT HUP INT TERM
for file in Reversible Axioms; do
  if "$LEAN" -DwarningAsError=true -o "$file.olean" "$file.lean" >"$out" 2>&1; then
    cat "$out"
  else
    cat "$out"; exit 1
  fi
  if grep -Eq 'sorryAx|error:|warning:' "$out"; then exit 1; fi
done
echo "gate: PASS"
