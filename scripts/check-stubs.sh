#!/bin/bash
set -e

# Check if type stubs are up-to-date with source code
# This ensures stubs are regenerated when the public API changes

echo "Checking type stubs are up-to-date..."

# Create temp directory for comparison
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Generate fresh stubs using stubgen (mypy)
uv run mypy --install-types --non-interactive || true
uv run stubgen -p pypitui -o "$TEMP_DIR" > /dev/null 2>&1

# Compare each generated stub with existing (root-level .pyi files)
STUBS_DIR="src/pypitui"
MISSING=0
OUTDATED=0

# Check existing stubs in root of package
for stub in "$STUBS_DIR"/*.pyi; do
    if [ -f "$stub" ]; then
        filename=$(basename "$stub")
        temp_stub="$TEMP_DIR/pypitui/$filename"
        
        if [ ! -f "$temp_stub" ]; then
            # __init__.pyi might not be generated if it's empty
            if [ "$filename" = "__init__.pyi" ]; then
                continue
            fi
            echo "  ✗ $filename - source file may have been removed"
            MISSING=$((MISSING + 1))
        # Ignore mypy version comments in diff
        elif ! diff -q "$stub" "$temp_stub" > /dev/null 2>&1; then
            echo "  ✗ $filename - out of date (run: uv run stubgen -p pypitui -o out, then copy from out/pypitui/)"
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
    echo "  uv run stubgen -p pypitui -o out"
    echo "  cp out/pypitui/*.pyi src/pypitui/"
    echo "  rm -rf out/"
    echo ""
    echo "Then commit the updated stubs."
    exit 1
fi

echo "  ✓ Type stubs are up-to-date"
exit 0
