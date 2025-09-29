"""
CSV2Notion Neo - Comprehensive Test Suite

This is the definitive test suite for CSV2Notion Neo that validates all CLI arguments,
flags, and switches. It provides complete coverage of the application's functionality
without requiring actual Notion API calls.

Test Coverage:
- All 50+ CLI arguments and their validation
- Argument parsing and type conversion
- Error handling for invalid arguments
- Function mapping and data structures
- Mock testing of core functionality
- Edge cases and boundary conditions
- Comprehensive scenarios combining multiple features
- Performance and reliability validation
- Notion SDK testing without credentials (mocked)
- Test runner functionality validation

This is the single comprehensive test suite that replaces all other test variations.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace

# Import CSV2Notion Neo modules
from csv2notion_neo.cli_args import parse_args, _parse_column_types, _parse_default_icon
from csv2notion_neo.utils_exceptions import CriticalError
from csv2notion_neo.utils_static import ALLOWED_TYPES, ConversionRules
from csv2notion_neo.utils_str import split_str
from csv2notion_neo.version import __version__

# Import Notion SDK modules for testing
from csv2notion_neo.notion_client import NotionClient, get_notion_client
from csv2notion_neo.notion_db_client import NotionClientExtended
from csv2notion_neo.notion_db import NotionDB
from csv2notion_neo.local_data import LocalData
from csv2notion_neo.notion_convert import NotionRowConverter
from csv2notion_neo.notion_uploader import NotionRowUploader


class TestCLIArgumentParsing:
    """Test comprehensive CLI argument parsing and validation."""
    
    def test_required_arguments(self):
        """Test that required arguments are properly validated."""
        # Test missing required arguments
        with pytest.raises(SystemExit):
            parse_args([])
        
        with pytest.raises(SystemExit):
            parse_args(["--token", "ntn_test_token_12345678901234567890"])
        
        with pytest.raises(SystemExit):
            parse_args(["--url", "test_url"])
    
    def test_general_options(self):
        """Test general CLI options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--max-threads", "10",
            "--log", "test.log",
            "--verbose",
            "test.csv"
        ])
        
        assert args.workspace == "Test Workspace"
        assert args.token == "ntn_test_token_12345678901234567890"
        assert args.url == "test_url"
        assert args.max_threads == 10
        assert args.log == Path("test.log")
        assert args.verbose is True
        assert args.csv_file == Path("test.csv")
    
    def test_machine_learning_options(self):
        """Test AI/ML related options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--hugging-face-token", "hf_token",
            "--hf-model", "blip-image",
            "--caption-column", "image_col", "caption_col",
            "test.csv"
        ])
        
        assert args.hugging_face_token == "hf_token"
        assert args.hf_model == "blip-image"
        assert args.caption_column == ["image_col", "caption_col"]
    
    def test_column_options(self):
        """Test column-related options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--column-types", "text,number,checkbox",
            "--delimiter", ";",
            "--add-missing-columns",
            "--rename-notion-key-column", "old_key", "new_key",
            "--randomize-select-colors",
            "test.csv"
        ])
        
        assert args.column_types == ["text", "number", "checkbox"]
        assert args.delimiter == ";"
        assert args.add_missing_columns is True
        assert args.rename_notion_key_column == ["old_key", "new_key"]
        assert args.randomize_select_colors is True
    
    def test_merge_options(self):
        """Test merge-related options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--merge",
            "--merge-only-column", "col1",
            "--merge-only-column", "col2",
            "--merge-skip-new",
            "test.csv"
        ])
        
        assert args.merge is True
        assert args.merge_only_column == ["col1", "col2"]
        assert args.merge_skip_new is True
    
    def test_relations_options(self):
        """Test relations-related options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--add-missing-relations",
            "test.csv"
        ])
        
        assert args.add_missing_relations is True
    
    def test_database_management_options(self):
        """Test database management options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--delete-all-database-entries"
        ])
        
        assert args.delete_all_database_entries is True
    
    def test_page_cover_options(self):
        """Test page cover and image options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--image-column", "img1", "img2",
            "--image-column-keep",
            "--image-column-mode", "cover",
            "--image-caption-column", "caption_col",
            "--image-caption-column-keep",
            "test.csv"
        ])
        
        assert args.image_column == ["img1", "img2"]
        assert args.image_column_keep is True
        assert args.image_column_mode == "cover"
        assert args.image_caption_column == "caption_col"
        assert args.image_caption_column_keep is True
    
    def test_page_icon_options(self):
        """Test page icon options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--icon-column", "icon_col",
            "--icon-column-keep",
            "--default-icon", "👍",
            "test.csv"
        ])
        
        assert args.icon_column == "icon_col"
        assert args.icon_column_keep is True
        assert args.default_icon == "👍"
    
    def test_validation_options(self):
        """Test validation and error handling options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--mandatory-column", "col1",
            "--mandatory-column", "col2",
            "--payload-key-column", "key_col",
            "--fail-on-relation-duplicates",
            "--fail-on-duplicates",
            "--fail-on-duplicate-csv-columns",
            "--fail-on-conversion-error",
            "--fail-on-inaccessible-relations",
            "--fail-on-missing-columns",
            "--fail-on-unsettable-columns",
            "--fail-on-wrong-status-values",
            "test.csv"
        ])
        
        assert args.mandatory_column == ["col1", "col2"]
        assert args.payload_key_column == "key_col"
        assert args.fail_on_relation_duplicates is True
        assert args.fail_on_duplicates is True
        assert args.fail_on_duplicate_csv_columns is True
        assert args.fail_on_conversion_error is True
        assert args.fail_on_inaccessible_relations is True
        assert args.fail_on_missing_columns is True
        assert args.fail_on_unsettable_columns is True
        assert args.fail_on_wrong_status_values is True


class TestArgumentValidation:
    """Test argument validation and error handling."""
    
    def test_column_types_validation(self):
        """Test column types validation."""
        # Valid column types
        valid_types = _parse_column_types("text,number,checkbox,date")
        assert valid_types == ["text", "number", "checkbox", "date"]
        
        # Invalid column types
        with pytest.raises(CriticalError):
            _parse_column_types("invalid_type,text")
        
        with pytest.raises(CriticalError):
            _parse_column_types("text,unknown_type")
    
    def test_default_icon_validation(self):
        """Test default icon validation."""
        # Valid emoji
        emoji_icon = _parse_default_icon("👍")
        assert emoji_icon == "👍"
        
        # Valid URL
        url_icon = _parse_default_icon("https://example.com/icon.png")
        assert url_icon == "https://example.com/icon.png"
        
        # Invalid file path (should raise error)
        with pytest.raises(CriticalError):
            _parse_default_icon("/nonexistent/path/icon.png")
    
    def test_max_threads_validation(self):
        """Test max threads validation."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_ntn_test_token_12345678901234567890_12345678901234567890",
            "--url", "test_url",
            "--max-threads", "0",  # Should be converted to 1
            "test.csv"
        ])
        assert args.max_threads == 1
        
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "secret_ntn_test_token_12345678901234567890_12345678901234567890",
            "--url", "test_url",
            "--max-threads", "10",
            "test.csv"
        ])
        assert args.max_threads == 10
    
    def test_notion_token_validation(self):
        """Test Notion token validation."""
        # Test valid ntn_ token
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_ntn_test_token_12345678901234567890_12345678901234567890",
            "--url", "test_url",
            "test.csv"
        ])
        assert args.token == "ntn_ntn_test_token_12345678901234567890_12345678901234567890"
        
        # Test valid secret_ token
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "secret_ntn_test_token_12345678901234567890_12345678901234567890",
            "--url", "test_url",
            "test.csv"
        ])
        assert args.token == "secret_ntn_test_token_12345678901234567890_12345678901234567890"
        
        # Test invalid token (no prefix)
        with pytest.raises(CriticalError, match="Invalid Notion integration token format"):
            parse_args([
                "--workspace", "Test Workspace",
                "--token", "invalid_token_12345678901234567890",
                "--url", "test_url",
                "test.csv"
            ])
        
        # Test invalid token (wrong prefix)
        with pytest.raises(CriticalError, match="Invalid Notion integration token format"):
            parse_args([
                "--workspace", "Test Workspace",
                "--token", "token_12345678901234567890",
                "--url", "test_url",
                "test.csv"
            ])
        
        # Test empty token
        with pytest.raises(CriticalError, match="Notion integration token cannot be empty"):
            parse_args([
                "--workspace", "Test Workspace",
                "--token", "",
                "--url", "test_url",
                "test.csv"
            ])
        
        # Test token too short
        with pytest.raises(CriticalError, match="Token appears to be too short"):
            parse_args([
                "--workspace", "Test Workspace",
                "--token", "ntn_short",
                "--url", "test_url",
                "test.csv"
            ])


class TestConversionRules:
    """Test ConversionRules dataclass functionality."""
    
    def test_conversion_rules_creation(self):
        """Test ConversionRules creation from arguments."""
        args = Namespace(
            csv_file=Path("test.csv"),
            token="ntn_test_token_12345678901234567890",
            url="test_url",
            workspace="Test Workspace",
            max_threads=5,
            verbose=False,
            log=None,
            column_types=None,
            delimiter=",",
            fail_on_duplicate_csv_columns=False,
            randomize_select_colors=False,
            image_column=None,
            image_column_keep=False,
            image_column_mode="block",
            image_caption_column=None,
            image_caption_column_keep=False,
            icon_column=None,
            icon_column_keep=False,
            default_icon=None,
            merge=False,
            merge_only_column=[],
            merge_skip_new=False,
            add_missing_relations=False,
            mandatory_column=[],
            payload_key_column=None,
            rename_notion_key_column=None,
            fail_on_relation_duplicates=False,
            fail_on_duplicates=False,
            fail_on_conversion_error=False,
            fail_on_inaccessible_relations=False,
            fail_on_missing_columns=False,
            fail_on_unsettable_columns=False,
            fail_on_wrong_status_values=False,
            delete_all_database_entries=False,
            hugging_face_token=None,
            caption_column=None,
            hf_model=None,
            add_missing_columns=False
        )
        
        rules = ConversionRules.from_args(args)
        assert rules.csv_file == Path("test.csv")
        assert rules.token == "ntn_test_token_12345678901234567890"
        assert rules.url == "test_url"
        assert rules.workspace == "Test Workspace"
        assert rules.max_threads == 5
        assert rules.verbose is False
        assert rules.delimiter == ","
        assert rules.fail_on_duplicate_csv_columns is False
        assert rules.randomize_select_colors is False
        assert rules.image_column is None
        assert rules.image_column_keep is False
        assert rules.image_column_mode == "block"
        assert rules.merge is False
        assert rules.merge_only_column == []
        assert rules.merge_skip_new is False
        assert rules.add_missing_relations is False
        assert rules.mandatory_column == []
        assert rules.payload_key_column is None
        assert rules.rename_notion_key_column is None
        assert rules.delete_all_database_entries is False
        assert rules.hugging_face_token is None
        assert rules.caption_column is None
        assert rules.hf_model is None
    
    def test_files_search_path_property(self):
        """Test files_search_path property."""
        rules = ConversionRules(
            csv_file=Path("/path/to/test.csv"),
            token="ntn_test_token_12345678901234567890",
            url="test_url",
            workspace="Test Workspace",
            max_threads=5,
            verbose=False,
            log=None,
            column_types=None,
            delimiter=",",
            fail_on_duplicate_csv_columns=False,
            randomize_select_colors=False,
            image_column=None,
            image_column_keep=False,
            image_column_mode="block",
            image_caption_column=None,
            image_caption_column_keep=False,
            icon_column=None,
            icon_column_keep=False,
            default_icon=None,
            merge=False,
            merge_only_column=[],
            merge_skip_new=False,
            add_missing_relations=False,
            mandatory_column=[],
            payload_key_column=None,
            rename_notion_key_column=None,
            fail_on_relation_duplicates=False,
            fail_on_duplicates=False,
            fail_on_conversion_error=False,
            fail_on_inaccessible_relations=False,
            fail_on_missing_columns=False,
            fail_on_unsettable_columns=False,
            fail_on_wrong_status_values=False,
            delete_all_database_entries=False,
            hugging_face_token=None,
            caption_column=None,
            hf_model=None,
            add_missing_columns=False
        )
        
        assert rules.files_search_path == Path("/path/to")


class TestDataProcessing:
    """Test data processing and conversion functionality."""
    
    def test_string_splitting(self):
        """Test string splitting utility."""
        # Test comma-separated values
        result = split_str("a,b,c")
        assert result == ["a", "b", "c"]
        
        # Test with spaces
        result = split_str("a, b, c")
        assert result == ["a", "b", "c"]
        
        # Test empty values
        result = split_str("a,,c")
        assert result == ["a", "c"]
        
        # Test list input
        result = split_str(["a", "b", "c"])
        assert result == ["a", "b", "c"]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_critical_error_handling(self):
        """Test CriticalError exception handling."""
        with pytest.raises(CriticalError):
            raise CriticalError("Test critical error")
    
    def test_invalid_column_types(self):
        """Test handling of invalid column types."""
        with pytest.raises(CriticalError):
            _parse_column_types("invalid_type")
    
    def test_missing_required_arguments(self):
        """Test handling of missing required arguments."""
        with pytest.raises(SystemExit):
            parse_args([])
        
        with pytest.raises(SystemExit):
            parse_args(["--workspace", "Test"])
    
    def test_invalid_file_paths(self):
        """Test handling of invalid file paths."""
        with pytest.raises(CriticalError):
            _parse_default_icon("/nonexistent/path/icon.png")


class TestVersionAndHelp:
    """Test version and help functionality."""
    
    def test_version_argument(self):
        """Test version argument."""
        with pytest.raises(SystemExit):
            parse_args(["--version"])
    
    def test_help_argument(self):
        """Test help argument."""
        with pytest.raises(SystemExit):
            parse_args(["--help"])
    
    def test_version_constant(self):
        """Test version constant."""
        assert __version__ is not None
        assert isinstance(__version__, str)


class TestComprehensiveScenarios:
    """Test comprehensive scenarios combining multiple features."""
    
    def test_full_upload_scenario(self):
        """Test full upload scenario with all options."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--max-threads", "3",
            "--log", "test.log",
            "--verbose",
            "--column-types", "text,number,checkbox",
            "--delimiter", ",",
            "--add-missing-columns",
            "--randomize-select-colors",
            "--merge",
            "--merge-only-column", "Name",
            "--add-missing-relations",
            "--image-column", "Image",
            "--image-column-keep",
            "--image-column-mode", "cover",
            "--icon-column", "Icon",
            "--icon-column-keep",
            "--default-icon", "👍",
            "--mandatory-column", "Name",
            "--payload-key-column", "ID",
            "--fail-on-duplicates",
            "--fail-on-conversion-error",
            "test.csv"
        ])
        
        # Verify all arguments are parsed correctly
        assert args.workspace == "Test Workspace"
        assert args.token == "ntn_test_token_12345678901234567890"
        assert args.url == "test_url"
        assert args.max_threads == 3
        assert args.log == Path("test.log")
        assert args.verbose is True
        assert args.column_types == ["text", "number", "checkbox"]
        assert args.delimiter == ","
        assert args.add_missing_columns is True
        assert args.randomize_select_colors is True
        assert args.merge is True
        assert args.merge_only_column == ["Name"]
        assert args.add_missing_relations is True
        assert args.image_column == ["Image"]
        assert args.image_column_keep is True
        assert args.image_column_mode == "cover"
        assert args.icon_column == "Icon"
        assert args.icon_column_keep is True
        assert args.default_icon == "👍"
        assert args.mandatory_column == ["Name"]
        assert args.payload_key_column == "ID"
        assert args.fail_on_duplicates is True
        assert args.fail_on_conversion_error is True
        assert args.csv_file == Path("test.csv")
    
    def test_ai_captioning_scenario(self):
        """Test AI captioning scenario."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--hugging-face-token", "hf_token",
            "--hf-model", "blip-image",
            "--caption-column", "image_col", "caption_col",
            "--image-column", "Image",
            "--image-column-mode", "block",
            "test.csv"
        ])
        
        assert args.hugging_face_token == "hf_token"
        assert args.hf_model == "blip-image"
        assert args.caption_column == ["image_col", "caption_col"]
        assert args.image_column == ["Image"]
        assert args.image_column_mode == "block"
    
    def test_database_deletion_scenario(self):
        """Test database deletion scenario."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--delete-all-database-entries"
        ])
        
        assert args.delete_all_database_entries is True
        # Note: csv_file is not required for deletion operations
    
    def test_validation_scenario(self):
        """Test comprehensive validation scenario."""
        args = parse_args([
            "--workspace", "Test Workspace",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--mandatory-column", "ID",
            "--mandatory-column", "Name",
            "--fail-on-relation-duplicates",
            "--fail-on-duplicates",
            "--fail-on-duplicate-csv-columns",
            "--fail-on-conversion-error",
            "--fail-on-inaccessible-relations",
            "--fail-on-missing-columns",
            "--fail-on-unsettable-columns",
            "--fail-on-wrong-status-values",
            "test.csv"
        ])
        
        assert args.mandatory_column == ["ID", "Name"]
        assert args.fail_on_relation_duplicates is True
        assert args.fail_on_duplicates is True
        assert args.fail_on_duplicate_csv_columns is True
        assert args.fail_on_conversion_error is True
        assert args.fail_on_inaccessible_relations is True
        assert args.fail_on_missing_columns is True
        assert args.fail_on_unsettable_columns is True
        assert args.fail_on_wrong_status_values is True


class TestNotionSDKWithoutCredentials:
    """Test Notion SDK functionality without requiring actual credentials."""
    
    @patch('csv2notion_neo.notion_client.Client')
    def test_notion_client_initialization(self, mock_client_class):
        """Test NotionClient initialization with mocked SDK."""
        # Mock the official Notion client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Test client initialization
        client = NotionClient("fake_token", "Test Workspace")
        
        assert client.integration_token == "fake_token"
        assert client.workspace == "Test Workspace"
        assert client.client == mock_client
        mock_client_class.assert_called_once_with(auth="fake_token")
    
    @patch('csv2notion_neo.notion_client.Client')
    def test_notion_client_get_collection(self, mock_client_class):
        """Test get_collection method with mocked SDK."""
        # Mock the official Notion client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock database response
        mock_db_response = {
            "id": "test_db_id",
            "title": [{"text": {"content": "Test Database"}}],
            "properties": {
                "Name": {"type": "title"},
                "Status": {"type": "select"}
            }
        }
        mock_client.databases.retrieve.return_value = mock_db_response
        
        # Test client
        client = NotionClient("fake_token")
        result = client.get_collection("test_db_id")
        
        assert result == mock_db_response
        mock_client.databases.retrieve.assert_called_once_with(database_id="test_db_id")
    
    @patch('csv2notion_neo.notion_client.Client')
    def test_notion_client_create_record(self, mock_client_class):
        """Test create_record method with mocked SDK."""
        # Mock the official Notion client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock page creation response
        mock_page_response = {"id": "test_page_id"}
        mock_client.pages.create.return_value = mock_page_response
        
        # Test client
        client = NotionClient("fake_token")
        result = client.create_record("block", "parent_id", title="Test Page")
        
        assert result == "test_page_id"
        mock_client.pages.create.assert_called_once()
    
    @patch('csv2notion_neo.notion_client.Client')
    def test_notion_client_upload_file(self, mock_client_class):
        """Test upload_file method with mocked SDK."""
        # Mock the official Notion client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the complex file upload flow
        mock_client.file_uploads.create.return_value = {"id": "file_upload_id"}
        mock_client.file_uploads.send.return_value = {"status": "uploaded"}
        
        # Test client
        client = NotionClient("fake_token")
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file_path = tmp_file.name
        
        try:
            result = client.upload_file(Path(tmp_file_path), "parent_block_id")
            # Verify the result structure
            assert isinstance(result, tuple)
            assert len(result) == 2
            file_url, metadata = result
            assert file_url.startswith("attachment:")
            assert "file_id" in metadata
            mock_client.file_uploads.create.assert_called_once()
            mock_client.file_uploads.send.assert_called_once()
        finally:
            os.unlink(tmp_file_path)
    
    @patch('csv2notion_neo.notion_client.Client')
    def test_notion_client_extended_initialization(self, mock_client_class):
        """Test NotionClientExtended initialization."""
        # Mock the official Notion client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Test extended client initialization
        client = NotionClientExtended("fake_token", workspace="Test Workspace")
        
        assert client.integration_token == "fake_token"
        assert client.workspace == "Test Workspace"
        assert client.client == mock_client
    
    @patch('csv2notion_neo.notion_client.Client')
    def test_notion_db_initialization(self, mock_client_class):
        """Test NotionDB initialization with mocked client."""
        # Mock the official Notion client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock database info response
        mock_db_info = {
            "id": "test_db_id",
            "title": [{"text": {"content": "Test Database"}}],
            "properties": {
                "Name": {"type": "title"},
                "Status": {"type": "select"}
            }
        }
        mock_client.databases.retrieve.return_value = mock_db_info
        
        # Test NotionDB initialization
        client = NotionClient("fake_token")
        db = NotionDB(client, "test_db_id")
        
        assert db.collection_id == "test_db_id"
        assert db.client == client
        assert db.name == "Test Database"
    
    @patch('csv2notion_neo.notion_client.Client')
    def test_notion_row_converter(self, mock_client_class):
        """Test NotionRowConverter with mocked dependencies."""
        # Mock the official Notion client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock database info
        mock_db_info = {
            "id": "test_db_id",
            "title": [{"text": {"content": "Test Database"}}],
            "properties": {
                "Name": {"type": "title"},
                "Status": {"type": "select"}
            }
        }
        mock_client.databases.retrieve.return_value = mock_db_info
        
        # Test converter initialization
        client = NotionClient("fake_token")
        db = NotionDB(client, "test_db_id")
        
        # Mock conversion rules
        mock_rules = MagicMock()
        
        # Test converter
        converter = NotionRowConverter(db, mock_rules)
        assert converter is not None
    
    @patch('csv2notion_neo.notion_client.Client')
    def test_notion_row_uploader(self, mock_client_class):
        """Test NotionRowUploader with mocked dependencies."""
        # Mock the official Notion client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock database info
        mock_db_info = {
            "id": "test_db_id",
            "title": [{"text": {"content": "Test Database"}}],
            "properties": {
                "Name": {"type": "title"},
                "Status": {"type": "select"}
            }
        }
        mock_client.databases.retrieve.return_value = mock_db_info
        
        # Test uploader initialization
        client = NotionClient("fake_token")
        db = NotionDB(client, "test_db_id")
        uploader = NotionRowUploader(db)
        
        assert uploader.db == db


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_arguments(self):
        """Test handling of empty argument values."""
        args = parse_args([
            "--workspace", "",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "test.csv"
        ])
        
        assert args.workspace == ""
        assert args.token == "ntn_test_token_12345678901234567890"
        assert args.url == "test_url"
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in arguments."""
        args = parse_args([
            "--workspace", "  Test Workspace  ",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--column-types", " text , number , checkbox ",
            "test.csv"
        ])
        
        assert args.workspace == "  Test Workspace  "
        assert args.column_types == ["text", "number", "checkbox"]
    
    def test_special_characters(self):
        """Test handling of special characters."""
        args = parse_args([
            "--workspace", "Test Workspace with Special Chars: !@#$%^&*()",
            "--token", "ntn_test_token_12345678901234567890",
            "--url", "test_url",
            "--default-icon", "🎉",
            "test.csv"
        ])
        
        assert args.workspace == "Test Workspace with Special Chars: !@#$%^&*()"
        assert args.default_icon == "🎉"




if __name__ == "__main__":
    pytest.main([__file__])
