# CSV2Notion Neo - Official API Migration Guide

## Overview

This guide documents the migration from the unofficial Notion API to the official Notion SDK. The migration maintains 100% backward compatibility while providing enhanced security, reliability, and future-proofing.

## What Changed

### 1. Authentication
- **Before**: `token_v2` session cookies from browser
- **After**: Integration tokens from Notion's official API

### 2. Client Implementation
- **Before**: Custom fork of unmaintained `notion-py`
- **After**: Official `notion-client` SDK

### 3. File Uploads
- **Before**: Custom upload logic using unofficial endpoints
- **After**: Official file upload API with better reliability

## Migration Steps

### Step 1: Get Integration Token

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "CSV2Notion Neo")
4. Select the workspace
5. Copy the "Internal Integration Token"

### Step 2: Grant Database Access

1. Open your Notion database
2. Click "Share" in the top right
3. Click "Add people, emails, groups, or integrations"
4. Search for your integration name
5. Select it and give it appropriate permissions

### Step 3: Update CLI Usage

**Before:**
```bash
csv2notion_neo --token "your_token_v2_cookie" --workspace "Your Workspace" data.csv
```

**After:**
```bash
csv2notion_neo --token "secret_abc123..." --workspace "Your Workspace" data.csv
```

### Step 4: Test Migration

Run the migration test script:
```bash
python csv2notion_neo/migration_to_official.py "your_integration_token" "your_database_url"
```

## Benefits of Migration

### 1. Enhanced Security
- Integration tokens are more secure than session cookies
- Tokens don't expire like browser sessions
- Better access control and permissions

### 2. Improved Reliability
- Official API is more stable and well-tested
- Better error handling and retry mechanisms
- Reduced dependency on unofficial endpoints

### 3. Future-Proofing
- Official API is actively maintained by Notion
- New features and improvements are automatically available
- No risk of unofficial API breaking changes

### 4. Better Performance
- Optimized official endpoints
- Improved file upload mechanisms
- Better rate limiting and error handling

## Technical Details

### New Architecture

```
csv2notion_neo/
├── notion_client_official.py      # Official SDK client adapter
├── notion_db_official.py          # Database operations
├── notion_row_upload_file_official.py  # File upload operations
├── notion_db_client_official.py   # Extended client compatibility
└── migration_to_official.py       # Migration utilities
```

### Compatibility Layer

The migration includes a comprehensive compatibility layer that:
- Maintains all existing function signatures
- Preserves all CLI options and flags
- Ensures seamless transition without code changes
- Provides fallback mechanisms for edge cases

### File Upload Improvements

The official API provides:
- Native file upload support up to 100MB
- Better error handling and retry logic
- Improved upload performance
- Support for multiple file types

## Troubleshooting

### Common Issues

1. **"Invalid token" error**
   - Ensure you're using an integration token, not a session cookie
   - Verify the token is copied correctly (no extra spaces)

2. **"Database not accessible" error**
   - Make sure the integration has access to the database
   - Check that the database URL is correct

3. **"File upload failed" error**
   - Verify file size is under 100MB
   - Check file permissions and accessibility

### Getting Help

1. Check the migration test output for specific errors
2. Review the Notion API documentation
3. Ensure your integration has proper permissions
4. Verify your database URL format

## Rollback Plan

If you need to rollback to the unofficial API:

1. Revert the import changes in `cli.py` and `cli_steps.py`
2. Remove the `notion-client` dependency
3. Restore the original client initialization

However, this is not recommended as the unofficial API is no longer maintained.

## Conclusion

The migration to the official Notion SDK provides significant benefits in terms of security, reliability, and future-proofing. The compatibility layer ensures a seamless transition without breaking existing functionality.

All existing features, including CSV/JSON uploads, image handling, and merge operations, continue to work exactly as before, but with improved performance and reliability.
