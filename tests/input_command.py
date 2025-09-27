from pathlib import PosixPath
from dotenv import load_dotenv
load_dotenv()
import os

ARGS_DICT = {'csv_file': PosixPath('tests/assets/notion-upload-test.json'), 
            'workspace': os.getenv("NOTION_WORKSPACE"),  
            'token': os.getenv("NOTION_TOKEN"), 
            'url': os.getenv("NOTION_URL"), 
            'max_threads': 3, 
            'log': PosixPath('tests/log.txt'), 
            'verbose': True, 
            # Ai options
            'hugging_face_token': None, 
            'hf_model': None, 
            # Column options
            'caption_column': None, 
            'column_types': None, 
            'delimiter': ',', 
            'add_missing_columns': False, 
            'rename_notion_key_column': None, 
            'randomize_select_colors': True, 
            'merge': True, 
            'merge_only_column': [], 
            'merge_skip_new': False, 
            'add_missing_relations': False, 
            # Image column options
            'image_column': ['Image Filename'], 
            'image_column_keep': True, 
            'image_column_mode': 'block', 
            'image_caption_column': None, 
            'image_caption_column_keep': False, 
            'icon_column': None, 
            'icon_column_keep': False, 
            'default_icon': None, 
            'mandatory_column': ['Marker ID'], 
            'payload_key_column': 'Marker ID', 
            # Fail on flags
            'fail_on_relation_duplicates': False, 
            'fail_on_duplicates': False, 
            'fail_on_duplicate_csv_columns': False, 
            'fail_on_conversion_error': False,
            'fail_on_inaccessible_relations': False, 
            'fail_on_missing_columns': False, 
            'fail_on_unsettable_columns': False, 
            'fail_on_wrong_status_values': False,
            # Database operations
            'delete_all_database_entries': False}