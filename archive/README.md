# Archive Directory

This directory contains files that were previously used in the project but are no longer actively maintained or used in the current development workflow.

## Archived Files

### .pre-commit-config.yaml
- Purpose: Pre-commit hooks configuration for local development
- Why Archived: CI/CD pipeline uses GitHub Actions workflows instead
- Previous Usage: Local code quality checks (black, isort, mypy, pytest)
- Current Alternative: GitHub Actions handles all testing and quality checks

### .versionrc.js
- Purpose: Standard-version configuration for automated version management
- Why Archived: Project uses manual version management instead
- Previous Usage: Automated version bumping and changelog generation
- Current Alternative: Manual version updates in csv2notion_neo/version.py

### archive_tests.py
- Purpose: Legacy test file from previous development
- Why Archived: Replaced by current test suite in tests/ directory
- Previous Usage: Early testing implementation
- Current Alternative: Comprehensive test suite in tests/test_upload.py

## Current Development Workflow

The project now uses:
- CI/CD: GitHub Actions workflows (.github/workflows/)
- Testing: pytest with tests/ directory
- Version Management: Manual updates in csv2notion_neo/version.py
- Code Quality: GitHub Actions automated checks

## Restoration Notes

If you need to restore any of these files:
1. Copy the file back to the project root
2. Update any paths or configurations as needed
3. Ensure compatibility with current project structure
4. Update documentation to reflect the change

## Archive Policy

Files are moved to archive when:
- They're no longer used in the current workflow
- They've been replaced by better alternatives
- They're kept for reference but not actively maintained
- They represent deprecated development approaches 