#!/bin/sh

# CSV2Notion Neo - Upload Test Script
# This script is NOT used in GitHub CI workflows
# It's available for manual testing and local development
# The CI uses pytest tests instead

TOOL_PATH="poetry run csv2notion_neo"
NOTION_WORKSPACE=""
NOTION_TOKEN=""
NOTION_URL=""
UPLOAD_PAYLOAD="tests/assets/notion-upload-test.json"
UPLOAD_LOG="tests/log.txt"

#$TOOL_PATH --workspace $NOTION_WORKSPACE --token $NOTION_TOKEN --url $NOTION_URL --image-column "Image Filename" --image-column-keep --mandatory-column "Marker ID" --icon-column "Icon Image" --payload-key-column "Marker ID" --max-threads 5 --merge --log $UPLOAD_LOG --verbose $UPLOAD_PAYLOAD
$TOOL_PATH --workspace "$NOTION_WORKSPACE" --token $NOTION_TOKEN --url $NOTION_URL --randomize-select-colors --image-column "Image Filename" --randomize-select-colors --image-column-keep --mandatory-column "Marker ID" --payload-key-column "Marker ID" --merge  --max-threads 5 --max-threads 1  --log "$UPLOAD_LOG" --verbose "$UPLOAD_PAYLOAD"