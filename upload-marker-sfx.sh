#!/bin/sh

TOOL_PATH="poetry run csv2notion_neo"
TOOL_PATH_2="marker_data_demo/csv2notion_neo"
NOTION_TOKEN="v02%3Auser_token_or_cookies%3Ac1TyK1LD5XpYfGLqxmDlJsN_PB-AGy9EBmnIMxMgQy7JNfETpdqgC2mK_OFdSF6gifcZiEBU53Xk3QuHQlBstsftZNtV3jzcgoXhtGX7FRIhxq1ravBTc9DW1f--Fr7DhYmZ"
NOTION_URL="https://www.notion.so/a47999650bac44cf80c3c512dcca7e52?v=15a6cdf4a39e410ea3d3cd12e8ae6150&pvs=4"
UPLOAD_CSV="marker_data_demo/user.csv"
UPLOAD_LOG="marker_data_demo/log.txt"

#$TOOL_PATH --token $NOTION_TOKEN --url $NOTION_URL --image-column "Image Filename" --image-column-keep --mandatory-column "Marker ID" --icon-column "Icon Image" --max-threads 5 --merge --log $UPLOAD_LOG --verbose "$UPLOAD_CSV"
#$TOOL_PATH --token $NOTION_TOKEN --url $NOTION_URL --mandatory-column "Marker ID" --merge-only-column "Marker Name" --max-threads 5 --merge --log $UPLOAD_LOG --verbose "$UPLOAD_CSV"
$TOOL_PATH --token $NOTION_TOKEN --url $NOTION_URL --image-column "Image Filename" --mandatory-column "Shot Code" --merge --max-threads 8 --log $UPLOAD_LOG --verbose "$UPLOAD_CSV"
#$TOOL_PATH --token $NOTION_TOKEN --url $NOTION_URL --max-threads 5 --merge --image-column "Image Filename" --mandatory-column "Shot Code" --log $UPLOAD_LOG --verbose "$UPLOAD_CSV"
#$TOOL_PATH --token $NOTION_TOKEN --url $NOTION_URL --image-column "Image Filename" --mandatory-column "Shot Code" --max-threads 5 --merge --log $UPLOAD_LOG --verbose "$UPLOAD_CSV"SS