<a href="https://github.com/TheAcharya/csv2notion-neo"><img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/CSV2Notion Neo_Icon.png?raw=true" width="200" alt="App icon" align="left"/>

<div>
<h1>CSV2Notion Neo</h1>
<!-- PyPI -->
<a href="https://pypi.python.org/pypi/csv2notion-neo">
<img src="https://img.shields.io/pypi/v/csv2notion-neo?label=version" alt="PyPI"/>
</a>
<!-- Python -->
<a href="https://pypi.org/project/csv2notion-neo/">
<img src="https://img.shields.io/pypi/pyversions/csv2notion-neo.svg" alt="Python"/>
</a>
<!-- tests -->
<a href="https://github.com/TheAcharya/csv2notion-neo/actions/workflows/test.yml">
<img src="https://github.com/TheAcharya/csv2notion-neo/actions/workflows/test.yml/badge.svg" alt="tests"/>
</a>
<!-- release_github -->
<a href="https://github.com/TheAcharya/csv2notion-neo/actions/workflows/release_github.yml">
<img src="https://github.com/TheAcharya/csv2notion-neo/actions/workflows/release_github.yml/badge.svg" alt="release_github"/>
</a>
<p>
<p>An advance method to upload & merge *.csv files to <a href="https://notion.so/" target="_blank">Notion</a>. CSV2Notion Neo uses <a href="https://github.com/jamalex/notion-py" target="_blank">notion-py</a> API Library.</p>

<br>
</div>

## Core Features

### Advantages over native import

- Actually merge CSV with existing database rows (not just add new ones), first column will be used as a key
- Manually set column types instead of relying on autodetection
- Automatically link or create new entries in relation columns based on their value
- Upload files into "Files & media" column
- Set icon for each row
- Set cover or embed image for each row
- Upload image file used for cover or icon
- Options for validation of input data

### Disadvantages over native import

- Slower speed, since every row is imported separately
  - this is mitigated by multithreaded upload

## Table of contents

- [Background](#background)
- [Installation](#installation)
  - [Pre-compiled Binary (Recommended)](#pre-compiled-binary-recommended)
  - [From Source](#from-source)
- [Guide](#guide)
  - [macOS Gatekeeper & Notarization](#macos-gatekeeper--notarization)
  - [Prerequisite](#prerequisite)
  - [Upload Speed](#upload-speed)
  - [Duplicate CSV Columns](#duplicate-csv-columns)
  - [Missing Columns](#missing-columns)
  - [Column Types](#column-types)
  - [Mergin](#merging)
  - [Relation Columns](#relation-columns)
  - [Cover Image & Embedded Image](#cover-image--embedded-image)
  - [Icons](#icons)
  - [Mandatory Columns](#mandatory-columns)
- [Examples](#examples)
- [Credits](#credits)
- [License](#license)
- [Reporting Bugs](#reporting-bugs)

## Background

Originally, we developed [csv2notion](https://github.com/vzhd1701/csv2notion) to address the lack of advanced importing support for `*.csv` files in [Notion](https://notion.so). We took inspiration from [Airtable](https://www.airtable.com)’s [CSV import extension](https://support.airtable.com/docs/csv-import-extension).

**CSV2Notion Neo** was created as a spin-off project to address occasional inactivity in the original repository and maintain compatibility with Notion. As Notion changes or updates its backend API periodically, we aim to fix and update the tool in a timely manner. Any dependent tools or project that relied on [csv2notion](https://github.com/vzhd1701/csv2notion), can use our **CSV2Notion Neo** tool interchangeably.

## Installation

### Pre-compiled Binary (Recommended)

Download the latest release of the latest binary release [here](https://github.com/TheAcharya/csv2notion-neo/releases).

### With PIP

```bash
$ pip install --user csv2notion_neo
```

**Python 3.7 or later required.**

### From source

This project uses [poetry](https://python-poetry.org/) for dependency management and packaging. You will have to install it first. See [poetry official documentation](https://python-poetry.org/docs/) for instructions.

```shell
$ git clone https://github.com/TheAcharya/csv2notion-neo.git
$ cd csv2notion_neo/
$ poetry install --no-dev
$ poetry run csv2notion_neo
```

## Guide

```plain
$ csv2notion_neo --help
usage: csv2notion_neo [-h] --token TOKEN [--url URL] [OPTION]... FILE

https://github.com/TheAcharya/csv2notion-neo

Upload & Merge CSV Data with Images to Notion Database

positional arguments:
  FILE                               CSV file to upload

general options:
  --token TOKEN                      Notion token, stored in token_v2 cookie for notion.so
  --url URL                          Notion database URL; if none is provided, will create a new database
  --max-threads NUMBER               upload threads (default: 5)
  --log FILE                         file to store program log
  --verbose                          output debug information
  --version                          show program's version number and exit
  -h, --help                         show this help message and exit

column options:
  --column-types TYPES               comma-separated list of column types to use for non-key columns;
                                     if none is provided, types will be guessed from CSV values
                                     (can also be used with --add-missing-columns flag)
  --add-missing-columns              if columns are present in CSV but not in Notion DB, add them to Notion DB
  --randomize-select-colors          randomize colors for added options in select and multi select columns

merge options:
  --merge                            merge CSV with existing Notion DB rows, first column will be used as a key
  --merge-only-column COLUMN         CSV column that should be updated on merge;
                                     when provided, other columns will be ignored
                                     (use multiple times for multiple columns)
  --merge-skip-new                   skip new rows in CSV that are not already in Notion DB during merge

relations options:
  --add-missing-relations            add missing entries into linked Notion DB

page cover options:
  --image-column COLUMN              CSV column that points to URL or image file that will be embedded for that row
  --image-column-keep                keep image CSV column as a Notion DB column
  --image-column-mode {cover,block}  upload image as [cover] or insert it as [block] (default: block)
  --image-caption-column COLUMN      CSV column that points to text caption that will be added to the image block
                                     if --image-column-mode is set to 'block'
  --image-caption-column-keep        keep image caption CSV column as a Notion DB column

page icon options:
  --icon-column COLUMN               CSV column that points to emoji, URL or image file
                                     that will be used as page icon for that row
  --icon-column-keep                 keep icon CSV column as a Notion DB column
  --default-icon ICON                Emoji, URL or image file that will be used as page icon for every row by default

validation options:
  --mandatory-column COLUMN          CSV column that cannot be empty (use multiple times for multiple columns)
  --fail-on-relation-duplicates      fail if any linked DBs in relation columns have duplicate entries;
                                     otherwise, first entry in alphabetical order
                                     will be treated as unique when looking up relations
  --fail-on-duplicates               fail if Notion DB or CSV has duplicates in key column,
                                     useful when sanitizing before merge to avoid ambiguous mapping
  --fail-on-duplicate-csv-columns    fail if CSV has duplicate columns;
                                     otherwise last column will be used
  --fail-on-conversion-error         fail if any column type conversion error occurs;
                                     otherwise errors will be replaced with empty strings
  --fail-on-inaccessible-relations   fail if any relation column points to a Notion DB that
                                     is not accessible to the current user;
                                     otherwise those columns will be ignored
  --fail-on-missing-columns          fail if columns are present in CSV but not in Notion DB;
                                     otherwise those columns will be ignored
  --fail-on-unsettable-columns       fail if DB has columns that don't support assigning value to them;
                                     otherwise those columns will be ignored
                                     (columns with type created_by, last_edited_by, rollup or formula)
  --fail-on-wrong-status-values      fail if values for 'status' columns don't have matching option in DB;
                                     otherwise those values will be replaced with default status
```

### macOS Gatekeeper & Notarization

After trying to run `csv2notion_neo` for the first time, the process will be blocked by macOS's Gatekeeper, and a system dialog will appear which includes

> "csv2notion_neo" can't be opened because the developer cannot be verified...

- To approve the process and allow `csv2notion_neo` to run, go to System Preferences, Security & Privacy, General, and look in the bottom right corner for a button to click.
- After approving `csv2notion_neo`, it should run successfully. 
- For more information, visit https://support.apple.com/en-us/HT202491.

### Prerequisite

You must pass a single `*.csv` file for upload. The CSV file must contain at least 2 rows. The first row will be used as a header.

Optionally you can provide a URL to an existing Notion database with the `--url` option; if not provided, the tool will create a new database named after the CSV file. The URL must link to a database view, not a page.

<details><summary>Obtaining Database URL</summary>
<p>

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/database_url.png?raw=true"> </p>

</p>
</details>


The tool also requires you to provide a `token_v2` cookie for the Notion website through `--token` option.

1. Login to your [Notion](https://www.notion.so/login) account via a web browser.
2. Find and copy the entire `token_v2` value including `v02%3Auser_token_or_cookies%` from your Notion session.

<details><summary>Obtaining Notion Session Token (Safari)</summary>
<p>

Enable Web Inspector

- If you don’t see the Develop menu in the menu bar, choose Safari, Settings, click Advanced, then select “Show features for web developers”.
- Press `⌥ + ⌘ + i` to show Web Inspector

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/notion_token_safari.gif?raw=true"> </p>

</p>
</details>

<details><summary>Obtaining Notion Session Token (Brave, Chrome or Edge)</summary>
<p>

Go to Setting, Privacy and security

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/notion_token_brave.gif?raw=true"> </p>

</p>
</details>

**Important notice**. `token_v2` cookie provides complete access to your Notion account. Handle it with caution.

### Upload Speed

Due to API limitations, the upload is performed one row at a time. To speed things up, this tool uses multiple parallel threads. Use the `--max-threads` option to control how fast it will go. Try not to set it too high to avoid rate limiting by the Notion server.

### Duplicate CSV Columns

Notion does not allow the database to have multiple columns with the same name. Therefore CSV columns will be treated as unique. Only the **last** column will be used if CSV has multiple columns with the same name. If you want the program to stop if it finds duplicate columns, use the `--fail-on-duplicate-csv-columns` flag.

### Missing Columns

If a CSV file has columns absent from Notion DB, they will be ignored by default. Use the `--add-missing-columns` flag if you want the tool to add missing columns into Notion DB. Use the `--fail-on-missing-columns` flag if you want the program to stop if it finds a column mismatch.

### Column Types

By default, the tool will try to guess column types based on their content. Alternatively, you can provide a comma-separated list of column types with the `--column-types` option when creating a new database or adding new columns with the `--add-missing-columns` flag. Since the first column in Notion DB is always text, the tool will use the list to set types for the rest of the columns.

By default, new options for `select` and `multi_select` columns are added with default (gray) color. If you want the tool to randomize colors for new options, use the `--randomize-select-colors` flag.

Some column types do not support assigning value to them because the database generates their content automatically. Currently these types include `created_by`, `last_edited_by`, `rollup` and `formula`. If you want the program to stop if it finds such columns in the database, use the `--fail-on-unsettable-columns` flag.

If the tool cannot convert the column value type properly, it will replace it with an empty string. If you want to make sure all values are correctly converted, use the `--fail-on-conversion-error` flag, which will stop execution in case of a conversion error.

The table below describes available codes for `--column-types` and what values are supported by each column type:

<details><summary>Support Table</summary>
<p>

| Column Type<br />Name   | Column Type<br />Code   | Supported Values | Multiple Values<br />(Comma Separated) |
| ----------------------- | ----------------------- | ---------------- | -------------------------------------- |
| **Basic**               |                         |                  |                                        |
| Text                    | `text`                  | string           | ❌                                     |
| Number                  | `number`                | numerical        | ❌                                     |
| Select                  | `select`                | string           | ❌                                     |
| Multi-select            | `multi_select`          | string           | ✅                                     |
| Status                  | `status`                | string           | ❌                                     |
| Date                    | `date`                  | any date format  | ✅ (range)                             |
| Person                  | `person`                | username, email  | ✅                                     |
| Files & media           | `file`                  | file name, URL   | ✅                                     |
| Checkbox                | `checkbox`              | `true`, `false`  | ❌                                     |
| URL                     | `url`                   | string           | ❌                                     |
| Email                   | `email`                 | string           | ❌                                     |
| Phone                   | `phone_number`          | string           | ❌                                     |
| **Advanced**            |                         |                  |                                        |
| Formula                 | `formula`               | `---`            | `---`                                  |
| Relation                | `---`                   | key, Notion URL  | ✅                                     |
| Rollup                  | `rollup`                | `---`            | `---`                                  |
| Created time            | `created_time`          | any date format  | ❌                                     |
| Created by              | `created_by`            | `---`            | `---`                                  |
| Last edited time        | `last_edited_time`      | any date format  | ❌                                     |
| Last edited by          | `last_edited_by`        | `---`            | `---`                                  |

</p>
</details>

### Merging

By default, the tool will add rows to the existing Notion DB. To merge CSV rows with the Notion database, use the `--merge` flag. The first column of CSV and Notion DB will be used as a key to update existing rows with new values. CSV rows that didn't have a match in Notion DB will be added as new.

Since the tool treats rows as unique during merge based on the key column, it will use first found rows with a unique key. To avoid this ambiguity, you might want to validate duplicate row keys with the `--fail-on-duplicates` flag. It will check both CSV and target Notion DB before the merge.

If you want only select columns to be updated, use the `--merge-only-column` option.

If you don't want the tool to add any new rows not already present in the Notion DB during merge, use the `--merge-skip-new` flag.

### Relation Columns

Notion database has a `relation` column type, which allows you to link together entries from different databases. The tool will try to match column data with keys from a linked database.

By default, it will match with the first found row; it will add nothing if it cannot find the match. Use the `--add-missing-relations` flag if you want the tool to create new entries in the linked DB if no match is found. Use the `--fail-on-conversion-error` flag if you want the program to stop if no match is found.

You can also use Notion URLs in columns of this type, and they must belong to the linked DB. The tool will not be able to add missing entries for URLs if you use the `--add-missing-columns` flag.

Since the tool treats rows in the linked DB as unique you can prevent ambiguous matching with the `--fail-on-relation-duplicates` flag. It will check linked DB for duplicate keys and stop the executions if it finds any.

If linked DB is not accessible (linked DB is deleted or your account doesn't have access to it), columns that point to it will be ignored. If you prefer the program to stop in this case, use the `--fail-on-inaccessible-relations` flag.

### Cover Image & Embedded Image

The tool allows you to add an image to each row with the `--image-column` option. It will use one column from CSV as a data source for the image. It can be either a URL or a file name. The file name must be either an absolute path or a path relative to the CSV file. The tool will upload the file to the Notion server.

By default, the tool will embed an image inside the row page. If you want it to use the image as a page cover, then set the `--image-column-mode` option to `cover`.

Column specified with the `--image-column` option will not be treated as a regular column by default. If you want it to appear in Notion DB, use the `--image-column-keep` flag.

To add custom caption to image block uploaded with `--image-column-mode` set to `block`, use `--image-caption-column` option. To also keep the caption as a Notion DB column, use `--image-caption-column-keep` flag.

### Icons

The tool allows you to add an icon to each row with the `--icon-column` option. The behavior is the same as with `--image-column`; the only difference is that you can use URL, file name, or single emoji.

To also treat `--icon-column` as a regular column, use `--icon-column-keep` flag, similar to `--image-column-keep`.

If you want to set the same icon for each row, use the `--default-icon` option. If both `--icon-column` and `--default-icon` are present, the default icon is used if the row doesn't have anything in the icon column.

### Mandatory Columns

If you want to ensure that specific columns always have value and are not allowed to be empty, then use the `--mandatory-column` option. The program execution will stop if validation fails.

## Examples

<details><summary>Importing CSV into New Database</summary>
<p>

```shell
csv2notion_neo --token YOUR_TOKEN_HERE test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_01.png?raw=true"> </p>

</p>
</details>

<details><summary>Using Custom Column Types</summary>
<p>

```shell
csv2notion_neo --token YOUR_TOKEN_HERE --column-types "number,multi_select" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_02.png?raw=true"> </p>

</p>
</details>

<details><summary>Importing CSV into Existing Database</summary>
<p>

```shell
csv2notion_neo --token YOUR_TOKEN_HERE --url NOTION_URL test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_03.gif?raw=true"> </p>

</p>
</details>

<details><summary>Merging CSV with Existing Database</summary>
<p>

```shell
csv2notion_neo --token YOUR_TOKEN_HERE --url NOTION_URL --merge test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_04.gif?raw=true"> </p>

</p>
</details>

<details><summary>Merging CSV with Select Columns in Existing Database</summary>
<p>

```shell
csv2notion_neo --token YOUR_ TOKEN_HERE --url NOTION URL --merge --merge-only-column "Column 2" --merge-onLy-column "Column 3" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_05.gif?raw=true"> </p>

</p>
</details>

<details><summary>Importing Rows with Images</summary>
<p>

```shell
csv2notion_neo --token YOUR_TOKEN_HERE --image-column "Image Column" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_06.gif?raw=true"> </p>

</p>
</details>

<details><summary>Importing Rows with Emoji Icons</summary>
<p>

```shell
csv2notion_neo --token YOUR_TOKEN_HERE --icon-column "Icon Column" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_07.gif?raw=true"> </p>

</p>
</details>

<details><summary>Updating Emoji Icon Only for All Rows</summary>
<p>

```shell
csv2notion_neo --token YOUR_TOKEN_HERE --url NOTION_URL --default-icon 👍 --merge --merge-only-column "Key" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_08.gif?raw=true"> </p>

</p>
</details>

## Credits

Original Idea and Workflow by [Vigneswaran Rajkumar](https://twitter.com/IAmVigneswaran)

Maintained by [Arjun Prakash](https://github.com/arjunprakash027) (1.0.0 ...)

Original Work by [Vladilen Zhdanov](https://github.com/vzhd1701)

Icon Design by [Bor Jen Goh](https://www.artstation.com/borjengoh)

## License

Licensed under the MIT license. See [LICENSE](https://github.com/TheAcharya/csv2notion-neo/blob/master/LICENSE) for details.

## Reporting Bugs

For bug reports, feature requests and other suggestions you can create [a new issue](https://github.com/TheAcharya/csv2notion-neo/issues) to discuss.
