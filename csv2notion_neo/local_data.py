import csv
import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional

from csv2notion_neo.notion_type_guess import guess_type_by_values
from csv2notion_neo.utils_exceptions import CriticalError
from icecream import ic

CSVRowType = Dict[str, str]

logger = logging.getLogger(__name__)


def data_read(file_path: Path, fail_on_duplicate_columns: bool) -> List[CSVRowType]:
    suffix = Path(file_path).suffix

    if "csv" in suffix:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as csv_file:
                return _csv_read_rows(csv_file, fail_on_duplicate_columns)
        except FileNotFoundError as e:
            raise CriticalError(f"File {file_path} not found") from e
    elif "json" in suffix:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as json_file:
                return _json_read_rows(json_file, fail_on_duplicate_columns)
        except FileNotFoundError as e:
            raise CriticalError(f"File {file_path} not found") from e

    else:
        raise CriticalError(f"{suffix} file extension not supported!")


def _csv_read_rows(
    csv_file: Iterable[str], fail_on_duplicate_columns: bool
) -> List[CSVRowType]:
    reader = csv.DictReader(csv_file, restval="")

    if not reader.fieldnames:
        raise CriticalError("CSV file has no columns.")

    duplicate_columns = _list_duplicates(list(reader.fieldnames))

    if duplicate_columns:
        message = f"Duplicate columns found in CSV: {duplicate_columns}."

        if fail_on_duplicate_columns:
            raise CriticalError(message)

        logger.warning(message)

    rows = list(reader)

    if rows and None in rows[0]:
        logger.warning(
            "Inconsistent number of columns detected."
            " Excess columns will be truncated."
        )
        rows = [_drop_dict_columns(row, [None]) for row in rows]

    return rows

def _json_read_rows(
    json_file: Iterable[str], fail_on_duplicate_columns: bool
) -> List[CSVRowType]:
    reader = json.load(json_file)

    if not reader:
        raise CriticalError("JSON file has no data")

    rows = list(reader)
    rows = [_convert_int_to_string(row) for row in rows]

    if rows and None in rows[0]:
        logger.warning(
            "Inconsistent number of columns detected."
            " Excess columns will be truncated."
        )
        rows = [_drop_dict_columns(row, [None]) for row in rows]

    return rows

def _list_duplicates(lst: List[str]) -> List[str]:
    return [lst_item for lst_item, count in Counter(lst).items() if count > 1]


def _drop_dict_columns(
    src_dict: Dict[Any, Any], columns_to_drop: Iterable[Any]
) -> Dict[Any, Any]:
    return {k: v for k, v in src_dict.items() if k not in columns_to_drop}

def _convert_int_to_string(src_dict:Dict[Any,Any]):
    for key,val in src_dict.items():
        if type(val) == int:
            src_dict[key] = str(val)
    
    return src_dict


class LocalData(Iterable[CSVRowType]):  # noqa:  WPS214
    def __init__(
        self,
        csv_file: Path,
        column_types: Optional[List[str]] = None,
        fail_on_duplicate_columns: bool = False,
        key_col_json: str = None,
        args:dict = None
    ) -> None:
        self.csv_file = csv_file
        self.rows = data_read(self.csv_file, fail_on_duplicate_columns)
        self.key_col = key_col_json
        self.types = self._column_types(column_types)


        #ai features
        try:
            if args.hugging_face_token:
                if args.caption_column:
                    self._create_ai_columns(args.caption_column[1])
                    self.model_url = self._pick_model(args.hf_model)
                else:
                    raise Exception("ai token provided, please provide column maps to fill the ai content")

        except Exception as e:
            logger.error(f"Problem in creating AI column {e}")

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[CSVRowType]:
        yield from self.rows

    @property
    def key_column(self) -> str:
        if self.key_col:
            return self.key_col
        
        return self.columns[0]

    @property
    def content_columns(self) -> List[str]:
        if self.key_column:
            return [ele for ele in self.columns if ele != self.key_column]
        return self.columns[1:]

    @property
    def columns(self) -> List[str]:
        return list(self.rows[0].keys()) if self.rows else []

    def columns_of_type(self, col_type: str) -> List[str]:
        return [col for col in self.content_columns if self.col_type(col) == col_type]

    def col_type(self, col_name: str) -> str:
        return self.types[col_name]

    def col_values(self, col_name: str) -> List[str]:
        return [row[col_name] for row in self.rows]

    def drop_columns(self, *columns: str) -> None:
        self.rows = [_drop_dict_columns(row, columns) for row in self.rows]
        self.types = _drop_dict_columns(self.types, columns)

    def drop_rows(self, *keys: str) -> None:
        self.rows = [row for row in self.rows if row[self.key_column] not in keys]

    def _create_ai_columns(self,column_name:str) -> None:
        self.types[column_name] = 'text'
        for x in self.rows:
            x[column_name] = ''

    def _pick_model(self,model_name:str) -> str:
        model_map = {
            "vit-gpt2":"https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning",
            "blip-image":"https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
            "git-large":"https://api-inference.huggingface.co/models/microsoft/git-large"
        }

        if model_name:
            try:
                model_url = model_map[model_name]
                logger.info(f"Using model {model_name}")
            except:
                logger.error(f"{model_name} is not present! defaulting to vit-gpt2")
                model_url = model_map["vit-gpt2"]
        else:
            logger.error(f"model not provided! defaulting to vit-gpt2")
            model_url = model_map["vit-gpt2"]
        
        return model_url
    
    def _column_types(self, column_types: Optional[List[str]] = None) -> Dict[str, str]:
        
        if not column_types:
            if self.key_column:
                return {
                key: guess_type_by_values(self.col_values(key))
                for key in self.content_columns
            }
            else:
                return {
                    key: guess_type_by_values(self.col_values(key))
                    for key in self.columns[1:]
                }   

        if len(column_types) != len(self.columns) - 1:
            raise CriticalError(
                "Each column (except key) type must be defined in custom types list"
            )

        return {key: column_types[i] for i, key in enumerate(self.content_columns)}
