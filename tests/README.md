# CSV2Notion Neo - Test Suite

This directory contains the comprehensive test suite for CSV2Notion Neo, including test data sets, integration tests, and automated testing scripts.

## Overview

The test suite is designed to validate CSV2Notion Neo's functionality across different scenarios, including:
- CSV and JSON file uploads
- Image and icon handling
- Database merging operations
- Notion API integration
- Error handling and validation

## Directory Structure

```
tests/
├── __init__.py                    # Python package initialization
├── README.md                      # This file
├── test_upload.py                 # Main integration test suite
├── input_command.py               # Test configuration and arguments
├── upload-markers_json-rename-key.sh  # Automated upload script
├── log.txt                        # Test execution logs (generated during testing)
└── assets/                        # Test data and media files
    ├── notion-upload-test.json    # JSON test data
    ├── icon-marker*.png           # Icon test images
    └── notion-upload-test_*.gif   # Animated test images
    └── notion-upload-test_*-Palette.jpg  # Static test images
```

## Test Components

### 1. Integration Tests (test_upload.py)

The main test suite that validates end-to-end functionality:

- Test Setup: Uses pytest fixtures for client and data initialization
- Upload Testing: Validates CSV/JSON upload to Notion databases
- Merge Operations: Tests database merging functionality
- Image Handling: Validates image upload and processing
- Error Handling: Tests various error scenarios

#### Usage
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_upload.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=csv2notion_neo
```

### 2. Test Configuration (input_command.py)

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
    'token': os.getenv("NOTION_TOKEN_A"),
    'url': os.getenv("NOTION_URL_A"),
    'log': PosixPath('tests/log.txt'),
    'image_column': ['Image Filename'],
    'mandatory_column': ['Marker ID'],
    'payload_key_column': 'Marker ID',
    # ... additional configuration
}
```

### 3. Automated Upload Script (upload-markers_json-rename-key.sh)

Shell script for automated testing and validation:

- Automated Uploads: Runs CSV2Notion Neo with predefined parameters
- Logging: Captures detailed execution logs to tests/log.txt
- Error Handling: Provides feedback on upload success/failure
- Configurable: Easy to modify for different test scenarios

#### Usage
```bash
# Make executable
chmod +x tests/upload-markers_json-rename-key.sh

# Run automated upload test
./tests/upload-markers_json-rename-key.sh

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
NOTION_TOKEN_A=your_notion_token_here
NOTION_URL_A=your_notion_database_url_here

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

# Run specific test
poetry run pytest tests/test_upload.py::test_upload_rows

# Run with coverage
poetry run pytest tests/ --cov=csv2notion_neo --cov-report=html

# Check test logs
cat tests/log.txt
```

### CI/CD Testing

The test suite is integrated with GitHub Actions:

```yaml
# Example GitHub Actions step
- name: Run Tests
  run: |
    poetry install
    poetry run pytest tests/ -v
```

### Automated Upload Testing

```bash
# Configure environment variables
export NOTION_TOKEN_A="your_token"
export NOTION_URL_A="your_database_url"

# Run automated upload test
./tests/upload-markers_json-rename-key.sh

# Review test logs
cat tests/log.txt
```

## Test Scenarios

### 1. Basic Upload Testing
- CSV/JSON file upload to new database
- Column type detection and mapping
- Data validation and error handling

### 2. Image Upload Testing
- Single and multiple image uploads
- Icon and cover image handling
- Image format validation

### 3. Database Merging
- Existing database updates
- Key-based row matching
- Partial column updates

### 4. Error Handling
- Invalid data scenarios
- API error responses
- Network connectivity issues

### 5. Performance Testing
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
   echo $NOTION_TOKEN_A
   echo $NOTION_URL_A
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

# Run specific test with debug
poetry run pytest tests/test_upload.py::test_upload_rows -v -s

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
- Pull requests
- Main branch commits
- Release builds

## Support

For test-related issues:
1. Check the troubleshooting section above
2. Review test logs in tests/log.txt
3. Verify environment configuration
4. Consult the main project documentation

For more information about CSV2Notion Neo testing, see the main project documentation and AGENT.MD file.
