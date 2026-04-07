#!/usr/bin/env bash
set -euo pipefail

TOOL="$(cd "$(dirname "$0")/.." && pwd)/append"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

errors=0
fail() { echo "FAIL: $1"; errors=$((errors + 1)); }

# --- Test 1: single line ---
"$TOOL" "$TMPDIR/t1.md" "hello world"
[ "$(cat "$TMPDIR/t1.md")" = "hello world" ] || fail "single line should write 'hello world'"

# --- Test 2: append second line ---
"$TOOL" "$TMPDIR/t1.md" "second line"
[ "$(wc -l < "$TMPDIR/t1.md")" -eq 2 ] || fail "should have 2 lines after second append"

# --- Test 3: multiline via stdin ---
"$TOOL" "$TMPDIR/t2.md" - <<'EOF'
## Header

- item 1
- item 2
EOF
[ "$(wc -l < "$TMPDIR/t2.md")" -eq 4 ] || fail "multiline should have 4 lines, got $(wc -l < "$TMPDIR/t2.md")"

# --- Test 4: multiline append to existing ---
"$TOOL" "$TMPDIR/t2.md" - <<'EOF'

## Second header
EOF
[ "$(wc -l < "$TMPDIR/t2.md")" -eq 6 ] || fail "should have 6 lines after second multiline append"

# --- Test 5: creates parent dirs? no, just file ---
"$TOOL" "$TMPDIR/newfile.md" "created"
[ -f "$TMPDIR/newfile.md" ] || fail "should create new file"

# --- Test 6: special characters ---
"$TOOL" "$TMPDIR/t3.md" 'backticks `code` and $vars and "quotes"'
grep -q 'backticks' "$TMPDIR/t3.md" || fail "special chars should survive"

# --- Test 7: empty text ---
"$TOOL" "$TMPDIR/t4.md" ""
[ -f "$TMPDIR/t4.md" ] || fail "empty text should still create file"

# --- Result ---
if [ "$errors" -eq 0 ]; then
  echo "PASS"
else
  echo "FAIL ($errors errors)"
fi
