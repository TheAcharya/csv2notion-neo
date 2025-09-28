# CSV2Notion Neo - Test Suite

This directory contains the modular test suite for CSV2Notion Neo, including test data sets, integration tests, and automated testing scripts.

## Overview

The test suite is designed to validate CSV2Notion Neo's functionality across different scenarios, including:
- CSV and JSON file uploads
- Image and icon handling
- Database merging operations
- Database entry deletion
- Notion API integration
- Error handling and validation
- CLI argument validation
- Notion SDK functionality without credentials

## Directory Structure

```
tests/
├── __init__.py                           # Python package initialization
├── README.md                             # This file
├── test_comprehensive.py                 # Comprehensive test suite (CLI + SDK)
├── test_upload.py                        # Upload functionality test suite
├── test_delete_database_entries.py       # Delete database entries test suite
├── input_command.py                      # Test configuration and arguments
├── upload-markers_json-rename-key.sh     # Manual upload test script (not used in CI)
├── upload-markers-delete-database-entries.sh  # Manual delete test script (not used in CI)
├── log.txt                               # Test execution logs (generated during testing)
└── assets/                               # Test data and media files
    ├── notion-upload-test.json           # JSON test data
    ├── icon-marker*.png                  # Icon test images
    ├── notion-upload-test_*.gif          # Animated test images
    └── notion-upload-test_*-Palette.jpg   # Static test images
```

## Test Components

### 1. Comprehensive Tests (test_comprehensive.py)

The comprehensive test suite that validates all CLI arguments and Notion SDK functionality:

- CLI Argument Testing: Validates all 50+ CLI arguments and switches
- Argument Validation: Tests argument parsing and type conversion
- Error Handling: Tests various error scenarios and edge cases
- Notion SDK Testing: Tests Notion SDK functionality without credentials using mocking
- Data Processing: Tests string splitting and data conversion utilities
- Conversion Rules: Tests ConversionRules dataclass functionality
- Version and Help: Tests version and help functionality
- Comprehensive Scenarios: Tests complex scenarios combining multiple features

#### Test Coverage for test_comprehensive.py

| Test Category | Test Class | Test Methods | Coverage | Status |
|---------------|------------|--------------|----------|---------|
| **CLI Argument Parsing** | `TestCLIArgumentParsing` | `test_required_arguments`, `test_general_options`, `test_machine_learning_options`, `test_column_options`, `test_merge_options`, `test_relations_options`, `test_database_management_options`, `test_page_cover_options`, `test_page_icon_options`, `test_validation_options` | All 50+ CLI arguments and switches | Covered |
| **Argument Validation** | `TestArgumentValidation` | `test_column_types_validation`, `test_default_icon_validation`, `test_max_threads_validation` | Argument parsing and type conversion | Covered |
| **Conversion Rules** | `TestConversionRules` | `test_conversion_rules_creation`, `test_files_search_path_property` | ConversionRules dataclass functionality | Covered |
| **Data Processing** | `TestDataProcessing` | `test_string_splitting` | String splitting and data conversion utilities | Covered |
| **Error Handling** | `TestErrorHandling` | `test_critical_error_handling`, `test_invalid_column_types`, `test_missing_required_arguments`, `test_invalid_file_paths` | Error scenarios and edge cases | Covered |
| **Version and Help** | `TestVersionAndHelp` | `test_version_argument`, `test_help_argument`, `test_version_constant` | Version and help functionality | Covered |
| **Comprehensive Scenarios** | `TestComprehensiveScenarios` | `test_full_upload_scenario`, `test_ai_captioning_scenario`, `test_database_deletion_scenario`, `test_validation_scenario` | Complex scenarios combining multiple features | Covered |
| **Notion SDK Testing** | `TestNotionSDKWithoutCredentials` | `test_notion_client_initialization`, `test_notion_client_get_collection`, `test_notion_client_create_record`, `test_notion_client_upload_file`, `test_notion_client_extended_initialization`, `test_notion_db_initialization`, `test_notion_row_converter`, `test_notion_row_uploader` | Notion SDK functionality without credentials | Covered |
| **Edge Cases** | `TestEdgeCases` | `test_empty_arguments`, `test_whitespace_handling`, `test_special_characters` | Edge cases and boundary conditions | Covered |

### 2. Upload Tests (test_upload.py)

The upload test suite that validates CSV/JSON upload functionality:

- Test Setup: Uses pytest fixtures for client and data initialization
- Upload Testing: Validates CSV/JSON upload to Notion databases
- Merge Operations: Tests database merging functionality
- Image Handling: Validates image upload and processing
- Error Handling: Tests various error scenarios

### 3. Delete Database Entries Tests (test_delete_database_entries.py)

The delete test suite that validates database entry deletion functionality:

- Delete Testing: Validates deletion of all database entries
- URL Validation: Tests proper database URL requirements
- Error Handling: Tests various deletion error scenarios
- API Integration: Tests Notion API delete operations

#### Usage
```bash
# Run all tests
pytest tests/

# Run comprehensive tests only
pytest tests/test_comprehensive.py

# Run upload tests only
pytest tests/test_upload.py

# Run delete tests only
pytest tests/test_delete_database_entries.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=csv2notion_neo

# Run comprehensive tests with local build script
./scripts/local-test-build.sh --comprehensive-test
```

### 4. Test Configuration (input_command.py)

Contains test configuration and argument definitions:

- Environment Variables: Loads Notion tokens and URLs from .env
- Test Arguments: Comprehensive argument dictionary for testing
- Data Sources: References test data files
- Feature Flags: Configures various CSV2Notion Neo features
- Logging: Configures log file output to tests/log.txt

#### Key Configuration
```python
ARGS_DICT = {
    'csv_file': 'tests/assets/notion-upload-test.json',
    'workspace': "Arjun's notion",
    'token': os.getenv("NOTION_TOKEN"),
    'url': os.getenv("NOTION_URL"),
    'log': PosixPath('tests/log.txt'),
    'image_column': ['Image Filename'],
    'mandatory_column': ['Marker ID'],
    'payload_key_column': 'Marker ID',
    # ... additional configuration
}
```

### 5. Manual Test Scripts

Shell scripts for manual testing and validation (NOT used in GitHub CI):

#### Upload Script (upload-markers_json-rename-key.sh)
- Automated Uploads: Runs CSV2Notion Neo with predefined parameters
- Logging: Captures detailed execution logs to tests/log.txt
- Error Handling: Provides feedback on upload success/failure
- Configurable: Easy to modify for different test scenarios

#### Delete Script (upload-markers-delete-database-entries.sh)
- Delete Operations: Runs CSV2Notion Neo with delete-all-database-entries flag
- Logging: Captures detailed execution logs to tests/log.txt
- Error Handling: Provides feedback on deletion success/failure
- Manual Testing: Available for local development and manual testing

#### Usage
```bash
# Make scripts executable
chmod +x tests/upload-markers_json-rename-key.sh
chmod +x tests/upload-markers-delete-database-entries.sh

# Run manual upload test
./tests/upload-markers_json-rename-key.sh

# Run manual delete test
./tests/upload-markers-delete-database-entries.sh

# Check test logs
cat tests/log.txt
```

## Test Data Sets

### JSON Test Data (assets/notion-upload-test.json)

Comprehensive test dataset containing:
- Marker Data: Sample marker entries with various properties
- Image References: Paths to test images and icons
- Metadata: Additional properties for testing different column types
- Validation Data: Data for testing mandatory columns and validation

### Test Images (assets/)

#### Icons
- icon-marker-chapter.png - Chapter marker icon
- icon-marker-todo-complete.png - Completed todo marker
- icon-marker-todo-incomplete.png - Incomplete todo marker
- icon-marker.png - Default marker icon

#### Animated Images
- notion-upload-test_*.gif - Animated test images for upload validation

#### Static Images
- notion-upload-test_*-Palette.jpg - Static test images with color palettes

## Environment Setup

### Required Environment Variables

Create a .env file in the project root with:

```bash
# Notion API Configuration
NOTION_TOKEN=your_notion_token_here
NOTION_URL=your_notion_database_url_here
NOTION_WORKSPACE=your_workspace_name

# Optional: Hugging Face for AI testing
HUGGING_FACE_TOKEN=your_hf_token_here
```

### Prerequisites

1. Notion Account: Active Notion workspace with API access
2. Test Database: Notion database for testing uploads
3. Python Environment: Poetry environment with all dependencies
4. Test Permissions: Write access to test database

## Running Tests

### Local Development Testing

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest tests/

# Run comprehensive tests (no credentials required)
poetry run pytest tests/test_comprehensive.py -v

# Run specific test
poetry run pytest tests/test_upload.py::test_upload_rows

# Run with coverage
poetry run pytest tests/ --cov=csv2notion_neo --cov-report=html

# Run comprehensive tests with local build script
./scripts/local-test-build.sh --comprehensive-test

# Check test logs
cat tests/log.txt
```

### CI/CD Testing

The test suite is integrated with GitHub Actions workflows:

#### Comprehensive Tests (comprehensive_test.yml)
- Runs on manual workflow dispatch
- Tests all CLI arguments and Notion SDK functionality without credentials
- Command: `pytest tests/test_comprehensive.py -v -s --tb=long`

#### Upload Tests (notion_image_upload_test.yml)
- Runs every Saturday at 8 AM Singapore time
- Tests upload functionality with pytest
- Command: `pytest tests/test_upload.py -v -s`

#### Delete Tests (notion_delete_database_entries_test.yml)
- Runs every Saturday at 10 AM Singapore time
- Tests delete database entries functionality with pytest
- Command: `pytest tests/test_delete_database_entries.py -v -s`

```yaml
# Example GitHub Actions step
- name: Run Tests
  run: |
    poetry install
    poetry run pytest tests/test_upload.py -v -s
```

### Manual Testing

```bash
# Configure environment variables
export NOTION_TOKEN="your_token"
export NOTION_URL="your_database_url"
export NOTION_WORKSPACE="your_workspace"

# Run manual upload test
./tests/upload-markers_json-rename-key.sh

# Run manual delete test
./tests/upload-markers-delete-database-entries.sh

# Review test logs
cat tests/log.txt
```

## Test Scenarios

### 1. Comprehensive CLI Testing
- All 50+ CLI arguments and switches validation
- Argument parsing and type conversion
- Error handling for invalid arguments
- Edge cases and boundary conditions
- Version and help functionality

### 2. Notion SDK Testing (Mocked)
- Client initialization and configuration
- Database operations without credentials
- File upload functionality
- Row conversion and upload operations
- Error handling and retry logic

### 3. Basic Upload Testing
- CSV/JSON file upload to new database
- Column type detection and mapping
- Data validation and error handling

### 4. Image Upload Testing
- Single and multiple image uploads
- Icon and cover image handling
- Image format validation

### 5. Database Merging
- Existing database updates
- Key-based row matching
- Partial column updates

### 6. Database Deletion Testing
- Delete all database entries
- Database URL validation
- Error handling for invalid URLs

### 7. Error Handling
- Invalid data scenarios
- API error responses
- Network connectivity issues

### 8. Performance Testing
- Large dataset uploads
- Concurrent upload operations
- Memory usage validation

## Test Data Management

### Adding New Test Data

1. Create Test Files: Add new CSV/JSON files to assets/
2. Update Configuration: Modify input_command.py as needed
3. Add Test Images: Include relevant test images in assets/
4. Update Documentation: Document new test scenarios

### Test Data Validation

```bash
# Validate JSON test data
python -m json.tool tests/assets/notion-upload-test.json

# Check image file integrity
file tests/assets/*.png tests/assets/*.gif tests/assets/*.jpg
```

## Logging and Debugging

### Test Logs

All test execution logs are saved to `tests/log.txt`:

```bash
# View recent test logs
tail -f tests/log.txt

# Search for errors in logs
grep -i error tests/log.txt

# View full test log
cat tests/log.txt
```

### Log File Management

```bash
# Clear old logs
rm tests/log.txt

# Archive logs with timestamp
mv tests/log.txt tests/log_$(date +%Y%m%d_%H%M%S).txt
```

## Troubleshooting

### Common Issues

1. Environment Variables Not Set
   ```bash
   # Check environment variables
   echo $NOTION_TOKEN
   echo $NOTION_URL
   echo $NOTION_WORKSPACE
   ```

2. Test Database Access
   - Ensure database URL is correct
   - Verify write permissions
   - Check workspace access

3. Image Upload Failures
   - Verify image file paths
   - Check file permissions
   - Validate image formats

4. API Rate Limiting
   - Reduce max_threads parameter
   - Add delays between tests
   - Use test-specific API tokens

### Debug Mode

```bash
# Run tests with debug output
poetry run pytest tests/ -v -s

# Run comprehensive tests with detailed traceback
poetry run pytest tests/test_comprehensive.py -v -s --tb=long

# Run specific test with debug
poetry run pytest tests/test_upload.py::test_upload_rows -v -s

# Run comprehensive tests with local build script (includes detailed traceback)
./scripts/local-test-build.sh --comprehensive-test

# Check detailed logs
cat tests/log.txt
```

## Contributing to Tests

### Adding New Tests

1. Follow pytest conventions: Use descriptive test names
2. Use fixtures: Leverage existing fixtures for setup
3. Add documentation: Document test purpose and expected behavior
4. Include test data: Add necessary test files to assets/

### Test Best Practices

- Isolation: Tests should be independent and not affect each other
- Cleanup: Clean up test data after execution
- Validation: Include assertions for expected outcomes
- Error Cases: Test both success and failure scenarios
- Logging: Use the configured log file for debugging

## Integration with Development Workflow

### Pre-commit Testing

Tests are integrated with pre-commit hooks:

```yaml
# .pre-commit-config.yaml
- id: pytest
  name: pytest
  stages: [commit]
  entry: poetry run pytest
  types: [python]
```

### Continuous Integration

Tests run automatically on:
- Scheduled runs (every Saturday)
- Manual workflow dispatch
- Pull requests (if configured)
- Main branch commits (if configured)
- Release builds (if configured)

## Support

For test-related issues:
1. Check the troubleshooting section above
2. Review test logs in tests/log.txt
3. Verify environment configuration
4. Consult the main project documentation

For more information about CSV2Notion Neo testing, see the main project documentation and AGENT.MD file.
