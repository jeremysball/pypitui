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

Add an entry to `CHANGELOG.md`:

```markdown
## [x.y.z] - YYYY-MM-DD

### Added
- New feature description

### Changed
- Change description

### Fixed
- Bug fix description
```

### 3. Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to x.y.z"
git push
```

### 4. Create and Push Tag

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

### 6. Verify Release

Check that the release appears on:
- **GitHub**: `https://github.com/jeremysball/pypitui/releases`
- **PyPI**: `https://pypi.org/project/pypitui/`

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

## Post-Release

After a successful release:

1. Verify the package installs correctly:
   ```bash
   pip install pypitui==x.y.z
   ```

2. Update dependent projects (like alfred) to use the new version

3. Announce the release if significant
