# csv2notion

[![PyPI version](https://img.shields.io/pypi/v/csv2notion?label=version)](https://pypi.python.org/pypi/csv2notion)
[![Python Version](https://img.shields.io/pypi/pyversions/csv2notion.svg)](https://pypi.org/project/csv2notion/)
[![tests](https://github.com/vzhd1701/csv2notion/actions/workflows/test.yml/badge.svg)](https://github.com/vzhd1701/csv2notion/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/vzhd1701/csv2notion/branch/master/graph/badge.svg)](https://codecov.io/gh/vzhd1701/csv2notion)

An alternative way to import `*.csv` files to [Notion.so](https://notion.so).

Due to current limitations of the official Notion SDK this tool is using the unofficial SDK by **Jamie Alexandre** [notion-py](https://github.com/jamalex/notion-py).

### Advantages over native import

- Actually merge CSV with existing database rows (not just add new ones), first column will be used as a key
- Manually set column types instead of relying on autodetection
- Automatically link or create new entries in relation columns based on their value
- Set icon for each row
- Set cover or embed image for each row
- Upload image file used for cover or icon
- Options for validation of input data

### Disadvantages over native import

- Slower speed, since every row is imported separately
  - this is mitigated by multithreaded upload

## Installation

[**Download the latest binary release**](https://github.com/vzhd1701/csv2notion/releases/latest) for your OS.

### With PIP

```bash
$ pip install csv2notion
```

**Python 3.7 or later required.**

Or, since **csv2notion** is a standalone tool, it might be more convenient to install it using [**pipx**](https://github.com/pipxproject/pipx):

```shell
$ pipx install csv2notion
```

### From source

This project uses [poetry](https://python-poetry.org/) for dependency management and packaging. You will have to install it first. See [poetry official documentation](https://python-poetry.org/docs/) for instructions.

```shell
$ git clone https://github.com/vzhd1701/csv2notion.git
$ cd csv2notion/
$ poetry install --no-dev
$ poetry run csv2notion
```

## Usage

```shell
$ csv2notion --help
usage: csv2notion [-h] --token TOKEN [--url URL] [--max-threads NUMBER] [--custom-types TYPES] [--image-column COLUMN] [--image-column-keep] [--image-column-mode {cover,block}] [--image-caption-column COLUMN]
                  [--image-caption-column-keep] [--icon-column COLUMN] [--icon-column-keep] [--default-icon ICON] [--missing-columns-action {add,ignore,fail}] [--missing-relations-action {add,ignore,fail}]
                  [--fail-on-relation-duplicates] [--fail-on-duplicates] [--fail-on-duplicate-csv-columns] [--fail-on-conversion-error] [--fail-on-inaccessible-relations] [--merge] [--merge-only-column COLUMN]
                  [--mandatory-column COLUMN] [--log FILE] [--verbose] [--version]
                  FILE

Import/Merge CSV file into Notion database

positional arguments:
  FILE                  CSV file to upload

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN         Notion token, stored in token_v2 cookie for notion.so [NEEDED FOR UPLOAD]
  --url URL             Notion database URL; if none is provided, will create a new database
  --max-threads NUMBER  upload threads (default: 5)
  --custom-types TYPES  comma-separated list of custom types to use for non-key columns; if none is provided, types will be guessed from CSV values (used when creating a new database or --missing-columns-action is set to 'add')
  --image-column COLUMN
                        CSV column that points to URL or image file that will be embedded for that row
  --image-column-keep   keep image CSV column as a Notion DB column
  --image-column-mode {cover,block}
                        upload image as [cover] or insert it as [block] (default: block)
  --image-caption-column COLUMN
                        CSV column that points to text caption that will be added to the image block if --image-column-mode is set to 'block'
  --image-caption-column-keep
                        keep image caption CSV column as a Notion DB column
  --icon-column COLUMN  CSV column that points to emoji, URL or image file that will be used as page icon for that row
  --icon-column-keep    keep icon CSV column as a Notion DB column
  --default-icon ICON   Emoji, URL or image file that will be used as page icon for every row by default
  --missing-columns-action {add,ignore,fail}
                        if columns are present in CSV but not in Notion DB, [add] them to Notion DB, [ignore] them or [fail] (default: ignore)
  --missing-relations-action {add,ignore,fail}
                        if entries are missing from linked Notion DB, [add] them to Notion DB, [ignore] them or [fail] (default: ignore)
  --fail-on-relation-duplicates
                        fail if any linked DBs in relation columns have duplicate entries; otherwise, first entry in alphabetical order will be treated as unique when looking up relations
  --fail-on-duplicates  fail if Notion DB or CSV has duplicates in key column, useful when sanitizing before merge to avoid ambiguous mapping
  --fail-on-duplicate-csv-columns
                        fail if CSV has duplicate columns; otherwise last column will be used
  --fail-on-conversion-error
                        fail if any column type conversion error occurs; otherwise errors will be replaced with empty strings
  --fail-on-inaccessible-relations
                        fail if any relation column points to a Notion DB that is not accessible to the current user; otherwise those columns will be ignored
  --merge               merge CSV with existing Notion DB rows, first column will be used as a key
  --merge-only-column COLUMN
                        CSV column that should be updated on merge; when provided, other columns will be ignored (define multiple times for multiple columns)
  --mandatory-column COLUMN
                        CSV column that cannot be empty (define multiple times for multiple columns)
  --log FILE            file to store program log
  --verbose             output debug information
  --version             show program's version number and exit
```

### Input

You must pass a single `*.csv` file for upload. The CSV file must contain at least 2 rows. The first row will be used as a header.

Optionally you can provide a URL to an existing Notion database with the `--url` option; if not provided, the tool will create a new database named after the CSV file. The URL must link [to a database view](https://github.com/vzhd1701/csv2notion/raw/master/examples/db_link.png), not a page.

The tool also requires you to provide a `token_v2` cookie for the Notion website through `--token` option. For information on how to get it, see [this article](https://vzhd1701.notion.site/Find-Your-Notion-Token-5f57951434c1414d84ac72f88226eede).

### Upload speed

Due to API limitations, the upload is performed one row at a time. To speed things up, this tool uses multiple parallel threads. Use the `--max-threads` option to control how fast it will go. Try not to set it too high to avoid rate limiting by the Notion server.

### Duplicate CSV columns

Notion does not allow the database to have multiple columns with the same name. Therefore CSV columns will be treated as unique. Only the **last** column will be used if CSV has multiple columns with the same name. If you want the program to stop if it finds duplicate columns, use the `--fail-on-duplicate-csv-columns` flag.

### Missing columns

If a CSV file has columns not present in Notion DB, they will be ignored by default. You can change this by using the `--missing-columns-action` option. Set it to `add` if you want the tool to add missing columns into Notion DB. Set to `fail` if you want the program to stop if it finds a column mismatch.

### Column types

By default, the tool will try to guess column types based on their content. Alternatively, you can provide a comma-separated list of column types with the `--custom-types` option when creating a new database or adding new columns with the `--missing-columns-action` option set to `add`. Since the first column in Notion DB is always text, the tool will use the list to set types for the rest of the columns.

If the tool cannot convert the column value type properly, it will replace it with an empty string. If you want to make sure all values are correctly converted, use the `--fail-on-conversion-error` flag, which will stop execution in case of a conversion error.

### Merging

By default, the tool will add rows to the existing Notion DB. To merge CSV rows with the Notion database, use the `--merge` flag. The first column of CSV and Notion DB will be used as a key to update existing rows with new values. CSV rows that didn't have a match in Notion DB will be added as new.

Since the tool treats rows as unique during merge based on the key column, it will use first found rows with a unique key. To avoid this ambiguity, you might want to validate duplicate row keys with the `--fail-on-duplicates` flag. It will check both CSV and target Notion DB before the merge.

If you want only select columns to be updated, use the `--merge-only-column` option.

### Relation columns

Notion database has a relation column type, which allows you to link together entries from different databases. The tool will try to match column data with keys from a linked database.

By default, it will match with the first found row; if it cannot find the match, it will add nothing. You can change this behavior with the `--missing-relations-action` option. Set it to `add` if you want the tool to create new entries in the linked DB if no match is found. Set it to `fail` if you want the program to stop if no match is found.

Since the tool treats rows in the linked DB as unique you can prevent ambiguous matching with the `--fail-on-relation-duplicates` flag. It will check linked DB for duplicate keys and stop the executions if it finds any.

If linked DB is not accessible, columns that point to it will be ignored. If you prefer the program to stop in this case, use the `--fail-on-inaccessible-relations` flag.

### Cover image / Embedded image

The tool allows you to add an image to each row with the `--image-column` option. It will use one column from CSV as a data source for the image. It can be either a URL or a file name. The file name must be either an absolute path or a path relative to the CSV file. The tool will upload the file to the Notion server.

By default, the tool will embed an image inside the row page. If you want it to use the image as a page cover, then set the `--image-column-mode` option to `cover`.

Column specified with the `--image-column` option will not be treated as a regular column by default. If you want it to appear in Notion DB, use the `--image-column-keep` flag.

To add custom caption to image block uploaded with `--image-column-mode` set to `block`, use `--image-caption-colum` option. To also keep the caption as a Notion DB column, use `--image-caption-column-keep` flag.

### Icon

The tool allows you to add an icon to each row with the `--icon-column` option. The behavior is the same as with `--image-column`; the only difference is that you can use URL, file name, or single emoji.

To also treat `--icon-column` as a regular column, use `--icon-column-keep` flag, similar to `--image-column-keep`.

If you want to set the same icon for each row, use the `--default-icon` option. If both `--icon-column` and `--default-icon` are present, the default icon is used if the row doesn't have anything in the icon column.

### Mandatory columns

If you want to ensure that specific columns always have value and are not allowed to be empty, then use the `--mandatory-column` option. The program execution will stop if validation fails.

## Examples

- [Importing CSV into new DB](https://github.com/vzhd1701/csv2notion/raw/master/examples/new_db.png)
- [Using custom column types](https://github.com/vzhd1701/csv2notion/raw/master/examples/new_db_types.png)
- [Importing CSV into existing DB](https://github.com/vzhd1701/csv2notion/raw/master/examples/add_new.png)
- [Merging CSV with existing DB](https://github.com/vzhd1701/csv2notion/raw/master/examples/merge.png)
- [Merging CSV with select columns in existing DB](https://github.com/vzhd1701/csv2notion/raw/master/examples/merge_only.png)
- [Importing rows with images](https://github.com/vzhd1701/csv2notion/raw/master/examples/image_column.png)
- [Importing rows with emoji icons](https://github.com/vzhd1701/csv2notion/raw/master/examples/icon_column.png)
- [Updating emoji icon only for all rows](https://github.com/vzhd1701/csv2notion/raw/master/examples/default_icon_only.png)

## Getting help

If you found a bug or have a feature request, please [open a new issue](https://github.com/vzhd1701/csv2notion/issues/new/choose).

If you have a question about the program or have difficulty using it, you are welcome to [the discussions page](https://github.com/vzhd1701/csv2notion/discussions). You can also mail me directly, I'm always happy to help.
