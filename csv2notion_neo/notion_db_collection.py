import random
from typing import Any, Dict, List, Optional, Tuple, cast

from csv2notion_neo.notion.collection import Collection, NotionSelect, CollectionRowBlock, CalendarView
from csv2notion_neo.notion.operations import build_operation

from csv2notion_neo.notion_row import CollectionRowBlockExtended
from csv2notion_neo.utils_db import make_status_column
from csv2notion_neo.utils_rand_id import rand_id_unique
from icecream import ic

class CollectionExtended(Collection):
    def get_rows(self) -> List[CollectionRowBlockExtended]:  # noqa: WPS615
        return [
            CollectionRowBlockExtended(row._client, row._id)
            for row in super().get_rows()
        ]

    def get_unique_rows(self) -> Dict[str, CollectionRowBlockExtended]:
        rows: Dict[str, CollectionRowBlockExtended] = {}

        # sort rows so that only first row is kept if multiple have same title
        sorted_rows = sorted(self.get_rows(), key=lambda r: str(r.title))

        for row in sorted_rows:
            rows.setdefault(row.title, row)
        
        return rows

    def add_row_block(
        self,
        update_views: bool = True,
        row_class: Optional[type] = None,
        properties: Optional[Dict[str, Any]] = None,
        columns: Optional[Dict[str, Any]] = None,
    ) -> CollectionRowBlockExtended:
        row_class = row_class or CollectionRowBlockExtended

        new_row = self._add_row_block(
            update_views=update_views,
            row_class=row_class,
            properties=properties,
            columns=columns,
        )

        return cast(CollectionRowBlockExtended, new_row)

    def _add_row_block(
        self,
        update_views: bool = True,
        row_class: Optional[type] = None,
        properties: Optional[Dict[str, Any]] = None,
        columns: Optional[Dict[str, Any]] = None,
    ) -> CollectionRowBlock:
        """
        Create a new empty CollectionRowBlock under this collection, and return the instance.
        """

        row_class = row_class or CollectionRowBlock

        row_id = self._client.create_record("block", self, type="page")
        row = row_class(self._client, row_id)

        columns = {} if columns is None else columns
        properties = {} if properties is None else properties

        with self._client.as_atomic_transaction():
            for key, val in properties.items():
                setattr(row, key, val)

        
            for key, val in columns.items():
                setattr(row.columns, key, val)

            if update_views:
                # make sure the new record is inserted at the end of each view
                for view in self.parent.views:
                    if view is None or isinstance(view, CalendarView):
                        continue

                    page_sort = view.get("page_sort", [])

                    if not page_sort:
                        view.set("page_sort", [row_id])
                    else:
                        last_element = page_sort[-1]
                        self._client.submit_transaction(
                            build_operation(
                                id=view.id,
                                path=["page_sort"],
                                args={"id": row_id, "after": last_element},
                                command="listAfter",
                                table=view._table,
                            )
                        )

        return row

    def add_column(self, column_name: str, column_type: str) -> None:
        schema_raw = self.get("schema")
        new_id = rand_id_unique(4, schema_raw)
        schema_raw[new_id] = {"name": column_name, "type": column_type}

        if column_type == "status":
            schema_raw[new_id].update(make_status_column())

        self.set("schema", schema_raw)

    def has_duplicates(self) -> bool:
        row_titles = [row.title for row in self.get_rows()]
        return len(row_titles) != len(set(row_titles))

    def is_accessible(self) -> bool:
        rec = self._client.get_record_data("collection", self.id, force_refresh=True)
        return rec is not None

    def check_schema_select_options(  # noqa: WPS210
        self, prop: Dict[str, Any], values: Any  # noqa: WPS110
    ) -> Tuple[bool, Dict[str, Any]]:
        schema_update = False

        prop_options = prop.setdefault("options", [])
        current_options = [p["value"].lower() for p in prop_options]
        if not isinstance(values, list):
            values = [values]  # noqa: WPS110

        for v in values:
            if v and v.lower() not in current_options:
                schema_update = True

                if self._client.options.get("is_randomize_select_colors") is True:
                    color = _get_random_select_color()
                else:
                    color = "default"

                prop_options.append(NotionSelect(v, color).to_dict())
        return schema_update, prop


def _get_random_select_color() -> str:
    return str(random.choice(NotionSelect.valid_colors))  # noqa: S311
