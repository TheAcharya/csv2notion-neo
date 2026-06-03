# Local Test Build Script

## Overview

The `local-test-build.sh` script provides a completely ephemeral build environment for CSV2Notion Neo. It creates a self-contained build system that doesn't install anything on your system, making it perfect for development, testing, and CI/CD workflows.

## Key Features

- Fully Ephemeral: Everything is contained in project directories
- No System Installation: Downloads standalone CPython into `.build/python/` (python-build-standalone)
- GitHub Actions Compatible: Poetry, setuptools, and plugin-export pins are intended to match CI/CD (macOS uses standalone Python bootstrap)
- Cross-Platform: Works on macOS (Apple Silicon or Intel)
- Clean Output: Professional logging without emojis
- Flexible Updates: Multiple dependency management options
- Comprehensive Testing: Built-in support for the comprehensive test suite (no Notion credentials required)

## Prerequisites

### System Requirements
- macOS (Apple Silicon or Intel)
- Host tools only: `curl` and `tar` (to download/extract Python into `.build/`)
- No system Python, Homebrew Python, or Poetry install required

## Quick Start

### Basic Build
```bash
# From the project root directory
./scripts/local-test-build.sh
```

This will:
1. Download standalone CPython 3.14.5 into `.build/python/` (pinned python-build-standalone release)
2. Install pip 26.1.2 in `.build/python/`
3. Install setuptools 82.0.1 in `.build/python/`
4. Install Poetry 2.4.1 in `.build/python/`
5. Install poetry-plugin-export 1.10.0
6. Install project dependencies via Poetry into `.build/venv/`
7. Install PyInstaller for building
8. Build the application
9. Output the binary to `test-build/csv2notion_neo`

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

# Run comprehensive test suite (96 tests, mocked Notion API)
./scripts/local-test-build.sh --comprehensive-test

# Clean .build/, test-build/, .pytest_cache/ and exit
./scripts/local-test-build.sh --clean
```

### Dependency Management
```bash
# Update poetry.lock file before building
./scripts/local-test-build.sh --update-lock

# Update all dependencies to latest versions
./scripts/local-test-build.sh --update-deps

# Update specific packages
./scripts/local-test-build.sh --update notion-client urllib3

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
│   ├── python/               # Standalone CPython + pip + Poetry
│   ├── downloads/            # Cached Python tarball
│   ├── venv/                 # Poetry project virtual environment
│   ├── cache/                # Poetry cache
│   ├── pip-cache/            # pip download cache
│   ├── poetry-config/        # Poetry configuration
│   └── poetry-home/          # Poetry application data
├── test-build/               # Build output (gitignored)
│   ├── csv2notion_neo        # Final executable binary
│   └── build/                # PyInstaller build artifacts
├── scripts/
│   └── local-test-build.sh   # This script
└── ... (other project files)
```

## Detailed Usage Examples

### Development Workflow

1. First Time Setup
   ```bash
   # Clone the repository
   git clone https://github.com/TheAcharya/csv2notion-neo.git
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
   ./scripts/local-test-build.sh --update notion-client

   # Update all dependencies
   ./scripts/local-test-build.sh --update-deps
   ```

4. Run Comprehensive Tests
   ```bash
   # Validates CLI args and Notion SDK behavior without live API credentials
   ./scripts/local-test-build.sh --comprehensive-test
   ```

5. Clean and Rebuild
   ```bash
   # Clean everything
   ./scripts/local-test-build.sh --clean

   # Fresh build
   ./scripts/local-test-build.sh
   ```

### CI/CD Integration

The script is designed to work seamlessly with GitHub Actions. Use the same Poetry, setuptools, and plugin-export versions in workflow `env` blocks:

```yaml
# Example GitHub Actions step
- name: Build CSV2Notion Neo
  run: |
    chmod +x scripts/local-test-build.sh
    ./scripts/local-test-build.sh

# Example comprehensive test step
- name: Run Comprehensive Tests
  run: |
    chmod +x scripts/local-test-build.sh
    ./scripts/local-test-build.sh --comprehensive-test
```

**Version alignment** (local script pins; workflows should use matching `env` values):

| Component | Local script | Suggested CI `env` |
|-----------|--------------|-------------------|
| Python | Standalone **3.14.5** on macOS | **3.14** (`BUILD_PYTHON_VERSION`) |
| pip | **26.1.2** (bootstrap only) | — |
| Poetry | **2.4.1** | `BUILD_POETRY_VERSION` |
| setuptools | **82.0.1** | `BUILD_SETUPTOOLS_VERSION` |
| poetry-plugin-export | **1.10.0** | `BUILD_POETRY_PLUGIN_EXPORT_VERSION` |
| PyInstaller | latest (Poetry venv at build time) | same pattern as CI binary job |

Local macOS builds download a standalone CPython tarball; CI runners typically use `actions/setup-python`. Tooling pins (Poetry, setuptools, export plugin) should match.

## Comprehensive Testing

The `--comprehensive-test` option runs `tests/test_comprehensive.py` (96 tests) with mocked Notion API calls—no integration token required.

- CLI validation: 50+ arguments and switches
- Notion SDK adapter tests (mocked `notion_client.Client`)
- Rate-limit and throttle behavior (`TestNotionRateLimitAndThrottle`)
- Automatic setup: creates `.build/` if missing

```bash
./scripts/local-test-build.sh --comprehensive-test
```

## Environment Details

### Build Environment
- Standalone Python: `.build/python/` (python-build-standalone 3.14.5, not system Python)
- Project venv: `.build/venv/` (Poetry-managed dependencies)
- pip: 26.1.2 (pinned bootstrap in `.build/python/`)
- Setuptools: 82.0.1 (installed before Poetry)
- Poetry: 2.4.1 (installed via pip in `.build/python/`)
- poetry-plugin-export: 1.10.0
- Dependencies: Managed by Poetry in `.build/venv/`

### Build Output
- Binary: `test-build/csv2notion_neo`
- Size: ~18MB typical on macOS (Python 3.14 one-file bundle; varies by platform)
- Architecture: Native to your system
- Dependencies: Self-contained (no external dependencies)

### PyInstaller Configuration
- Spec File: Uses `csv2notion_neo.spec` from project root
- Output Directory: `test-build/`
- Build Artifacts: `test-build/build/`
- Installation: Installed separately (not in `pyproject.toml`)

## Troubleshooting

### Common Issues

1. "Missing required host tools"
   ```bash
   # curl and tar must be available (standard on macOS)
   which curl tar
   ```

2. "Failed to download standalone Python"
   ```bash
   # Retry after network check, or clean and rebuild
   ./scripts/local-test-build.sh --clean
   ./scripts/local-test-build.sh
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

5. SSL Warning during build
   ```
   urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+,
   currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'
   ```
   This warning is normal on macOS when building locally due to different SSL library versions
   between the build environment and system. It doesn't affect the functionality of the built binary
   and can be safely ignored.

6. Comprehensive test failures
   ```bash
   ./scripts/local-test-build.sh --comprehensive-test
   ls -la .build/ tests/test_comprehensive.py
   ```

7. Clean fails on nested Poetry cache
   ```bash
   chmod -R u+w .build 2>/dev/null
   ./scripts/local-test-build.sh --clean
   ```

### Debug Mode

If you encounter issues, you can inspect the build environment:

```bash
# Check what's in the build directory
ls -la .build/

# Check the standalone interpreter
.build/python/bin/python3 --version

# Check setuptools installation
.build/python/bin/pip show setuptools

# Check Poetry installation
.build/python/bin/poetry --version

# Check PyInstaller installation
.build/python/bin/poetry run pyinstaller --version

# Run comprehensive tests manually
.build/python/bin/poetry run pytest tests/test_comprehensive.py -v --tb=long
```

## Cleanup

### Manual Cleanup
```bash
# Remove build directories
rm -rf .build/ test-build/ .pytest_cache/

# Or use the script
./scripts/local-test-build.sh --clean
```

### What Gets Cleaned
- `.build/` - Complete ephemeral environment
- `test-build/` - Build output and artifacts
- `.pytest_cache/` - Pytest cache (when using `--clean`)
- `dist/` - Legacy build output (if exists)
- `build/` - Legacy build artifacts (if exists)

## Best Practices

### For Developers
1. Always run from project root: The script expects `pyproject.toml` in the current directory
2. Use clean builds: Run `--clean` when switching branches, changing Python pins, or after major dependency changes
3. Test the binary: Always verify `./test-build/csv2notion_neo --help` works after building
4. Keep dependencies updated: Use `--show-outdated` to check for updates; prefer `--lock-only --update <pkg>` for targeted bumps
5. Run comprehensive tests before releases: `./scripts/local-test-build.sh --comprehensive-test`

### For CI/CD
1. Use matching env pins: Align workflow variables with the script configuration (see Version Alignment)
2. Clean before build: Run `--clean` in CI when you need a fully fresh environment
3. Test the output: Verify the built binary in your target environment
4. Comprehensive tests in CI: Use `--comprehensive-test` for fast validation without Notion credentials

## Script Configuration

### Script configuration variables

Pinned at the top of `scripts/local-test-build.sh`:

```bash
BUILD_DIR=".build"
TEST_BUILD_DIR="test-build"
PYTHON_STANDALONE_VERSION="3.14.5"   # macOS standalone CPython (python-build-standalone)
PYTHON_STANDALONE_RELEASE_TAG="20260510"
PIP_VERSION="26.1.2"
POETRY_VERSION="2.4.1"
SETUPTOOLS_VERSION="82.0.1"
POETRY_PLUGIN_EXPORT_VERSION="1.10.0"
PROJECT_NAME="csv2notion_neo"
```

### Customization

To modify the script behavior, edit the configuration section at the top of `local-test-build.sh`.

## Support

### Getting Help
```bash
# Show script help
./scripts/local-test-build.sh --help

# Check script configuration
head -30 scripts/local-test-build.sh
```

### Reporting Issues

If you encounter issues with the build script:
1. Run `./scripts/local-test-build.sh --clean`
2. Try a fresh build
3. Check the prerequisites
4. Review the troubleshooting section above

## Security Notes

- The script only downloads and installs packages from trusted sources (PyPI, python-build-standalone, Poetry)
- All dependencies are installed in isolated environments under `.build/`
- No system-wide installations or modifications are made
- The build environment is completely ephemeral and can be safely deleted
- Version pinning ensures reproducible builds across environments

## Version Alignment

This build script pins the local macOS toolchain as follows:

- **Python**: standalone **3.14.5** locally; CI should use **3.14** via `actions/setup-python`
- **pip**: **26.1.2** (local bootstrap)
- **Poetry**: **2.4.1**
- **Setuptools**: **82.0.1**
- **poetry-plugin-export**: **1.10.0**
- **PyInstaller**: latest (installed in the Poetry venv during build)

Update `.github/workflows/build.yml` and related workflows so `env` blocks use the same Poetry, setuptools, and export-plugin versions when you roll out Python 3.14 in CI.

---

Note: This script is designed to be completely self-contained and safe to run. It will not modify your system Python installation or install any packages globally.

---

# Docker Run Script

## Overview

The `docker-run.sh` script provides a convenient way to set up and run CSV2Notion Neo in a Docker container environment.

## Quick Start

```bash
# From the project root directory
./scripts/docker-run.sh
```

This will:
1. Build the Docker image using Docker Buildx
2. Create and start a container with the project mounted
3. Set up SSH access on port 2222

## Container Details

- Base Image: Python 3.11-slim
- Package Manager: Poetry
- Memory Limit: 512MB
- CPU Limit: 1.0 cores
- Port: 2222 (SSH)
- Volume Mount: Current directory mounted to `/app`

## Container Access

The container runs in detached mode with SSH access on port 2222:

```bash
ssh -p 2222 root@localhost
```

## Alternative Usage

You can also run the Docker setup directly:

```bash
# From the docker directory
cd docker
./install_from_docker.sh
```

## Prerequisites

- Docker and Docker Buildx installed
- SSH client (for container access)

For more detailed information, see the [Docker README](../docker/README.md).
