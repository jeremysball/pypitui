#!/bin/bash
set -e

# Check if type stubs are up-to-date with source code
# This ensures stubs are regenerated when the public API changes

echo "Checking type stubs are up-to-date..."

# Create temp directory for comparison
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Generate fresh stubs to temp location
uv run stubgen src/pypitui -o "$TEMP_DIR" --no-import 2>/dev/null || true

# Compare each generated stub with existing
STUBS_DIR="src/pypitui/stubs/pypitui"
MISSING=0
OUTDATED=0

if [ -d "$STUBS_DIR" ]; then
    for stub in "$STUBS_DIR"/*.pyi; do
        if [ -f "$stub" ]; then
            filename=$(basename "$stub")
            temp_stub="$TEMP_DIR/pypitui/$filename"
            
            if [ ! -f "$temp_stub" ]; then
                echo "  ✗ $filename - source file may have been removed"
                MISSING=$((MISSING + 1))
            elif ! diff -q "$stub" "$temp_stub" > /dev/null 2>&1; then
                echo "  ✗ $filename - out of date (run: uv run stubgen src/pypitui -o src/pypitui/stubs)"
                OUTDATED=$((OUTDATED + 1))
            fi
        fi
    done
fi

# Check for new source files without stubs
for source in src/pypitui/*.py; do
    if [ -f "$source" ]; then
        filename=$(basename "$source" .py)
        stub="$STUBS_DIR/${filename}.pyi"
        temp_stub="$TEMP_DIR/pypitui/${filename}.pyi"
        
        if [ -f "$temp_stub" ] && [ ! -f "$stub" ]; then
            echo "  ✗ ${filename}.pyi - missing stub file"
            MISSING=$((MISSING + 1))
        fi
    fi
done

if [ $MISSING -gt 0 ] || [ $OUTDATED -gt 0 ]; then
    echo ""
    echo "Stubs need updating. Run:"
    echo "  uv run stubgen src/pypitui -o src/pypitui/stubs"
    echo ""
    echo "Then refine manually if needed before committing."
    exit 1
fi

echo "  ✓ Type stubs are up-to-date"
exit 0
