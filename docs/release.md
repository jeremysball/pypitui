# Release Procedure

This document describes the release process for pypitui.

## Overview

pypitui uses **GitHub Actions** for automated releases to PyPI. The workflow is triggered by pushing a version tag.

## Prerequisites

- Write access to the GitHub repository
- The repository must have **Trusted Publishing** configured on PyPI
- All tests must pass locally

## Release Steps

### 1. Update Version

Update the version in `pyproject.toml`:

```toml
[project]
version = "x.y.z"
```

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (x): Breaking changes
- **MINOR** (y): New features (backward compatible)
- **PATCH** (z): Bug fixes

### 2. Update Changelog

Add an entry to `CHANGELOG.md` at the top of the file:

```markdown
## [x.y.z] - YYYY-MM-DD

### Added
- New feature description

### Changed
- Change description

### Fixed
- Bug fix description

### Removed
- Removed feature description
```

**Changelog Categories:**
- `Added`: New features
- `Changed`: Changes to existing functionality
- `Deprecated`: Soon-to-be removed features
- `Removed`: Removed features
- `Fixed`: Bug fixes
- `Security`: Security fixes

**Example:**
```markdown
## [0.4.3] - 2025-03-13

### Added
- Support for wide character handling in boxes
- New `StatusLine` component for status bars

### Fixed
- Cursor positioning bug in wrapped input
- ANSI escape sequence handling
```

### 3. Commit Changes

Stage and commit the version and changelog updates:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to x.y.z"
git push
```

### 4. Create and Push Tag

Create an annotated tag with a descriptive message:

```bash
git tag -a vx.y.z -m "Release vx.y.z"
git push origin vx.y.z
```

**Example:**
```bash
git tag -a v0.4.3 -m "Release v0.4.3"
git push origin v0.4.3
```

### 5. Monitor Release

The GitHub Actions workflow (`release.yml`) will automatically:

1. **Validate**: Run ruff, basedpyright, and tests
2. **Build**: Create distribution packages (sdist and wheel)
3. **GitHub Release**: Create a release with changelog notes
4. **Publish**: Upload to PyPI via trusted publishing

Monitor progress at:
`https://github.com/jeremysball/pypitui/actions`

### 6. Verify GitHub Release

The workflow automatically creates a GitHub release with:
- Release title: `Release vx.y.z`
- Body: Changelog entry for that version
- Attachments: Source distribution and wheel files

Check the release at:
`https://github.com/jeremysball/pypitui/releases`

### 7. Verify PyPI Release

Check that the package appears on PyPI:
`https://pypi.org/project/pypitui/`

Verify installation:
```bash
pip install pypitui==x.y.z
```

## Manual GitHub Release (if needed)

If you need to create a GitHub release manually (e.g., after a failed workflow):

### Using GitHub Web UI:

1. Go to `https://github.com/jeremysball/pypitui/releases`
2. Click **"Draft a new release"**
3. Select the tag (e.g., `v0.4.3`)
4. Set **Release title**: `Release v0.4.3`
5. Set **Description**: Copy the relevant section from `CHANGELOG.md`
6. Optionally attach the built distribution files from `dist/`
7. Click **"Publish release"**

### Using GitHub CLI:

```bash
# Create release with changelog notes
gh release create vx.y.z \
  --title "Release vx.y.z" \
  --notes-file release_notes.md \
  dist/*
```

**Example:**
```bash
# Extract changelog for version 0.4.3
awk '/^## \[0.4.3\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md > release_notes.md

# Create release
gh release create v0.4.3 \
  --title "Release v0.4.3" \
  --notes-file release_notes.md \
  dist/*
```

## Troubleshooting

### Tag Already Exists

If you see:
```
fatal: tag 'vx.y.z' already exists
```

Delete and recreate:
```bash
git tag -d vx.y.z
git push --delete origin vx.y.z
git tag -a vx.y.z -m "Release vx.y.z"
git push origin vx.y.z
```

### Release Fails

Check the GitHub Actions logs for:
- Test failures
- Lint errors
- Build errors

Fix issues, commit, and push a new tag.

### Changelog Not Extracted

If the release notes are empty, ensure:
1. `CHANGELOG.md` exists in the repository root
2. The version header format is correct: `## [x.y.z] - YYYY-MM-DD`
3. The version in the tag matches the changelog (e.g., tag `v0.4.3` matches `## [0.4.3]`)

## Post-Release Checklist

After a successful release:

- [ ] GitHub release created with proper changelog
- [ ] PyPI package updated
- [ ] Package installs correctly: `pip install pypitui==x.y.z`
- [ ] Dependent projects (like alfred) updated to use new version
- [ ] Announce the release if significant (Discord, Twitter, etc.)

## Quick Reference

```bash
# Full release sequence
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.4.3"
git push
git tag -a v0.4.3 -m "Release v0.4.3"
git push origin v0.4.3

# Monitor
# https://github.com/jeremysball/pypitui/actions
# https://github.com/jeremysball/pypitui/releases
# https://pypi.org/project/pypitui/
```
