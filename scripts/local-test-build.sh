#!/bin/bash

# CSV2Notion Neo - Ephemeral Build Script for macOS
# This script creates a completely self-contained build environment in .build/
# No system-level installations required

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BUILD_DIR=".build"
TEST_BUILD_DIR="test-build"
PYTHON_VERSION="3.9"
POETRY_VERSION="2.1.3"
SETUPTOOLS_VERSION="80.9.0"
PROJECT_NAME="csv2notion_neo"

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

# Check if required tools are available
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check for required tools
    local missing_tools=()
    
    if ! command_exists curl; then
        missing_tools+=("curl")
    fi
    
    if ! command_exists xar; then
        missing_tools+=("xar")
    fi
    
    if ! command_exists cpio; then
        missing_tools+=("cpio")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_error "Please install these tools first. On macOS, xar and cpio are usually pre-installed."
        print_error "You can install curl with: brew install curl"
        exit 1
    fi
    
    print_success "All required tools are available"
}

# Function to setup Python (using system Python with virtual environment)
setup_python() {
    local python_dir="$BUILD_DIR/python"
    local python_bin="$python_dir/bin/python3"
    
    if [ -f "$python_bin" ]; then
        print_status "Python virtual environment already exists in $python_dir"
        return 0
    fi
    
    print_status "Setting up Python virtual environment in $python_dir..."
    
    # Check if system Python is available
    if ! command_exists python3; then
        print_error "System Python 3 is not available. Please install Python 3 first."
        print_error "You can install it with: brew install python"
        exit 1
    fi
    
    # Get system Python version
    local system_python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "Using system Python: $system_python_version"
    
    # Check if Python version is compatible (3.9 or higher)
    local major_version=$(echo "$system_python_version" | cut -d'.' -f1)
    local minor_version=$(echo "$system_python_version" | cut -d'.' -f2)
    
    if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 9 ]); then
        print_error "Python 3.9 or higher is required. Current version: $system_python_version"
        print_error "Please upgrade Python to version 3.9 or higher."
        exit 1
    fi
    
    # Create virtual environment using system Python
    if ! python3 -m venv "$python_dir"; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    # Verify installation
    if [ -f "$python_bin" ]; then
        print_status "Python version: $($python_bin --version)"
        print_success "Python virtual environment created successfully"
    else
        print_error "Python virtual environment creation failed"
        exit 1
    fi
}

# Function to install setuptools
install_setuptools() {
    local pip_bin="$BUILD_DIR/python/bin/pip"
    
    print_status "Installing setuptools $SETUPTOOLS_VERSION..."
    
    # Install setuptools using pip in our virtual environment
    if ! "$pip_bin" install "setuptools==$SETUPTOOLS_VERSION"; then
        print_error "setuptools installation failed"
        exit 1
    fi
    
    print_success "setuptools installed successfully"
}

# Function to setup Poetry
setup_poetry() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    local python_bin="$BUILD_DIR/python/bin/python3"
    local pip_bin="$BUILD_DIR/python/bin/pip"
    
    if [ -f "$poetry_bin" ]; then
        print_status "Poetry already installed in virtual environment"
        return 0
    fi
    
    print_status "Installing Poetry $POETRY_VERSION in virtual environment..."
    
    # Set PATH to use our virtual environment
    export PATH="$(pwd)/$BUILD_DIR/python/bin:$PATH"
    
    # Install Poetry using pip in our virtual environment
    if ! "$pip_bin" install "poetry==$POETRY_VERSION"; then
        print_error "Poetry installation failed"
        exit 1
    fi
    
    # Verify installation
    if [ ! -f "$poetry_bin" ]; then
        print_error "Poetry installation failed - binary not found"
        exit 1
    fi
    
    print_success "Poetry installed successfully"
}

# Function to configure Poetry
configure_poetry() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    local venv_path="$BUILD_DIR/venv"
    local cache_dir="$BUILD_DIR/cache"
    
    print_status "Configuring Poetry..."
    
    # Create directories
    mkdir -p "$venv_path" "$cache_dir"
    
    # Configure Poetry to use local directories
    $poetry_bin config virtualenvs.create true
    $poetry_bin config virtualenvs.in-project false
    $poetry_bin config virtualenvs.path "$venv_path"
    $poetry_bin config cache-dir "$cache_dir"
    
    print_success "Poetry configured for local development"
}

# Function to install dependencies
install_dependencies() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    local update_flag="$1"
    local packages="$2"
    
    print_status "Installing project dependencies..."
    
    # Check if pyproject.toml exists
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Are you in the CSV2Notion Neo project directory?"
        exit 1
    fi
    
    # Check if we should update lock file first
    if [ "$update_flag" = "--update-lock" ]; then
        print_status "Updating Poetry lock file..."
        if ! $poetry_bin lock; then
            print_error "Failed to update lock file"
            exit 1
        fi
        print_success "Lock file updated"
    elif [ "$update_flag" = "--update-deps" ]; then
        if [ -n "$packages" ]; then
            print_status "Updating specific dependencies: $packages"
            if ! $poetry_bin update $packages; then
                print_error "Failed to update dependencies: $packages"
                exit 1
            fi
        else
            print_status "Updating all dependencies to latest versions..."
            if ! $poetry_bin update; then
                print_error "Failed to update all dependencies"
                exit 1
            fi
        fi
        print_success "Dependencies updated to latest versions"
    elif [ "$update_flag" = "--update-selective" ]; then
        print_status "Updating specific dependencies: $packages"
        if ! $poetry_bin update $packages; then
            print_error "Failed to update selected dependencies"
            exit 1
        fi
        print_success "Selected dependencies updated"
    else
        # Standard install from existing lock file
        if ! $poetry_bin install; then
            print_error "Failed to install dependencies"
            exit 1
        fi
    fi
    
    print_success "Dependencies installed successfully"
}

# Function to build the application
build_application() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    
    print_status "Building CSV2Notion Neo application..."
    
    # Clean previous builds
    rm -rf "$TEST_BUILD_DIR"/ dist/ build/
    
    # Check if csv2notion_neo.spec exists
    if [ ! -f "csv2notion_neo.spec" ]; then
        print_error "csv2notion_neo.spec not found. Cannot build binary."
        exit 1
    fi
    
    # Build the binary using PyInstaller
    if ! $poetry_bin run python -m PyInstaller --distpath "$TEST_BUILD_DIR" --workpath "$TEST_BUILD_DIR/build" csv2notion_neo.spec; then
        print_error "Build failed during PyInstaller execution"
        exit 1
    fi
    
    # Check if build was successful
    if [ -f "$TEST_BUILD_DIR/csv2notion_neo" ]; then
        print_success "Build completed successfully!"
        print_success "Binary created: $TEST_BUILD_DIR/csv2notion_neo"
        
        # Make binary executable
        chmod +x "$TEST_BUILD_DIR/csv2notion_neo"
        
        # Show binary info
        ls -la "$TEST_BUILD_DIR/csv2notion_neo"
        print_status "Binary size: $(du -h "$TEST_BUILD_DIR/csv2notion_neo" | cut -f1)"
    else
        print_error "Build failed - binary not found in $TEST_BUILD_DIR/"
        exit 1
    fi
}

# Function to run tests (optional)
run_tests() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    
    if [ "$1" = "--test" ]; then
        print_status "Running tests..."
        if ! $poetry_bin run python -m pytest tests/ -v; then
            print_warning "Tests failed, but continuing..."
        fi
    fi
}

# Function to show outdated packages
show_outdated() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    
    print_status "Checking for outdated packages..."
    
    # Setup environment first
    check_requirements
    setup_python
    install_setuptools
    setup_poetry
    configure_poetry
    
    # Set environment variable to prevent pytest cache creation
    export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
    
    # Install current dependencies first
    if ! $poetry_bin install; then
        print_error "Failed to install dependencies for outdated check"
        exit 1
    fi
    
    # Show outdated packages
    $poetry_bin show --outdated
    
    # Clean up any pytest cache that might have been created
    if [ -d ".pytest_cache" ]; then
        rm -rf .pytest_cache
        print_status "Cleaned up pytest cache directory"
    fi
    
    exit 0
}

# Function to clean build directory
clean_build() {
    if [ "$1" = "--clean" ]; then
        print_status "Cleaning build directory..."
        rm -rf "$BUILD_DIR"
        rm -rf "$TEST_BUILD_DIR"/ dist/ build/
        print_success "Build directory cleaned"
        exit 0
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [PACKAGES...]"
    echo ""
    echo "Options:"
    echo "  --clean                Clean build directory and exit"
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
    echo "Everything is installed in the .build/ directory and can be safely deleted."
    echo ""
    echo "Comprehensive Testing:"
    echo "  The comprehensive test suite validates all CLI arguments, flags, and switches"
    echo "  without requiring actual Notion API calls. If .build/ doesn't exist, it will"
    echo "  automatically set up the build environment first."
    echo ""
    echo "Examples:"
    echo "  $0                          # Normal build"
    echo "  $0 --comprehensive-test     # Run comprehensive tests"
    echo "  $0 --update-lock            # Update lock file then build"
    echo "  $0 --update-deps            # Update all deps to latest versions then build"
    echo "  $0 --update requests pytest # Update only requests and pytest packages"
    echo "  $0 --lock-only --update requests # Update requests and regenerate lock file only"
    echo "  $0 --show-outdated          # Show which packages can be updated"
    echo "  $0 --clean                  # Clean build directory"
}

# Function to install PyInstaller if needed
install_pyinstaller() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    
    print_status "Installing PyInstaller for building..."
    
    # Install PyInstaller in the Poetry virtual environment
    if ! $poetry_bin run pip install pyinstaller; then
        print_error "PyInstaller installation failed"
        exit 1
    fi
    
    print_success "PyInstaller installed successfully"
}

# Function to run comprehensive tests
run_comprehensive_tests() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    
    print_status "Running comprehensive test suite..."
    
    # Check if test file exists
    if [ ! -f "tests/test_comprehensive.py" ]; then
        print_error "Comprehensive test file not found: tests/test_comprehensive.py"
        exit 1
    fi
    
    # Set up PATH for our portable Python
    export PATH="$(pwd)/$BUILD_DIR/python/bin:$PATH"
    
    # Run the comprehensive test
    print_status "Running comprehensive test suite..."
    if ! $poetry_bin run pytest tests/test_comprehensive.py -v --tb=long; then
        print_error "Comprehensive tests failed"
        exit 1
    fi
    
    print_success "Comprehensive tests completed successfully!"
}

# Function to check if build environment exists
check_build_environment() {
    local poetry_bin="$BUILD_DIR/python/bin/poetry"
    
    if [ ! -f "$poetry_bin" ]; then
        print_status "Build environment not found. Setting up build environment first..."
        return 1
    fi
    
    # Check if Poetry virtual environment exists
    if [ ! -d "$BUILD_DIR/venv" ]; then
        print_status "Poetry virtual environment not found. Setting up build environment first..."
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
    
    # Parse command line arguments
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
                # Collect package names
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
    
    # Handle comprehensive test options
    if [ -n "$COMPREHENSIVE_TEST" ]; then
        print_status "Comprehensive test mode"
        
        # Check if build environment exists
        if ! check_build_environment; then
            print_status "Setting up build environment first..."
            
            # Check system requirements
            check_requirements
            
            # Create build directory
            mkdir -p "$BUILD_DIR"
            
            # Setup build environment
            setup_python
            install_setuptools
            setup_poetry
            configure_poetry
            
            # Install dependencies
            install_dependencies "$UPDATE_FLAG" "$PACKAGES"
        else
            print_status "Using existing build environment"
        fi
        
        # Run comprehensive tests
        run_comprehensive_tests
        exit 0
    fi
    
    # Validate selective update
    if [ "$UPDATE_FLAG" = "--update-selective" ] && [ -z "$PACKAGES" ]; then
        print_error "No packages specified for selective update"
        print_status "Use: $0 --update package1 package2 ..."
        exit 1
    fi
    
    print_status "Starting CSV2Notion Neo build process..."
    print_status "Build directory: $BUILD_DIR"
    
    # Check system requirements
    check_requirements
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    
    # Setup build environment
    setup_python
    install_setuptools
    setup_poetry
    configure_poetry
    
    # Handle lock-only mode
    if [ "$LOCK_ONLY" = true ]; then
        print_status "Lock-only mode: updating lock file..."
        local poetry_bin="$BUILD_DIR/python/bin/poetry"
        
        # Set up PATH for our portable Python
        export PATH="$(pwd)/$BUILD_DIR/python/bin:$PATH"
        
        if [ "$UPDATE_FLAG" = "--update-deps" ]; then
            print_status "Updating all dependencies to latest versions..."
            if ! $poetry_bin update; then
                print_error "Failed to update all dependencies"
                exit 1
            fi
        elif [ "$UPDATE_FLAG" = "--update-selective" ]; then
            print_status "Updating specific dependencies: $PACKAGES"
            if ! $poetry_bin update $PACKAGES; then
                print_error "Failed to update selected dependencies"
                exit 1
            fi
        else
            print_status "Updating lock file..."
            if ! $poetry_bin lock; then
                print_error "Failed to update lock file"
                exit 1
            fi
        fi
        
        print_success "Lock file updated successfully!"
        exit 0
    fi
    
    # Build the application
    export PATH="$(pwd)/$BUILD_DIR/python/bin:$PATH"
    install_dependencies "$UPDATE_FLAG" "$PACKAGES"
    install_pyinstaller
    build_application
    
    # Run tests if requested
    run_tests "$TEST_FLAG"
    
    print_success "Build process completed!"
    print_status "To run the application: ./$TEST_BUILD_DIR/csv2notion_neo"
    print_status "To clean build files: $0 --clean"
    print_status "Build artifacts are in: $TEST_BUILD_DIR/"
}

# Check if script is run from project root
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the CSV2Notion Neo project root directory"
    exit 1
fi

# Run main function
main "$@"