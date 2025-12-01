# CSV2Notion Neo - Test Suite

This directory contains the modular test suite for CSV2Notion Neo, including test data sets, integration tests, and automated testing scripts.

## Overview

The test suite is designed to validate CSV2Notion Neo's functionality across different scenarios, including:
- CSV and JSON file uploads
- Image and icon handling
- Database merging operations
- Database entry deletion
- Notion API integration (API version 2025-09-03 with data_sources structure)
- Error handling and validation
- CLI argument validation with token format validation and URL validation
- Notion SDK functionality without credentials (notion-client 2.7.0)
- Column type detection and auto-detection
- Data processing and conversion utilities
- Advanced multi-feature scenarios
- Edge cases and boundary conditions

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
- Argument Validation: Tests argument parsing, type conversion, token format validation, and URL validation
- Error Handling: Tests various error scenarios and edge cases
- Notion SDK Testing: Tests Notion SDK functionality without credentials using mocking
- Data Processing: Tests string splitting, data conversion utilities, and real-time progress bar updates
- Conversion Rules: Tests ConversionRules dataclass functionality
- Version and Help: Tests version and help functionality
- Comprehensive Scenarios: Tests complex scenarios combining multiple features
- Column Type Detection: Tests auto-detection and type guessing functionality
- Column Type Operations: Tests all Notion column types and their operations
- Merge Operations: Tests database merging and updating operations
- Image Operations: Tests image upload and processing operations
- Icon Operations: Tests icon assignment and processing operations
- Relation Operations: Tests database relations and linking operations
- Validation Operations: Tests data validation and error handling operations
- File Operations: Tests file upload and media handling operations
- Advanced Scenarios: Tests complex multi-feature scenarios
- Edge Cases: Tests edge cases and boundary conditions

#### Complete Test Coverage for test_comprehensive.py

| Test Category | Test Class | Test Methods | Coverage | Status |
|---------------|------------|--------------|----------|---------|
| CLI Argument Parsing | TestCLIArgumentParsing | test_required_arguments, test_general_options, test_machine_learning_options, test_column_options, test_merge_options, test_relations_options, test_database_management_options, test_page_cover_options, test_page_icon_options, test_validation_options | All 50+ CLI arguments and switches | Covered |
| Argument Validation | TestArgumentValidation | test_column_types_validation, test_default_icon_validation, test_max_threads_validation, test_notion_token_validation | Argument parsing, type conversion, token format validation, and URL validation | Covered |
| Conversion Rules | TestConversionRules | test_conversion_rules_creation, test_files_search_path_property | ConversionRules dataclass functionality | Covered |
| Data Processing | TestDataProcessing | test_string_splitting, test_date_conversion, test_merge_race_condition_prevention, test_large_dataset_merge_simulation, test_progress_bar_real_time_updates | String splitting, data conversion utilities, and real-time progress bar updates | Covered |
| Error Handling | TestErrorHandling | test_critical_error_handling, test_invalid_column_types, test_missing_required_arguments, test_invalid_file_paths | Error scenarios and edge cases | Covered |
| Version and Help | TestVersionAndHelp | test_version_argument, test_help_argument, test_version_constant | Version and help functionality | Covered |
| Comprehensive Scenarios | TestComprehensiveScenarios | test_full_upload_scenario, test_ai_captioning_scenario, test_database_deletion_scenario, test_validation_scenario | Complex scenarios combining multiple features | Covered |
| Notion SDK Testing | TestNotionSDKWithoutCredentials | test_notion_client_initialization, test_notion_client_get_collection, test_notion_client_create_record, test_notion_client_upload_file, test_notion_client_extended_initialization, test_notion_db_initialization, test_notion_row_converter, test_notion_row_uploader, test_notion_db_pagination_large_datasets | Notion SDK functionality without credentials, including pagination for large datasets | Covered |
| Column Type Detection | TestColumnTypeDetection | test_type_guessing_numbers, test_type_guessing_urls, test_type_guessing_emails, test_type_guessing_checkboxes, test_type_guessing_by_values | Auto-detection and type guessing functionality | Covered |
| Column Type Operations | TestColumnTypeOperations | test_column_type_validation, test_column_type_mapping, test_column_type_combinations, test_column_type_edge_cases | All Notion column types and their operations | Covered |
| Merge Operations | TestMergeOperations | test_merge_argument_parsing, test_merge_validation_scenarios, test_merge_column_validation, test_merge_edge_cases | Database merging and updating operations | Covered |
| Image Operations | TestImageOperations | test_image_column_arguments, test_image_caption_arguments, test_image_mode_validation, test_image_column_edge_cases | Image upload and processing operations | Covered |
| Icon Operations | TestIconOperations | test_icon_column_arguments, test_default_icon_validation, test_icon_column_edge_cases | Icon assignment and processing operations | Covered |
| Relation Operations | TestRelationOperations | test_relation_argument_parsing, test_relation_validation_scenarios, test_relation_edge_cases | Database relations and linking operations | Covered |
| Validation Operations | TestValidationOperations | test_mandatory_column_validation, test_validation_error_handling, test_validation_scenarios | Data validation and error handling operations | Covered |
| File Operations | TestFileOperations | test_file_validation, test_file_extension_validation, test_file_size_validation | File upload and media handling operations | Covered |
| Advanced Scenarios | TestAdvancedScenarios | test_full_feature_scenario, test_ai_captioning_scenario, test_merge_with_relations_scenario, test_database_deletion_scenario, test_validation_scenario | Complex multi-feature scenarios | Covered |
| Edge Cases | TestEdgeCases | test_empty_arguments, test_whitespace_handling, test_special_characters | Edge cases and boundary conditions | Covered |

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
- URL Validation: Tests proper database URL requirements and Notion.so domain validation
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
    'image_column': ['Image Filename', 'Palette Filename'],
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
NOTION_TOKEN=ntn_your_notion_token_here  # Must start with 'ntn_' or 'secret_'
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

# Run comprehensive tests with local build script (recommended)
./scripts/local-test-build.sh --comprehensive-test

# Run specific pagination test
./.build/venv/csv2notion-neo-NE53AkMF-py3.9/bin/python -m pytest tests/test_comprehensive.py::TestNotionSDKWithoutCredentials::test_notion_db_pagination_large_datasets -v

# Run large dataset merge simulation test
./.build/venv/csv2notion-neo-NE53AkMF-py3.9/bin/python -m pytest tests/test_comprehensive.py::TestDataProcessing::test_large_dataset_merge_simulation -v

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
- Token format validation (ntn_ and secret_ prefixes)
- URL validation (Notion.so domain and protocol validation)
- Error handling for invalid arguments
- Edge cases and boundary conditions
- Version and help functionality

### 2. Notion SDK Testing (Mocked)
- Client initialization and configuration (API version 2025-09-03)
- Database operations without credentials using data_sources structure
- File upload functionality via file_uploads API
- Row conversion and upload operations
- Error handling and retry logic
- Large Dataset Pagination: Tests pagination handling for datasets >100 rows (PR #66)

### 3. Column Type Detection and Operations
- Auto-detection of number, URL, email, checkbox types
- Type guessing by value patterns
- All Notion column types validation and parsing
- Column type combinations and edge cases
- Type mapping and validation scenarios

### 4. Database Operations
- Database merging and updating operations
- Merge argument parsing and validation
- Merge column validation and edge cases
- Database relations and linking operations
- Relation argument parsing and validation

### 5. Image and Icon Operations
- Image upload and processing operations
- Image column argument parsing
- Image caption and mode validation
- Icon assignment and processing operations
- Default icon validation and edge cases

### 6. Data Validation and Processing
- Data validation and error handling operations
- Mandatory column validation
- Validation error handling scenarios
- String splitting and data conversion utilities
- File validation and extension checking

### 7. Advanced Multi-Feature Scenarios
- Complex multi-feature scenarios combining multiple operations
- Full feature scenario testing with all operations
- AI captioning scenario testing
- Merge with relations scenario testing
- Database deletion scenario testing
- Comprehensive validation scenario testing

### 8. Edge Cases and Boundary Conditions
- Empty argument handling
- Whitespace handling in arguments
- Special character handling
- Boundary condition testing
- Error scenario validation

### 9. Basic Upload Testing
- CSV/JSON file upload to new database
- Column type detection and mapping
- Data validation and error handling

### 10. Image Upload Testing
- Single and multiple image uploads
- Icon and cover image handling
- Image format validation

### 11. Database Merging
- Existing database updates
- Key-based row matching
- Partial column updates

### 12. Database Deletion Testing
- Delete all database entries
- Database URL validation (Notion.so domain and protocol validation)
- Error handling for invalid URLs

### 13. Error Handling
- Invalid data scenarios
- Invalid token format scenarios
- Invalid URL format scenarios (non-Notion.so domains, invalid protocols)
- API error responses
- Network connectivity issues

### 14. Performance Testing
- Large dataset uploads
- Concurrent upload operations
- Memory usage validation
- Pagination Testing: Validates handling of large Notion databases (>100 rows)
- Race Condition Prevention: Tests thread-safe operations for concurrent uploads

## Recent Improvements

### Notion API 2025-09-03 Migration
- API Version: Upgraded to Notion API version 2025-09-03
- SDK Update: Updated notion-client to version 2.7.0
- Data Sources: Migrated to new data_sources structure for database properties
- Property Retrieval: Properties now fetched from data_sources endpoint instead of database object
- Schema Updates: Database schema modifications use data_sources.update endpoint
- Database Creation: Uses initial_data_source for new database property definitions
- Test Updates: All mocked tests updated to reflect new API response structure

### PR #66: Large Dataset Pagination Support
- Issue Fixed: Merge operations creating duplicates on large datasets (>100 rows)
- Solution: Complete pagination support in NotionDB.rows property
- Testing: Added comprehensive pagination test with 250 rows across 3 pages
- Performance: 4-5x improvement with thread-safe caching
- Validation: Ensures no duplicate rows and complete data retrieval

### Enhanced Test Coverage
- New Test: `test_notion_db_pagination_large_datasets` validates pagination logic
- Large Dataset Simulation: `test_large_dataset_merge_simulation` tests 1000-row scenarios
- Race Condition Testing: Validates thread-safe operations for concurrent uploads
- Real-time Progress: Tests progress bar updates during multi-threaded operations

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

2. Invalid Token Format
   ```bash
   # Check token format (must start with 'ntn_' or 'secret_')
   echo $NOTION_TOKEN | grep -E '^(ntn_|secret_)'
   ```

3. Invalid URL Format
   ```bash
   # Check URL format (must be Notion.so domain with http/https protocol)
   echo $NOTION_URL | grep -E '^https?://.*notion\.so'
   ```

4. Test Database Access
   - Ensure database URL is correct
   - Verify write permissions
   - Check workspace access

5. Image Upload Failures
   - Verify image file paths
   - Check file permissions
   - Validate image formats

6. API Rate Limiting
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

## Complete Test Coverage Summary

The CSV2Notion Neo test suite provides comprehensive coverage across 18 test categories with 78 individual test methods:

### Test Statistics
- Total Test Classes: 18
- Total Test Methods: 78
- Test Execution Time: ~0.88 seconds
- Coverage: 100% of CLI arguments and core functionality
- External Dependencies: None (all tests use mocking)
- Recent Updates: Added pagination tests for large datasets (PR #66)

### Test Categories Breakdown
1. CLI Argument Parsing (10 tests) - All command-line arguments and switches
2. Argument Validation (4 tests) - Token, URL, and type validation
3. Conversion Rules (2 tests) - Dataclass functionality and properties
4. Data Processing (5 tests) - String operations, utilities, and real-time progress bar updates
5. Error Handling (4 tests) - CriticalError scenarios and validation
6. Version and Help (3 tests) - Version constants and help functionality
7. Comprehensive Scenarios (4 tests) - Multi-feature combinations
8. Notion SDK Testing (9 tests) - Mocked API interactions, including pagination for large datasets
9. Column Type Detection (5 tests) - Auto-detection and type guessing
10. Column Type Operations (4 tests) - All Notion column types
11. Merge Operations (4 tests) - Database merging and updating
12. Image Operations (4 tests) - Image upload and processing
13. Icon Operations (3 tests) - Icon assignment and validation
14. Relation Operations (3 tests) - Database relations and linking
15. Validation Operations (3 tests) - Data validation and error handling
16. File Operations (3 tests) - File upload and media handling
17. Advanced Scenarios (5 tests) - Complex multi-feature scenarios
18. Edge Cases (3 tests) - Boundary conditions and special characters

### Key Testing Features
- No External API Calls: All tests use mocking to avoid Notion API dependencies
- Notion API 2025-09-03: Tests updated for new data_sources structure
- Comprehensive CLI Coverage: All 50+ CLI arguments and switches tested
- Error Scenario Testing: Invalid inputs, malformed data, and edge cases
- Performance Validation: File operations, memory usage, and concurrent operations
- Integration Testing: Multi-feature scenarios combining various operations
- Large Dataset Support: Pagination testing for databases >100 rows (PR #66)
- Thread Safety: Race condition prevention for concurrent operations
- Real-time Updates: Progress bar testing during multi-threaded uploads
- Documentation: Each test method is clearly documented and searchable

For more information about CSV2Notion Neo testing, see the main project documentation and AGENT.MD file.

Note: This test suite is compatible with notion-client 2.7.0 and Notion API version 2025-09-03.
