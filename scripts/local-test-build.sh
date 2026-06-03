#!/bin/bash

# CSV2Notion Neo - Ephemeral Build Script for macOS
# This script creates a completely self-contained build environment in .build/
# No system-level Python, pip, Poetry, or project dependencies are installed.
# Only pre-existing macOS tools are used to download/extract (curl, tar).

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (local macOS toolchain; align GitHub Actions env when CI is updated)
BUILD_DIR=".build"
TEST_BUILD_DIR="test-build"
PYTHON_VERSION="3.14"
# Pinned python-build-standalone release (see https://github.com/astral-sh/python-build-standalone/releases)
PYTHON_STANDALONE_RELEASE_TAG="20260510"
PYTHON_STANDALONE_VERSION="3.14.5"
PIP_VERSION="26.1.2"
POETRY_VERSION="2.4.1"
SETUPTOOLS_VERSION="82.0.1"
POETRY_PLUGIN_EXPORT_VERSION="1.10.0"
PROJECT_NAME="csv2notion_neo"
STANDALONE_MARKER_FILE=".standalone-installed"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Resolve project root (script must be run from repo root; verified below)
get_project_root() {
    pwd
}

# macOS triplet for python-build-standalone artifacts
detect_standalone_triplet() {
    local arch
    arch="$(uname -m)"
    case "$arch" in
        arm64|aarch64)
            echo "aarch64-apple-darwin"
            ;;
        x86_64)
            echo "x86_64-apple-darwin"
            ;;
        *)
            print_error "Unsupported macOS architecture: $arch"
            exit 1
            ;;
    esac
}

# Download URL for the pinned standalone CPython build
get_standalone_download_url() {
    local triplet="$1"
    local asset="cpython-${PYTHON_STANDALONE_VERSION}+${PYTHON_STANDALONE_RELEASE_TAG}-${triplet}-install_only.tar.gz"
    printf '%s\n' \
        "https://github.com/astral-sh/python-build-standalone/releases/download/${PYTHON_STANDALONE_RELEASE_TAG}/${asset//+/%2B}"
}

# Path to the standalone interpreter inside .build/python/
get_build_python_bin() {
    local python_dir
    python_dir="$(get_project_root)/$BUILD_DIR/python"
    local candidate
    for candidate in python3 \
        "python${PYTHON_STANDALONE_VERSION}" \
        python3.14 python3.13 python3.12 python3.11 python3.10 python3.9; do
        if [ -x "$python_dir/bin/$candidate" ]; then
            echo "$python_dir/bin/$candidate"
            return 0
        fi
    done
    return 1
}

# Keep Poetry, pip, and caches entirely under .build/
setup_build_environment_exports() {
    local root
    root="$(get_project_root)"
    export PATH="$root/$BUILD_DIR/python/bin:$PATH"
    export POETRY_HOME="$root/$BUILD_DIR/poetry-home"
    export POETRY_CONFIG_DIR="$root/$BUILD_DIR/poetry-config"
    export POETRY_CACHE_DIR="$root/$BUILD_DIR/cache"
    export PIP_CACHE_DIR="$root/$BUILD_DIR/pip-cache"
    export PYTHONNOUSERSITE=1
    mkdir -p "$POETRY_HOME" "$POETRY_CONFIG_DIR" "$POETRY_CACHE_DIR" "$PIP_CACHE_DIR"
}

# Check for host tools used only to download/extract (nothing is installed system-wide)
check_requirements() {
    print_status "Checking host tools (download/extract only)..."

    local missing_tools=()

    if ! command_exists curl; then
        missing_tools+=("curl")
    fi

    if ! command_exists tar; then
        missing_tools+=("tar")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required host tools: ${missing_tools[*]}"
        print_error "These must exist on macOS to fetch Python into $BUILD_DIR/ only."
        print_error "They do not install Python or project dependencies system-wide."
        exit 1
    fi

    print_success "Host tools available (curl, tar)"
}

# Install standalone CPython under .build/python/ (python-build-standalone)
setup_python() {
    local root python_dir marker expected_marker python_bin triplet url tarball
    root="$(get_project_root)"
    python_dir="$root/$BUILD_DIR/python"
    marker="$python_dir/$STANDALONE_MARKER_FILE"
    expected_marker="${PYTHON_STANDALONE_VERSION}+${PYTHON_STANDALONE_RELEASE_TAG}"
    python_bin="$(get_build_python_bin || true)"

    if [ -f "$marker" ] && [ "$(cat "$marker")" = "$expected_marker" ] && [ -n "$python_bin" ]; then
        print_status "Standalone Python already installed in $BUILD_DIR/python"
        print_status "Python version: $("$python_bin" --version 2>&1)"
        return 0
    fi

    print_status "Installing standalone Python ${PYTHON_STANDALONE_VERSION} into $BUILD_DIR/python..."
    triplet="$(detect_standalone_triplet)"
    url="$(get_standalone_download_url "$triplet")"
    mkdir -p "$root/$BUILD_DIR/downloads"
    tarball="$root/$BUILD_DIR/downloads/cpython-${PYTHON_STANDALONE_VERSION}-${triplet}-install_only.tar.gz"

    print_status "Downloading from python-build-standalone (${triplet})..."
    if ! curl -fsSL "$url" -o "$tarball"; then
        print_error "Failed to download standalone Python"
        print_error "URL: $url"
        exit 1
    fi

    rm -rf "$python_dir"
    mkdir -p "$root/$BUILD_DIR"
    if ! tar -xzf "$tarball" -C "$root/$BUILD_DIR"; then
        print_error "Failed to extract standalone Python into $BUILD_DIR/"
        exit 1
    fi

    python_bin="$(get_build_python_bin || true)"
    if [ -z "$python_bin" ]; then
        print_error "Standalone Python extraction failed: no interpreter in $BUILD_DIR/python/bin"
        exit 1
    fi

    echo "$expected_marker" > "$marker"
    print_status "Python version: $("$python_bin" --version 2>&1)"
    print_success "Standalone Python installed under $BUILD_DIR/python"
}

# Function to install pinned pip (matches PIP_VERSION)
update_pip() {
    local python_bin pip_version
    python_bin="$(get_build_python_bin)"

    print_status "Installing pip $PIP_VERSION in $BUILD_DIR/python..."

    if ! "$python_bin" -m pip install "pip==$PIP_VERSION"; then
        print_error "pip installation failed"
        exit 1
    fi

    pip_version=$("$python_bin" -m pip --version 2>&1 | cut -d' ' -f2)
    print_success "pip installed (version $pip_version)"
}

# Function to install setuptools
install_setuptools() {
    local python_bin
    python_bin="$(get_build_python_bin)"

    update_pip

    print_status "Installing setuptools $SETUPTOOLS_VERSION into $BUILD_DIR/python..."

    if ! "$python_bin" -m pip install "setuptools==$SETUPTOOLS_VERSION"; then
        print_error "setuptools installation failed"
        exit 1
    fi

    print_success "setuptools installed successfully"
}

# Function to setup Poetry
setup_poetry() {
    local root poetry_bin python_bin installed_version
    root="$(get_project_root)"
    poetry_bin="$root/$BUILD_DIR/python/bin/poetry"
    python_bin="$(get_build_python_bin)"

    if [ -f "$poetry_bin" ]; then
        installed_version=$("$poetry_bin" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if [ "$installed_version" = "$POETRY_VERSION" ]; then
            print_status "Poetry $POETRY_VERSION already installed in $BUILD_DIR/python"
            return 0
        fi
        print_status "Poetry $installed_version found; installing $POETRY_VERSION..."
    else
        print_status "Installing Poetry $POETRY_VERSION into $BUILD_DIR/python..."
    fi

    if ! "$python_bin" -m pip install "poetry==$POETRY_VERSION"; then
        print_error "Poetry installation failed"
        exit 1
    fi

    if [ ! -f "$poetry_bin" ]; then
        print_error "Poetry installation failed - binary not found"
        exit 1
    fi

    print_success "Poetry installed successfully"
}

# Function to configure Poetry
configure_poetry() {
    local root poetry_bin venv_path
    root="$(get_project_root)"
    poetry_bin="$root/$BUILD_DIR/python/bin/poetry"
    venv_path="$root/$BUILD_DIR/venv"

    print_status "Configuring Poetry (all paths under $BUILD_DIR/)..."

    mkdir -p "$venv_path"

    "$poetry_bin" config virtualenvs.create true
    "$poetry_bin" config virtualenvs.in-project false
    "$poetry_bin" config virtualenvs.path "$venv_path"
    "$poetry_bin" config cache-dir "$root/$BUILD_DIR/cache"

    print_success "Poetry configured for local development"
}

# Function to install poetry-plugin-export (matches GitHub Actions build.yml)
install_poetry_plugin_export() {
    local poetry_bin
    poetry_bin="$(get_project_root)/$BUILD_DIR/python/bin/poetry"
    print_status "Installing poetry-plugin-export $POETRY_PLUGIN_EXPORT_VERSION..."
    if ! "$poetry_bin" self add "poetry-plugin-export==$POETRY_PLUGIN_EXPORT_VERSION"; then
        print_error "poetry-plugin-export installation failed"
        exit 1
    fi
    print_success "poetry-plugin-export installed successfully"
}

# Function to install dependencies
install_dependencies() {
    local poetry_bin
    poetry_bin="$(get_project_root)/$BUILD_DIR/python/bin/poetry"
    local update_flag="$1"
    local packages="$2"

    print_status "Installing project dependencies..."

    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Are you in the CSV2Notion Neo project directory?"
        exit 1
    fi

    if [ "$update_flag" = "--update-lock" ]; then
        print_status "Updating Poetry lock file..."
        if ! "$poetry_bin" lock; then
            print_error "Failed to update lock file"
            exit 1
        fi
        print_success "Lock file updated"
    elif [ "$update_flag" = "--update-deps" ]; then
        if [ -n "$packages" ]; then
            print_status "Updating specific dependencies: $packages"
            if ! "$poetry_bin" update $packages; then
                print_error "Failed to update dependencies: $packages"
                exit 1
            fi
        else
            print_status "Updating all dependencies to latest versions..."
            if ! "$poetry_bin" update; then
                print_error "Failed to update all dependencies"
                exit 1
            fi
        fi
        print_success "Dependencies updated to latest versions"
    elif [ "$update_flag" = "--update-selective" ]; then
        print_status "Updating specific dependencies: $packages"
        if ! "$poetry_bin" update $packages; then
            print_error "Failed to update selected dependencies"
            exit 1
        fi
        print_success "Selected dependencies updated"
    else
        if ! "$poetry_bin" install; then
            print_error "Failed to install dependencies"
            exit 1
        fi
    fi

    print_success "Dependencies installed successfully"
}

# Function to build the application
build_application() {
    local poetry_bin
    poetry_bin="$(get_project_root)/$BUILD_DIR/python/bin/poetry"

    print_status "Building CSV2Notion Neo application..."

    rm -rf "$TEST_BUILD_DIR"/ dist/ build/

    if [ ! -f "csv2notion_neo.spec" ]; then
        print_error "csv2notion_neo.spec not found. Cannot build binary."
        exit 1
    fi

    if ! "$poetry_bin" run python -m PyInstaller --distpath "$TEST_BUILD_DIR" --workpath "$TEST_BUILD_DIR/build" csv2notion_neo.spec; then
        print_error "Build failed during PyInstaller execution"
        exit 1
    fi

    if [ -f "$TEST_BUILD_DIR/csv2notion_neo" ]; then
        print_success "Build completed successfully!"
        print_success "Binary created: $TEST_BUILD_DIR/csv2notion_neo"

        chmod +x "$TEST_BUILD_DIR/csv2notion_neo"

        ls -la "$TEST_BUILD_DIR/csv2notion_neo"
        print_status "Binary size: $(du -h "$TEST_BUILD_DIR/csv2notion_neo" | cut -f1)"
    else
        print_error "Build failed - binary not found in $TEST_BUILD_DIR/"
        exit 1
    fi
}

# Function to run tests (optional)
run_tests() {
    local poetry_bin
    poetry_bin="$(get_project_root)/$BUILD_DIR/python/bin/poetry"

    if [ "$1" = "--test" ]; then
        print_status "Running tests..."
        if ! "$poetry_bin" run python -m pytest tests/ -v -p no:vcr; then
            print_warning "Tests failed, but continuing..."
        fi
    fi
}

# Function to show outdated packages
show_outdated() {
    local poetry_bin
    poetry_bin="$(get_project_root)/$BUILD_DIR/python/bin/poetry"

    print_status "Checking for outdated packages..."

    check_requirements
    mkdir -p "$BUILD_DIR"
    setup_build_environment_exports
    setup_python
    install_setuptools
    setup_poetry
    configure_poetry
    install_poetry_plugin_export

    if ! "$poetry_bin" install; then
        print_error "Failed to install dependencies for outdated check"
        exit 1
    fi

    "$poetry_bin" show --outdated

    exit 0
}

# Function to clean build directory
clean_build() {
    if [ "$1" = "--clean" ]; then
        print_status "Cleaning build directory, test output, and pytest cache..."
        if [ -d "$BUILD_DIR" ]; then
            chmod -R u+w "$BUILD_DIR" 2>/dev/null || true
            find "$BUILD_DIR" -name '.DS_Store' -delete 2>/dev/null || true
            rm -rf "$BUILD_DIR"
        fi
        rm -rf "$TEST_BUILD_DIR" dist/ build/
        rm -rf ".pytest_cache"
        print_success "Removed $BUILD_DIR/, $TEST_BUILD_DIR/, and .pytest_cache/"
        exit 0
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [PACKAGES...]"
    echo ""
    echo "Options:"
    echo "  --clean                Clean .build/, test-build/, .pytest_cache/ and exit"
    echo "  --test                 Run tests after building"
    echo "  --comprehensive-test   Run comprehensive test suite"
    echo "  --update-lock          Update poetry.lock file before building"
    echo "  --update-deps          Update dependencies to latest versions and rebuild lock file"
    echo "  --update               Update specific packages (provide package names as arguments)"
    echo "  --lock-only            Only update lock file without building"
    echo "  --show-outdated        Show outdated packages"
    echo "  --help                 Show this help message"
    echo ""
    echo "This script creates an ephemeral build environment for CSV2Notion Neo."
    echo "Standalone Python, Poetry, pip, caches, and deps live only under .build/."
    echo "Nothing is installed system-wide. Delete .build/ to remove the environment."
    echo ""
    echo "Pinned toolchain (matches Airlift local build):"
    echo "  Python: ${PYTHON_STANDALONE_VERSION} (${PYTHON_STANDALONE_RELEASE_TAG})"
    echo "  pip: ${PIP_VERSION}  |  Poetry: ${POETRY_VERSION}  |  setuptools: ${SETUPTOOLS_VERSION}"
    echo ""
    echo "Comprehensive Testing:"
    echo "  Validates CLI arguments and Notion SDK behavior without live API credentials."
    echo "  If .build/ is missing, the environment is created automatically."
    echo ""
    echo "Examples:"
    echo "  $0                           # Normal build"
    echo "  $0 --comprehensive-test      # Run comprehensive tests"
    echo "  $0 --update-lock             # Update lock file then build"
    echo "  $0 --update-deps             # Update all deps to latest versions then build"
    echo "  $0 --update requests pytest  # Update only requests and pytest packages"
    echo "  $0 --lock-only --update requests # Update requests and regenerate lock file only"
    echo "  $0 --show-outdated           # Show which packages can be updated"
    echo "  $0 --clean                   # Clean build directory"
}

# Function to install PyInstaller if needed
install_pyinstaller() {
    local poetry_bin
    poetry_bin="$(get_project_root)/$BUILD_DIR/python/bin/poetry"

    print_status "Installing PyInstaller for building..."

    if ! "$poetry_bin" run pip install pyinstaller; then
        print_error "PyInstaller installation failed"
        exit 1
    fi

    print_success "PyInstaller installed successfully"
}

# Function to run comprehensive tests
run_comprehensive_tests() {
    local poetry_bin
    poetry_bin="$(get_project_root)/$BUILD_DIR/python/bin/poetry"

    print_status "Running comprehensive test suite..."

    if [ ! -f "tests/test_comprehensive.py" ]; then
        print_error "Comprehensive test file not found: tests/test_comprehensive.py"
        exit 1
    fi

    if ! "$poetry_bin" run pytest tests/test_comprehensive.py -v --tb=long -p no:vcr; then
        print_error "Comprehensive tests failed"
        exit 1
    fi

    print_success "Comprehensive tests completed successfully!"
}

# Function to check if build environment exists
check_build_environment() {
    local root poetry_bin marker expected_marker
    root="$(get_project_root)"
    poetry_bin="$root/$BUILD_DIR/python/bin/poetry"
    marker="$root/$BUILD_DIR/python/$STANDALONE_MARKER_FILE"
    expected_marker="${PYTHON_STANDALONE_VERSION}+${PYTHON_STANDALONE_RELEASE_TAG}"

    if [ ! -f "$marker" ] || [ "$(cat "$marker")" != "$expected_marker" ]; then
        print_status "Standalone Python not ready in $BUILD_DIR/. Setting up first..."
        return 1
    fi

    if ! get_build_python_bin >/dev/null; then
        print_status "Python interpreter missing in $BUILD_DIR/python/. Setting up first..."
        return 1
    fi

    if [ ! -f "$poetry_bin" ]; then
        print_status "Poetry not found in $BUILD_DIR/. Setting up first..."
        return 1
    fi

    if [ ! -d "$root/$BUILD_DIR/venv" ]; then
        print_status "Poetry virtualenv not found in $BUILD_DIR/venv. Setting up first..."
        return 1
    fi

    if ! "$poetry_bin" run python -c "import pytest" >/dev/null 2>&1; then
        print_status "Project dependencies not installed in $BUILD_DIR/venv. Setting up first..."
        return 1
    fi

    return 0
}

# Main execution
main() {
    local UPDATE_FLAG=""
    local TEST_FLAG=""
    local LOCK_ONLY=false
    local PACKAGES=""
    local COMPREHENSIVE_TEST=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                clean_build "$1"
                ;;
            --test)
                TEST_FLAG="--test"
                shift
                ;;
            --comprehensive-test)
                COMPREHENSIVE_TEST="comprehensive"
                shift
                ;;
            --update-lock)
                UPDATE_FLAG="--update-lock"
                shift
                ;;
            --update-deps)
                UPDATE_FLAG="--update-deps"
                shift
                ;;
            --update)
                UPDATE_FLAG="--update-selective"
                shift
                while [[ $# -gt 0 ]] && [[ ! $1 =~ ^-- ]]; do
                    if [ -z "$PACKAGES" ]; then
                        PACKAGES="$1"
                    else
                        PACKAGES="$PACKAGES $1"
                    fi
                    shift
                done
                ;;
            --lock-only)
                LOCK_ONLY=true
                shift
                ;;
            --show-outdated)
                show_outdated
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    if [ -n "$COMPREHENSIVE_TEST" ]; then
        print_status "Comprehensive test mode"

        if ! check_build_environment; then
            print_status "Setting up build environment first..."

            check_requirements
            mkdir -p "$BUILD_DIR"
            setup_build_environment_exports
            setup_python
            install_setuptools
            setup_poetry
            configure_poetry
            install_poetry_plugin_export

            install_dependencies "$UPDATE_FLAG" "$PACKAGES"
        else
            print_status "Using existing build environment"
            setup_build_environment_exports
            install_poetry_plugin_export
        fi

        install_dependencies "$UPDATE_FLAG" "$PACKAGES"

        run_comprehensive_tests
        exit 0
    fi

    if [ "$UPDATE_FLAG" = "--update-selective" ] && [ -z "$PACKAGES" ]; then
        print_error "No packages specified for selective update"
        print_status "Use: $0 --update package1 package2 ..."
        exit 1
    fi

    print_status "Starting CSV2Notion Neo build process..."
    print_status "Build directory: $BUILD_DIR"

    check_requirements
    mkdir -p "$BUILD_DIR"
    setup_build_environment_exports
    setup_python
    install_setuptools
    setup_poetry
    configure_poetry
    install_poetry_plugin_export

    if [ "$LOCK_ONLY" = true ]; then
        print_status "Lock-only mode: updating lock file..."
        local poetry_bin
        poetry_bin="$(get_project_root)/$BUILD_DIR/python/bin/poetry"

        if [ "$UPDATE_FLAG" = "--update-deps" ]; then
            print_status "Updating all dependencies to latest versions..."
            if ! "$poetry_bin" update; then
                print_error "Failed to update all dependencies"
                exit 1
            fi
        elif [ "$UPDATE_FLAG" = "--update-selective" ]; then
            print_status "Updating specific dependencies: $PACKAGES"
            if ! "$poetry_bin" update $PACKAGES; then
                print_error "Failed to update selected dependencies"
                exit 1
            fi
        else
            print_status "Updating lock file..."
            if ! "$poetry_bin" lock; then
                print_error "Failed to update lock file"
                exit 1
            fi
        fi

        print_success "Lock file updated successfully!"
        exit 0
    fi

    install_dependencies "$UPDATE_FLAG" "$PACKAGES"
    install_pyinstaller
    build_application

    run_tests "$TEST_FLAG"

    print_success "Build process completed!"
    print_status "To run the application: ./$TEST_BUILD_DIR/csv2notion_neo"
    print_status "To clean build files: $0 --clean"
    print_status "Build artifacts are in: $TEST_BUILD_DIR/"
}

if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the CSV2Notion Neo project root directory"
    exit 1
fi

main "$@"
