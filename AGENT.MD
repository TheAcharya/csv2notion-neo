# CSV2Notion Neo - Agent Documentation

## Table of Contents

- [Project Overview](#project-overview)
- [Version 2.0.0+ Migration](#version-200-migration)
  - [Migration Details](#migration-details)
    - [Authentication Changes](#authentication-changes)
    - [API Implementation Changes](#api-implementation-changes)
    - [Database URL Requirements](#database-url-requirements)
    - [File Upload Implementation](#file-upload-implementation)
    - [Error Handling Improvements](#error-handling-improvements)
    - [Codebase Structure Changes](#codebase-structure-changes)
- [Core Architecture](#core-architecture)
  - [Main Components](#main-components)
- [Key Features](#key-features)
  - [Data Import Capabilities](#data-import-capabilities)
  - [Advanced Operations](#advanced-operations)
  - [AI Integration](#ai-integration)
  - [Performance Features](#performance-features)
- [Development Guidelines](#development-guidelines)
  - [Code Structure](#code-structure)
  - [Local Development Workflow](#local-development-workflow)
  - [Testing Strategy](#testing-strategy)
  - [Code Quality](#code-quality)
  - [Dependencies](#dependencies)
- [API Integration](#api-integration)
  - [Notion API](#notion-api)
  - [Hugging Face API](#hugging-face-api)
- [Configuration Management](#configuration-management)
  - [Command Line Arguments](#command-line-arguments)
  - [Environment Variables](#environment-variables)
- [Error Handling](#error-handling)
  - [Custom Exceptions](#custom-exceptions)
  - [Logging Strategy](#logging-strategy)
- [Security Considerations](#security-considerations)
  - [Authentication](#authentication)
  - [Data Privacy](#data-privacy)
- [Performance Optimization](#performance-optimization)
  - [Upload Efficiency](#upload-efficiency)
  - [Memory Management](#memory-management)
- [Deployment and Distribution](#deployment-and-distribution)
  - [Packaging](#packaging)
  - [CI/CD Pipeline](#cicd-pipeline)
- [Maintenance and Updates](#maintenance-and-updates)
  - [Version Management](#version-management)
  - [API Compatibility](#api-compatibility)
- [Contributing Guidelines](#contributing-guidelines)
  - [Development Setup](#development-setup)
  - [Ephemeral Build System](#ephemeral-build-system)
  - [Code Review Process](#code-review-process)
  - [Testing Requirements](#testing-requirements)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Mode](#debug-mode)
- [Future Roadmap](#future-roadmap)
  - [Planned Features](#planned-features)
  - [Technical Debt](#technical-debt)
- [Outdated Packages Held Back Due to Dependency Constraints](#outdated-packages-held-back-due-to-dependency-constraints)

## Project Overview

CSV2Notion Neo is an advanced command-line tool for uploading and merging CSV or JSON files with images to Notion databases. It serves as a successor to the original csv2notion project, providing enhanced compatibility with Notion's evolving API and additional features like AI-powered image captioning.

## Version 2.0.0+ Migration

CSV2Notion Neo has been fully migrated to use the official [Notion API](https://developers.notion.com/) and the [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) library. This migration provides better reliability, security, and future compatibility. The application now uses Notion integration tokens instead of session cookies and requires database URLs to be provided for all operations.

### Migration Details

#### Authentication Changes
- Previous: Used `token_v2` session cookies from Notion web interface
- Current: Uses official Notion integration tokens with format validation (starts with 'secret_' or 'ntn_')
- Benefits: Enhanced security, better token management, official authentication method, improved user experience with clear error messages

#### API Implementation Changes
- Previous: Custom implementation using unofficial private Notion APIs
- Current: Official [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) library integration
- Benefits: Official API support, better error handling, future-proof compatibility

#### Database URL Requirements
- Previous: Optional database URL with automatic database creation
- Current: Mandatory database URL for all operations (supports both database URLs and page URLs)
- Benefits: Clearer workflow, explicit database targeting, better error handling, ability to create databases within existing pages

#### File Upload Implementation
- Previous: Custom file upload logic with signed URLs
- Current: Official Notion file_uploads API endpoints
- Benefits: Standardised upload process, better error handling, official support

#### Error Handling Improvements
- Previous: Custom error handling for unofficial API responses
- Current: Official API error codes and structured error responses
- Benefits: Better error messages, standardised error handling, official documentation

#### Codebase Structure Changes
- Removed: `csv2notion_neo/notion/` directory (legacy API implementation)
- Added: `csv2notion_neo/notion_client.py` (API client wrapper with comprehensive retry logic)
- Added: `csv2notion_neo/notion_db.py` (database operations with enhanced schema detection)
- Added: `csv2notion_neo/notion_row_upload_file.py` (file uploads with retry logic)
- Added: `csv2notion_neo/notion_db_client.py` (extended client with additional functionality)
- Renamed: All "_official" suffixed files to clean names without suffixes
- Enhanced: Comprehensive retry logic with 15 attempts, exponential backoff, and jitter
- Improved: Clear separation between two distinct logic paths for database operations

## Core Architecture

### Main Components

1. CLI Interface (`csv2notion_neo/cli.py`)
   - Entry point for the application
   - Handles argument parsing and logging setup
   - Orchestrates the main workflow

2. Data Processing (`csv2notion_neo/local_data.py`)
   - Reads and validates CSV/JSON files
   - Manages column types and data structure
   - Handles AI feature integration

3. Notion Integration (`csv2notion_neo/notion_client.py`, `csv2notion_neo/notion_db.py`)
   - Notion API client implementation using notion-sdk-py
   - Database and collection management with API
   - File upload and block operations through API endpoints
   - Comprehensive retry logic with 15 attempts, exponential backoff, and jitter
   - Smart error handling for different error types (server errors, rate limits, network issues)
   - Two distinct logic paths: creating new databases in pages vs uploading to existing databases

4. Conversion Engine (`csv2notion_neo/notion_convert.py`)
   - Converts CSV/JSON data to Notion format
   - Handles different column types
   - Manages image and icon processing

5. Upload System (`csv2notion_neo/notion_uploader.py`)
   - Manages row uploads to Notion
   - Handles merge operations
   - Integrates AI captioning features

## Key Features

### Data Import Capabilities
- CSV and JSON file support with comprehensive delimiter support (comma, semicolon, pipe, tab, etc.)
- Enhanced automatic column type detection with intelligent schema analysis and smart pattern recognition
- Timecode detection for video/film data (automatically set to Rich Text)
- Boolean/checkbox detection with comprehensive pattern matching
- Status/select detection for limited unique values with semantic meaning
- Numeric detection for integers, decimals, and percentages
- URL, email, and phone number pattern recognition
- Date format detection supporting multiple international formats
- Manual column type specification
- Support for all Notion column types (text, number, select, multi_select, date, checkbox, url, email, phone_number, file, person, relation, rollup, formula, created_time, last_edited_time, created_by, last_edited_by)
- Page URL support for creating databases within existing Notion pages

### Advanced Operations
- Merge existing databases using key columns
- Relation column handling with automatic linking
- File upload support for images and documents
- Icon and cover image assignment
- Mandatory column validation
- Database management: Archive all entries in a database using --delete-all-database-entries (database URL required, page URLs not supported)

### AI Integration
- Hugging Face integration for image captioning
- Support for multiple AI models (vit-gpt2, blip-image, git-large)
- Automatic caption generation for uploaded images

### Performance Features
- Multithreaded uploads for improved speed with race condition prevention
- Rate limiting to respect Notion API limits with exponential backoff
- Progress tracking with tqdm
- Thread-safe select option management to prevent conflicts during concurrent uploads
- Database creation within pages with proper initialization delays and retry logic
- Enhanced retry mechanism with 15 max retries and exponential backoff for API errors
- Robust error handling for 503 Service Unavailable, timeout, and 409 Conflict errors
- Comprehensive retry logic for file uploads, page creation, and database operations
- Enhanced error handling for concurrent operations
- Smart retry logic with jitter to prevent thundering herd problems
- Production-ready retry system handling high concurrency, large files, and rate limits
- Two distinct logic paths with optimized retry strategies for different scenarios

## Development Guidelines

### Code Structure
- Follow Python type hints throughout
- Use dataclasses for configuration objects
- Implement proper error handling with custom exceptions
- Maintain comprehensive logging

### Local Development Workflow
- Use the ephemeral build script (`scripts/local-test-build.sh`) for local development
- Creates self-contained build environment in `.build/` directory
- No system-level installations required
- Supports dependency updates and testing workflows
- Produces identical builds to CI/CD pipeline

### Testing Strategy
- Unit tests for core functionality
- Integration tests for Notion API interactions
- VCR-based testing for API responses
- Coverage reporting for quality assurance
- Local testing with ephemeral environment
- Comprehensive test suite (test_comprehensive.py) for CLI argument validation and Notion SDK testing without credentials

### Code Quality
- Black formatting with 88 character line length
- isort for import organization
- flake8 and wemake-python-styleguide for linting
- mypy for type checking
- Pre-commit hooks for automated quality checks

### Dependencies
- Python 3.9+ required
- Poetry for dependency management
- Key dependencies: notion-client (notion-sdk-py), requests, tqdm, emoji, python-dateutil, icecream

## API Integration

### Notion API
- Notion API client implementation using notion-sdk-py library
- Support for all Notion API endpoints (databases, pages, blocks, users, file uploads)
- File upload handling through file_uploads endpoints with comprehensive retry logic
- Built-in rate limiting and error handling from the SDK with exponential backoff
- Integration token authentication for enhanced security
- Full compatibility with Notion's API specifications
- Smart retry logic with 15 attempts, exponential backoff, and jitter for production reliability
- Two distinct logic paths: creating new databases in pages vs uploading to existing databases
- Enhanced error handling for different error types (server errors, rate limits, network issues)

### Hugging Face API
- Integration with Hugging Face inference API
- Support for image captioning models
- Token-based authentication
- Retry logic for model loading

## Configuration Management

### Command Line Arguments
- Workspace and integration token authentication (mandatory) with format validation
- Database URL or page URL specification (mandatory) - supports both existing databases and page URLs for creating new databases
- Column type mapping
- Image and icon handling options
- Merge and validation flags
- AI model configuration
- Database management: --delete-all-database-entries for archiving all pages in a database (database URL required, page URLs not supported)

### Environment Variables
- Notion integration tokens (starts with 'secret_' or 'ntn_')
- Hugging Face API tokens
- Test configuration for CI/CD

## Error Handling

### Custom Exceptions
- CriticalError: For fatal application errors
- NotionError: For Notion API related issues
- ValidationError: For data validation failures

### Logging Strategy
- Configurable log levels (INFO, DEBUG, WARNING)
- File-based logging support
- Structured error messages with context
- Clean, user-friendly output with verbose debugging options available

## Security Considerations

### Authentication
- Secure integration token handling for official Notion API
- Token format validation with user-friendly error messages
- Hugging Face token management
- No hardcoded credentials in source code
- Integration token validation and error handling

### Data Privacy
- Local file processing
- Secure file uploads to Notion
- AI image analysis with privacy warnings

## Performance Optimization

### Upload Efficiency
- Multithreaded processing with configurable thread count
- Batch operations where possible
- Progress tracking for large datasets

### Memory Management
- Streaming file processing for large CSV files
- Efficient data structures for row handling
- Proper cleanup of temporary resources

## Deployment and Distribution

### Packaging
- Poetry-based dependency management
- PyPI distribution
- Pre-compiled binaries for multiple platforms
- Docker support for containerized deployment

### CI/CD Pipeline
- Automated testing on multiple Python versions
- Code quality checks with pre-commit hooks
- Automated releases with GitHub Actions
- Docker image building and publishing
- Ephemeral local build system for development and testing

## Maintenance and Updates

### Version Management
- Semantic versioning (MAJOR.MINOR.PATCH)
- Changelog maintenance
- Backward compatibility considerations

### API Compatibility
- Full compatibility with official Notion API specifications
- Regular dependency updates for notion-sdk-py
- Compatibility testing with official Notion API versions
- Official API stability and backward compatibility guarantees

## Contributing Guidelines

### Development Setup
1. Clone the repository
2. Install Poetry (optional - ephemeral build script handles this)
3. Run `poetry install` for dependencies OR use `./scripts/local-test-build.sh`
4. Set up pre-commit hooks
5. Configure environment variables for testing

### Ephemeral Build System
- Script: `scripts/local-test-build.sh`
- Environment: Self-contained in `.build/` directory
- Features:
  - Automatic Python virtual environment setup
  - Poetry installation and configuration
  - Dependency management with update options
  - PyInstaller binary creation
  - Testing integration
  - Clean build artifacts management
- Usage:
  ```bash
  # Basic build
  ./scripts/local-test-build.sh
  
  # Build with tests
  ./scripts/local-test-build.sh --test
  
  # Run comprehensive test suite
  ./scripts/local-test-build.sh --comprehensive-test
  
  # Update dependencies
  ./scripts/local-test-build.sh --update-deps
  
  # Clean build environment
  ./scripts/local-test-build.sh --clean
  ```

### Code Review Process
- All changes require pull request review
- Automated testing must pass
- Code quality checks must be satisfied
- Documentation updates for new features

### Testing Requirements
- Unit tests for new functionality
- Integration tests for API changes
- Manual testing for UI/UX changes
- Performance testing for optimization changes
- Comprehensive test suite for CLI argument validation and Notion SDK functionality

## Troubleshooting

### Common Issues
- Integration token expiration or invalid tokens (resolved with format validation and clear error messages)
- Invalid token format (resolved with user-friendly validation and guidance)
- Rate limiting from Notion API (resolved with 15-attempt retry logic and exponential backoff)
- File upload failures through API endpoints (resolved with enhanced retry logic)
- AI model loading issues
- Column type conversion errors
- Database access permissions and sharing requirements
- Database deletion operations requiring proper permissions and database URL validation (page URLs not supported for deletion operations)
- Race conditions during concurrent select option creation (resolved with thread-safe implementation)
- Database creation within pages timing issues (resolved with initialization delays and retry logic)
- CSV delimiter parsing failures (resolved with delimiter parameter fix)
- 409 Conflict errors during page creation (resolved with exponential backoff retry logic)
- 503 Service Unavailable and timeout errors during uploads (resolved with enhanced retry mechanism)
- Transient API errors and network connectivity issues (resolved with comprehensive retry logic)
- High concurrency scenarios (resolved with smart retry logic and jitter)
- Large file uploads (resolved with extended retry windows)
- Rate limit scenarios (resolved with exponential backoff and extended retry attempts)

### Debug Mode
- Enable verbose logging with --verbose flag
- File-based logging for detailed analysis
- Error context preservation for debugging

## Future Roadmap

### Planned Features
- Enhanced AI model support
- Additional file format support
- Improved performance optimizations
- Extended validation options
- Better error recovery mechanisms

### Technical Debt
- Code refactoring for better modularity
- Enhanced test coverage
- Performance benchmarking
- Documentation improvements

This documentation should be kept in sync with the cursorrule file to ensure consistent development practices and project understanding. 

## Outdated Packages Held Back Due to Dependency Constraints

The following packages are currently outdated but have not been updated because doing so would break compatibility with other dependencies in the project (such as flake8 plugins, wemake-python-styleguide, etc.):

| Package                  | Installed | Latest   | Reason Held Back                                 |
|--------------------------|-----------|----------|-------------------------------------------------|
| click                    | 8.1.8     | 8.2.1    | Transitive, constrained by parent dependencies   |
| eradicate                | 2.3.0     | 3.0.0    | Required by flake8-eradicate/wemake-styleguide   |
| flake8                   | 3.9.0     | 7.3.0    | Required by wemake-python-styleguide             |
| flake8-bandit            | 3.0.0     | 4.1.1    | Plugin, version tied to flake8                   |
| flake8-broken-line       | 0.4.0     | 1.0.0    | Plugin, version tied to flake8                   |
| flake8-bugbear           | 22.12.6   | 24.12.12 | Plugin, version tied to flake8                   |
| flake8-commas            | 2.1.0     | 4.0.0    | Plugin, version tied to flake8                   |
| flake8-eradicate         | 1.4.0     | 1.5.0    | Plugin, version tied to eradicate/flak8          |
| flake8-isort             | 4.2.0     | 6.1.2    | Plugin, version tied to flake8/isort             |
| flake8-rst-docstrings    | 0.2.7     | 0.3.1    | Plugin, version tied to flake8                   |
| isort                    | 5.13.2    | 6.0.1    | Required by flake8-isort                         |
| mccabe                   | 0.6.1     | 0.7.0    | Required by flake8 <5                            |
| pep8-naming              | 0.11.1    | 0.15.1   | Latest requires flake8 >=5                       |
| pre-commit               | 2.21.0    | 4.2.0    | Not updated to avoid breaking hooks              |
| pycodestyle              | 2.7.0     | 2.14.0   | Required by flake8 <5                            |
| pyfakefs                 | 4.7.0     | 5.9.1    | Not updated to avoid breaking tests              |
| pyflakes                 | 2.3.1     | 3.4.0    | Required by flake8 <5                            |
| pytest                   | 7.4.4     | 8.4.1    | Not updated to avoid breaking test compatibility |
| pytest-cov               | 3.0.0     | 6.2.1    | Not updated to avoid breaking test compatibility |
| testfixtures             | 7.2.2     | 9.1.0    | Not updated to avoid breaking test compatibility |
| wemake-python-styleguide | 0.16.1    | 1.3.0    | Latest requires Python >=3.10                    |

> These packages will be updated when their dependencies allow, or when the project drops support for Python 3.9 or older plugin versions. 