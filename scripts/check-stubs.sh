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

# Compare each generated stub with existing (root-level .pyi files)
STUBS_DIR="src/pypitui"
MISSING=0
OUTDATED=0

# Check existing stubs in root of package
for stub in "$STUBS_DIR"/*.pyi; do
    if [ -f "$stub" ]; then
        filename=$(basename "$stub")
        # Skip the pypitui.pyi top-level re-export file
        if [ "$filename" = "pypitui.pyi" ]; then
            continue
        fi
        temp_stub="$TEMP_DIR/pypitui/$filename"
        
        if [ ! -f "$temp_stub" ]; then
            # __init__.pyi is hand-written, stubgen doesn't generate it
            if [ "$filename" = "__init__.pyi" ]; then
                continue
            fi
            echo "  ✗ $filename - source file may have been removed"
            MISSING=$((MISSING + 1))
        elif ! diff -q "$stub" "$temp_stub" > /dev/null 2>&1; then
            echo "  ✗ $filename - out of date (run: uv run stubgen src/pypitui -o src/pypitui/stubs, then copy and refine)"
            OUTDATED=$((OUTDATED + 1))
        fi
    fi
done

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
    echo "  cp src/pypitui/stubs/pypitui/*.pyi src/pypitui/"
    echo ""
    echo "Then refine manually before committing."
    exit 1
fi

echo "  ✓ Type stubs are up-to-date"
exit 0
