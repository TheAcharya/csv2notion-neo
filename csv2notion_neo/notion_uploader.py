from dataclasses import dataclass
from typing import Any, Dict

from csv2notion_neo.notion_db import NotionDB
from csv2notion_neo.notion_row import CollectionRowBlockExtended
from icecream import ic
from csv2notion_neo.utils_ai import AI

@dataclass
class NotionUploadRow(object):
    columns: Dict[str, Any]
    properties: Dict[str, Any]

    def key(self) -> str:
        if "payload_key_column" in self.properties:
            if self.properties["payload_key_column"]:
                return str(self.columns[self.properties["payload_key_column"]])
        return str(list(self.columns.values())[0])

class NotionRowUploader(object):
    def __init__(self, db: NotionDB):
        self.db = db

    def upload_row(self, row: NotionUploadRow, is_merge: bool) -> None:

        #CHECK
        if 'AI' in row.properties:
            ai_client = AI(row.properties['AI'])
            row.columns = ai_client.out(row.columns)
        #row.columns['ai caption'] = '2'
        post_properties = _extract_post_properties(row.properties)

        db_row = self._get_db_row(row, is_merge)

        # these need to be updated after
        # because they can't be updated in atomic transaction
        for prop, prop_val in post_properties.items():
            setattr(db_row, prop, prop_val)

    def _get_db_row(
        self, row: NotionUploadRow, is_merge: bool
    ) -> CollectionRowBlockExtended:
      
        existing_row = self.db.rows.get(row.key()) if is_merge else None

        if is_merge and existing_row:
            cur_row = existing_row
            cur_row.update(properties=row.properties, columns=row.columns)
        else:
            cur_row = self.db.add_row(properties=row.properties, columns=row.columns)
        return cur_row


def _extract_post_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
    return {
        p: properties.pop(p)
        for p in properties.copy()
        if p in {"cover_block", "cover_block_caption", "last_edited_time","cover"}
    }
