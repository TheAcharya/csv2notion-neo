# Local Test Build Script

## Overview

The `local-test-build.sh` script provides a completely ephemeral build environment for CSV2Notion Neo. It creates a self-contained build system that doesn't install anything on your system, making it perfect for development, testing, and CI/CD workflows.

## Key Features

- Fully Ephemeral: Everything is contained in project directories
- No System Installation: Uses system Python with virtual environments
- GitHub Actions Compatible: Same approach as CI/CD pipeline
- Cross-Platform: Works on macOS (Apple Silicon)
- Clean Output: Professional logging without emojis
- Flexible Updates: Multiple dependency management options

## Prerequisites

### System Requirements
- macOS (Apple Silicon)
- System Python 3.8+ installed (matches GitHub Actions workflow)
- Basic tools: `curl`, `xar`, `cpio` (usually pre-installed on macOS)

## Quick Start

### Basic Build
```bash
# From the project root directory
./scripts/local-test-build.sh
```

This will:
1. Create a virtual environment in `.build/python/`
2. Install setuptools 69.0.0 (matches GitHub Actions)
3. Install Poetry 1.7.1 in the virtual environment
4. Install project dependencies via Poetry
5. Install PyInstaller for building
6. Build the application
7. Output the binary to `test-build/csv2notion_neo`

### Run the Built Application
```bash
./test-build/csv2notion_neo --help
```

## Command Line Options

### Build Options
```bash
# Normal build
./scripts/local-test-build.sh

# Build and run tests
./scripts/local-test-build.sh --test

# Clean build directory and exit
./scripts/local-test-build.sh --clean
```

### Dependency Management
```bash
# Update poetry.lock file before building
./scripts/local-test-build.sh --update-lock

# Update all dependencies to latest versions
./scripts/local-test-build.sh --update-deps

# Update specific packages
./scripts/local-test-build.sh --update requests pytest

# Only update lock file (no build)
./scripts/local-test-build.sh --lock-only --update requests

# Show outdated packages
./scripts/local-test-build.sh --show-outdated
```

### Help
```bash
# Show detailed help
./scripts/local-test-build.sh --help
```

## Directory Structure

After running the script, your project will have:

```
csv2notion-neo/
├── .build/                    # Ephemeral build environment (gitignored)
│   ├── python/               # Virtual environment
│   ├── venv/                 # Poetry virtual environment
│   └── cache/                # Poetry cache
├── test-build/               # Build output (gitignored)
│   ├── csv2notion_neo       # Final executable binary
│   └── build/               # PyInstaller build artifacts
├── scripts/
│   └── local-test-build.sh  # This script
└── ... (other project files)
```

## Detailed Usage Examples

### Development Workflow

1. First Time Setup
   ```bash
   # Clone the repository
   git clone https://github.com/your-username/csv2notion-neo.git
   cd csv2notion-neo
   
   # Build the application
   ./scripts/local-test-build.sh
   ```

2. Regular Development
   ```bash
   # Make changes to your code
   # ...
   
   # Rebuild
   ./scripts/local-test-build.sh
   
   # Test the changes
   ./test-build/csv2notion_neo --help
   ```

3. Update Dependencies
   ```bash
   # Update specific package
   ./scripts/local-test-build.sh --update requests
   
   # Update all dependencies
   ./scripts/local-test-build.sh --update-deps
   ```

4. Clean and Rebuild
   ```bash
   # Clean everything
   ./scripts/local-test-build.sh --clean
   
   # Fresh build
   ./scripts/local-test-build.sh
   ```

### CI/CD Integration

The script is designed to work seamlessly with GitHub Actions and uses identical versions:

```yaml
# Example GitHub Actions step
- name: Build CSV2Notion Neo
  run: |
    chmod +x scripts/local-test-build.sh
    ./scripts/local-test-build.sh
```

**Version Alignment with GitHub Actions:**
- Python: 3.8+ (matches `BUILD_PYTHON_VERSION: 3.8`)
- Poetry: 1.7.1 (matches `BUILD_POETRY_VERSION: 1.7.1`)
- Setuptools: 69.0.0 (matches `setuptools==69.0.0`)
- PyInstaller: Latest version (matches CI workflow)

## Environment Details

### Virtual Environment
- Location: `.build/python/`
- Python: Uses system Python 3.8+ with `python3 -m venv`
- Setuptools: 69.0.0 (installed before Poetry)
- Poetry: 1.7.1 (installed via pip in the virtual environment)
- Dependencies: Managed by Poetry in `.build/venv/`

### Build Output
- Binary: `test-build/csv2notion_neo`
- Size: ~8.3MB (typical)
- Architecture: Native to your system (Intel/Apple Silicon)
- Dependencies: Self-contained (no external dependencies)

### PyInstaller Configuration
- Spec File: Uses `csv2notion_neo.spec` from project root
- Output Directory: `test-build/`
- Build Artifacts: `test-build/build/`
- Installation: Installed separately (not in `pyproject.toml`)

## Troubleshooting

### Common Issues

1. "System Python 3 is not available"
   ```bash
   # Install Python 3
   brew install python
   ```

2. "Missing required tools"
   ```bash
   # Install curl if missing
   brew install curl
   # xar and cpio are usually pre-installed on macOS
   ```

3. Build fails with PyInstaller errors
   ```bash
   # Clean and rebuild
   ./scripts/local-test-build.sh --clean
   ./scripts/local-test-build.sh
   ```

4. Permission denied
   ```bash
   # Make script executable
   chmod +x scripts/local-test-build.sh
   ```

### Debug Mode

If you encounter issues, you can inspect the build environment:

```bash
# Check what's in the build directory
ls -la .build/

# Check the virtual environment
.build/python/bin/python --version

# Check setuptools installation
.build/python/bin/pip show setuptools

# Check Poetry installation
.build/python/bin/poetry --version

# Check PyInstaller installation
.build/python/bin/poetry run pyinstaller --version
```

## Cleanup

### Manual Cleanup
```bash
# Remove build directories
rm -rf .build/ test-build/

# Or use the script
./scripts/local-test-build.sh --clean
```

### What Gets Cleaned
- `.build/` - Complete ephemeral environment
- `test-build/` - Build output and artifacts
- `dist/` - Legacy build output (if exists)
- `build/` - Legacy build artifacts (if exists)

## Best Practices

### For Developers
1. Always run from project root: The script expects `pyproject.toml` in the current directory
2. Use clean builds: Run `--clean` when switching branches or after dependency changes
3. Test the binary: Always verify `./test-build/airlift --help` works after building
4. Keep dependencies updated: Use `--show-outdated` to check for updates
5. Version consistency: Local builds use identical versions to production CI/CD

### For CI/CD
1. Use exact versions: The script uses identical versions to GitHub Actions workflow
2. Clean before build: Always run `--clean` in CI to ensure fresh builds
3. Cache dependencies: Consider caching `.build/` in CI for faster builds
4. Test the output: Verify the built binary works in your deployment environment
5. Version consistency: Local builds match production builds exactly

## Script Configuration

### Environment Variables
The script uses these configuration variables (aligned with GitHub Actions):
```bash
BUILD_DIR=".build"           # Ephemeral build environment
TEST_BUILD_DIR="test-build"  # Build output directory
PYTHON_VERSION="3.8"         # Target Python version (matches CI)
POETRY_VERSION="1.7.1"       # Poetry version (matches CI)
SETUPTOOLS_VERSION="69.0.0"  # Setuptools version (matches CI)
```

### Customization
To modify the script behavior, edit the configuration section at the top of `local-test-build.sh`.

## Support

### Getting Help
```bash
# Show script help
./scripts/local-test-build.sh --help

# Check script version and configuration
head -20 scripts/local-test-build.sh
```

### Reporting Issues
If you encounter issues with the build script:
1. Run `./scripts/local-test-build.sh --clean`
2. Try a fresh build
3. Check the prerequisites
4. Review the troubleshooting section above

## Security Notes

- The script only downloads and installs packages from trusted sources (PyPI, Poetry)
- All dependencies are installed in isolated virtual environments
- No system-wide installations or modifications are made
- The build environment is completely ephemeral and can be safely deleted
- Version pinning ensures reproducible builds across environments

## Version Alignment

This build script is designed to produce identical builds to the GitHub Actions workflow:

- **Python**: 3.8+ (matches `BUILD_PYTHON_VERSION: 3.8`)
- **Poetry**: 1.7.1 (matches `BUILD_POETRY_VERSION: 1.7.1`)
- **Setuptools**: 69.0.0 (matches `setuptools==69.0.0`)
- **PyInstaller**: Latest version (matches CI workflow)

This ensures that local development builds are identical to production releases, eliminating any potential issues caused by version mismatches.

---

Note: This script is designed to be completely self-contained and safe to run. It will not modify your system Python installation or install any packages globally. 