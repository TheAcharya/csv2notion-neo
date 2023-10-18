#!/bin/sh

TOOL_PATH="poetry run csv2notion_neo"
NOTION_TOKEN="v02%3Auser_token_or_cookies%3Ac1TyK1LD5XpYfGLqxmDlJsN_PB-AGy9EBmnIMxMgQy7JNfETpdqgC2mK_OFdSF6gifcZiEBU53Xk3QuHQlBstsftZNtV3jzcgoXhtGX7FRIhxq1ravBTc9DW1f--Fr7DhYmZ"
NOTION_URL="https://www.notion.so/9275939ac1cd4214a44a54ec6da27383?v=3610508219144eabbe9fc846383920a1&pvs=4"
UPLOAD_CSV="fake_file.csv"
UPLOAD_LOG="test_log.txt"

$TOOL_PATH --token $NOTION_TOKEN --url $NOTION_URL --log $UPLOAD_LOG --verbose "$UPLOAD_CSV"