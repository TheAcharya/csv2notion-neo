# CSV2Notion Neo - Agent Documentation

## Project Overview

CSV2Notion Neo is an advanced command-line tool for uploading and merging CSV or JSON files with images to Notion databases. It serves as a successor to the original csv2notion project, providing enhanced compatibility with Notion's evolving API and additional features like AI-powered image captioning.

## Core Architecture

### Main Components

1. **CLI Interface** (`csv2notion_neo/cli.py`)
   - Entry point for the application
   - Handles argument parsing and logging setup
   - Orchestrates the main workflow

2. **Data Processing** (`csv2notion_neo/local_data.py`)
   - Reads and validates CSV/JSON files
   - Manages column types and data structure
   - Handles AI feature integration

3. **Notion Integration** (`csv2notion_neo/notion/`)
   - Custom Notion client implementation
   - Database and collection management
   - File upload and block operations

4. **Conversion Engine** (`csv2notion_neo/notion_convert.py`)
   - Converts CSV/JSON data to Notion format
   - Handles different column types
   - Manages image and icon processing

5. **Upload System** (`csv2notion_neo/notion_uploader.py`)
   - Manages row uploads to Notion
   - Handles merge operations
   - Integrates AI captioning features

## Key Features

### Data Import Capabilities
- CSV and JSON file support
- Automatic column type detection
- Manual column type specification
- Support for all Notion column types (text, number, select, multi_select, date, checkbox, url, email, phone_number, file, person, relation, rollup, formula, created_time, last_edited_time, created_by, last_edited_by)

### Advanced Operations
- Merge existing databases using key columns
- Relation column handling with automatic linking
- File upload support for images and documents
- Icon and cover image assignment
- Mandatory column validation

### AI Integration
- Hugging Face integration for image captioning
- Support for multiple AI models (vit-gpt2, blip-image, git-large)
- Automatic caption generation for uploaded images

### Performance Features
- Multithreaded uploads for improved speed
- Rate limiting to respect Notion API limits
- Progress tracking with tqdm

## Development Guidelines

### Code Structure
- Follow Python type hints throughout
- Use dataclasses for configuration objects
- Implement proper error handling with custom exceptions
- Maintain comprehensive logging

### Testing Strategy
- Unit tests for core functionality
- Integration tests for Notion API interactions
- VCR-based testing for API responses
- Coverage reporting for quality assurance

### Code Quality
- Black formatting with 88 character line length
- isort for import organization
- flake8 and wemake-python-styleguide for linting
- mypy for type checking
- Pre-commit hooks for automated quality checks

### Dependencies
- Python 3.8+ required
- Poetry for dependency management
- Key dependencies: requests, tqdm, emoji, python-dateutil, icecream

## API Integration

### Notion API
- Custom client implementation for Notion's unofficial private API
- Support for CRDT operations and atomic transactions
- File upload handling with signed URLs
- Rate limiting and error handling
- Note: Uses unofficial private APIs that may change without notice

### Hugging Face API
- Integration with Hugging Face inference API
- Support for image captioning models
- Token-based authentication
- Retry logic for model loading

## Configuration Management

### Command Line Arguments
- Workspace and token authentication
- Database URL specification
- Column type mapping
- Image and icon handling options
- Merge and validation flags
- AI model configuration

### Environment Variables
- Notion authentication tokens
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

## Security Considerations

### Authentication
- Secure token handling for Notion API
- Hugging Face token management
- No hardcoded credentials in source code

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

## Maintenance and Updates

### Version Management
- Semantic versioning (MAJOR.MINOR.PATCH)
- Changelog maintenance
- Backward compatibility considerations

### API Compatibility
- Monitoring Notion unofficial private API changes
- Regular dependency updates
- Compatibility testing with different Notion versions
- Note: Unofficial APIs may break with Notion updates, requiring prompt fixes

## Contributing Guidelines

### Development Setup
1. Clone the repository
2. Install Poetry
3. Run `poetry install` for dependencies
4. Set up pre-commit hooks
5. Configure environment variables for testing

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

## Troubleshooting

### Common Issues
- Authentication token expiration
- Rate limiting from Notion unofficial private API
- File upload failures
- AI model loading issues
- Column type conversion errors
- Unofficial API breaking changes from Notion updates

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