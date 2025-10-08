#!/bin/sh

# CSV2Notion Neo - Delete Database Entries Test Script
# This script is NOT used in GitHub CI workflows
# It's available for manual testing and local development
# The CI uses pytest tests instead

TOOL_PATH="poetry run csv2notion_neo"
NOTION_WORKSPACE=""
NOTION_TOKEN=""
NOTION_URL=""
UPLOAD_PAYLOAD="tests/assets/notion-upload-test.json"
UPLOAD_LOG="tests/log.txt"

$TOOL_PATH --workspace "$NOTION_WORKSPACE" --token $NOTION_TOKEN --url $NOTION_URL --delete-all-database-entries --log "$UPLOAD_LOG" --verbose