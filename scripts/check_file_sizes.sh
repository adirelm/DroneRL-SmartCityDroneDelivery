#!/usr/bin/env bash
# Fail if any tracked Python file exceeds 150 lines (CLAUDE.md rule).
set -euo pipefail

LIMIT=150
violations=()
while IFS= read -r -d '' file; do
    lines=$(wc -l < "$file")
    if [ "$lines" -gt "$LIMIT" ]; then
        violations+=("$file: $lines lines")
    fi
done < <(find src tests scripts analysis -name '*.py' -print0)

if [ ${#violations[@]} -gt 0 ]; then
    echo "Files exceeding ${LIMIT}-line limit:" >&2
    printf '  %s\n' "${violations[@]}" >&2
    exit 1
fi
echo "All Python files within ${LIMIT}-line limit."
