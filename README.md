<p align="center">
  <a href="https://github.com/TheAcharya/csv2notion-neo"><img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/CSV2Notion Neo_Icon.png?raw=true" height="200">
  <h1 align="center">CSV2Notion Neo</h1>
</p>


<p align="center"><a href="https://github.com/TheAcharya/csv2notion-neo/blob/main/LICENSE"><img src="http://img.shields.io/badge/license-MIT-lightgrey.svg?style=flat" alt="license"/></a>&nbsp;<a href="https://pypi.python.org/pypi/csv2notion-neo"><img src="https://img.shields.io/pypi/v/csv2notion-neo?label=version" alt="PyPI"/></a>&nbsp;<a href="https://pypi.org/project/csv2notion-neo/"><img src="https://img.shields.io/pypi/pyversions/csv2notion-neo.svg" alt="Python"/></a>&nbsp;<a href="https://github.com/TheAcharya/csv2notion-neo/actions/workflows/release_github.yml"><img src="https://github.com/TheAcharya/csv2notion-neo/actions/workflows/release_github.yml/badge.svg" alt="release_github"/></a>&nbsp;<a href="Github All Releases"><img src="https://img.shields.io/github/downloads/TheAcharya/csv2notion-neo/total.svg" alt="release_github"/></a></p>

An advance method to upload & merge *.csv or *.json files with images to <a href="https://notion.so/" target="_blank">Notion</a> database.

## Core Features

### Advantages over native import

- Merge CSV or JSON with the existing database, using the first column as a key to combine existing rows
- Choose column types manually instead of letting Notion detecting them automatically
- Link or create new entries in relation columns based on their values automatically
- Easily upload files into the designated "Files & Media" column
- Assign a icon for each row for quick identification
- Set a cover or embed an image for each row to enhance visual representation
- Upload image files for covers or icons
- Apply validation options for input data to ensure accuracy
- Automatically analyse and generate captions for images using Hugging Face's open-source AI/ML models

### Disadvantages over native import
 
- Importing each row separately might lead to slower speed
  - To address this, utilise multithreaded upload

## Table of contents

- [Background](#background)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [Pre-compiled Binary (Recommended)](#pre-compiled-binary-recommended)
  - [From Source](#from-source)
- [Guide](#guide)
  - [macOS Release](#macos-release)
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
  - [AI/ML Options (Hugging Face)](#aiml-options-hugging-face)
- [Examples](#examples)
- [Utilised By](#utilised-by)
- [Credits](#credits)
- [License](#license)
- [Reporting Bugs](#reporting-bugs)

## Background

Originally, we developed [csv2notion](https://github.com/vzhd1701/csv2notion) to address the lack of advanced importing support for `*.csv` files in [Notion](https://notion.so). We took inspiration from [Airtable](https://www.airtable.com)’s [CSV import extension](https://support.airtable.com/docs/csv-import-extension).

**CSV2Notion Neo** was created as a spin-off project to address inactivity in the original repository and maintain compatibility with Notion. As Notion changes or updates its backend API periodically, we aim to fix, update and add new features to the tool in a timely manner. Any dependent tools or project that relied on [csv2notion](https://github.com/vzhd1701/csv2notion), can use our **CSV2Notion Neo** tool interchangeably requiring additional augments.

## System Requirements

### Linux (x64)
- Operating System: Linux (64-bit)
- Architecture: x64
- Dependencies: None (ensure basic Linux shell tools are available)

### macOS (ARM64)
- Operating System: macOS 11 (Big Sur) or later
- Architecture: ARM64 (Apple Silicon)
- Dependencies: None

### Windows (x64)
- Operating System: Windows 10 or later (64-bit)
- Architecture: x64
- Dependencies: None

## Installation

### Pre-compiled Binary (Recommended)

Download the latest release of the latest binary release [here](https://github.com/TheAcharya/csv2notion-neo/releases).

### With [Homebrew](https://brew.sh/) (Recommended for macOS)

```bash
$ brew install TheAcharya/homebrew-tap/csv2notion-neo
```
```bash
$ brew uninstall --cask csv2notion-neo
```

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

Upload & Merge CSV or JSON Data with Images to Notion Database

positional arguments:
  FILE                               CSV or JSON file to upload

general options:
  --workspace                        active Notion workspace name
  --token                            Notion token, stored in token_v2 cookie for notion.so
  --url URL                          Notion database URL; if none is provided, will create a new database
  --max-threads                      upload threads (default: 5)
  --log FILE                         file to store program log
  --verbose                          output debug information
  --version                          show program's version number and exit
  -h, --help                         show this help message and exit

machine learning options:
  --hugging-face-token              Hugging Face token to use image captioning model online
  --hf-model                        Provide the model used for generating caption <vit-gpt2 | blip-image| git-large> (defaults: vit-gpt2)
  --caption-column                  Provide both image column and column where caption would be written

column options:
  --column-types                     comma-separated list of column types to use for non-key columns;
                                     if none is provided, types will be guessed from CSV values
                                     (can also be used with --add-missing-columns flag)
  --add-missing-columns              if columns are present in CSV but not in Notion DB, add them to Notion DB
  --rename-notion-key-column         rename the key column in the file to a different key column in Airtable
  --randomize-select-colors          randomize colors for added options in select and multi select columns

merge options:
  --merge                            merge CSV or JSON with existing Notion DB rows, first column will be used as a key
  --merge-only-column                CSV or JSON column that should be updated on merge;
                                     when provided, other columns will be ignored
                                     (use multiple times for multiple columns)
  --merge-skip-new                   skip new rows in CSV or JSON that are not already in Notion DB during merge

relations options:
  --add-missing-relations            add missing entries into linked Notion DB

page cover options:
  --image-column COLUMN              one or more CSV or JSON column that points to URL or image file that will be embedded for that row
  --image-column-keep                keep image CSV or JSON column as a Notion DB column
  --image-column-mode {cover,block}  upload image as [cover] or insert it as [block] (default: block)
  --image-caption-column             CSV or JSON column that points to text caption that will be added to the image block
                                     if --image-column-mode is set to 'block'
  --image-caption-column-keep        keep image caption CSV or JSON column as a Notion DB column

page icon options:
  --icon-column                      CSV or JSON column that points to emoji, URL or image file
                                     that will be used as page icon for that row
  --icon-column-keep                 keep icon CSV or JSON column as a Notion DB column
  --default-icon ICON                Emoji, URL or image file that will be used as page icon for every row by default

validation options:
  --mandatory-column                 CSV or JSON column that cannot be empty (use multiple times for multiple columns)
  --payload-key-column               JSON object that is the key in Notion DB;
                                     if JSON file is used, this cannot be empty
  --fail-on-relation-duplicates      fail if any linked DBs in relation columns have duplicate entries;
                                     otherwise, first entry in alphabetical order
                                     will be treated as unique when looking up relations
  --fail-on-duplicates               fail if Notion DB or CSV or JSON has duplicates in key column,
                                     useful when sanitizing before merge to avoid ambiguous mapping
  --fail-on-duplicate-csv-columns    fail if CSV or JSON has duplicate columns;
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

### macOS Release

<details><summary>Privacy & Security</summary>
<p>

For macOS, you have the option of two distinct releases: one packaged within a `.zip` archive and the other in a `.pkg` format. Navigate to the `Privacy & Security` settings and set your preference to `App Store and identified developers`.

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/macOS-privacy.png?raw=true"> </p>

</p>
</details>

Utilise the `CSV2Notion Neo.pkg` installer to install the command-line binary into your system. Upon completion, find the installed binary `csv2notion_neo` located within `/usr/local/bin`. To uninstall, you can utalise this terminal command.

```plain
sudo rm /usr/local/bin/csv2notion_neo
```

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/macOS-installer.png?raw=true"> </p>

### Prerequisite

You must pass a single `*.csv` file for upload. The CSV file must contain at least 2 rows. The first row will be used as a header.

Optionally you can provide a URL to an existing Notion database with the `--url` option; if not provided, the tool will create a new database named after the CSV file. The URL must link to a database view, not a page.

<details><summary>Obtaining Database URL</summary>
<p>

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/database_url.png?raw=true"> </p>

</p>
</details>

<details><summary>Obtaining Workspace Name</summary>
<p>

<p align="center"> <img src="https://www.notion.so/cdn-cgi/image/format=auto,width=3840,quality=100/https://images.ctfassets.net/spoqsaf9291f/36DSq2EcSv3Q9uUUnRXdMo/9f8e7900ef53569a84c8625097bcc271/Workspace_settings_-_hero.png"> </p>

1. To see your Workspace name go to `Settings & members` at the top of the left sidebar. In the window that pops up, click on the `Settings` tab.
2. If your Workspace name is `Acme Inc.`, you are required to provide `--workspace "Acme Inc."` as such.

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

### AI/ML Options (Hugging Face)

Hugging Face is a prominent AI company known for its contributions to natural language processing (NLP) through its comprehensive open-source platform. It offers an extensive library called Transformers, which provides pre-trained models for a wide range of NLP tasks, including text generation, sentiment analysis, translation, and more. These models are based on state-of-the-art architectures like BERT, GPT, and T5.

The platform fosters a vibrant open-source community where developers and researchers can share and collaborate on models. Users can access, fine-tune, and deploy a vast array of community-contributed models via the Hugging Face Model Hub. This collaborative environment accelerates innovation and democratizes access to advanced machine learning tools.

<details><summary>Obtaining Hugging Face Token</summary>
<p>

Steps to Obtain a Hugging Face Token with Write Mode

1. **Create a Hugging Face Account (if you don't have one already):**
   - Go to the [Hugging Face website](https://huggingface.co/).
   - Click on "Sign Up" in the top right corner.
   - Fill in your details (username, email, password) and complete the registration process.

2. **Log In to Your Account:**
   - If you already have an account, simply log in by clicking "Log In" and entering your credentials.

3. **Navigate to Your Profile Settings:**
   - Once logged in, click on your profile icon in the top right corner of the page.
   - From the dropdown menu, select "Settings."

4. **Access the API Tokens Section:**
   - In the settings menu on the left side of the screen, find and click on "Access Tokens."

5. **Create a New API Token:**
   - In the "Access Tokens" section, you will see an option to create a new token.
   - Click on "New token."

6. **Set Permissions to Write Mode:**
   - Provide a name for your token (e.g., "MyWriteToken").
   - Set the permissions type to "Write" type by selecting the "Write" from the dropdown. This will grant the token write access, allowing you to perform actions that modify data on Hugging Face.

7. **Generate and Copy Your Token:**
   - Click on the "Generate token" button.
   - Your new token will be displayed. Copy it and store it in a secure place, as you will need it to access Hugging Face's API services.

**Note:** Keep your token secure and do not share it publicly, as it grants access to your Hugging Face account and its resources.

</p>
</details>

<details><summary>Avaliable Model Information</summary>
<p>

| Models      | Information                                                          | Accuracy |
| ---------- | -------------------------------------------------------------------- | -------- |
| vit-gpt2   | [Link](https://huggingface.co/nlpconnect/vit-gpt2-image-captioning)  | Low - Medium   |
| blip-image | [Link](https://huggingface.co/Salesforce/blip-image-captioning-base) | Low - Medium   |
| git-large  | [Link](https://huggingface.co/microsoft/git-large)                   | Low - Medium   |

**Note:** Additional models will be integrated in the future from Hugging Face as better models are identified.

</p>
</details>

> [!WARNING]  
> Please be aware that this feature is currently in an experimental phase. We strongly advise against uploading sensitive images or those of a personal and private nature. Images will be uploaded to Hugging Face’s servers for analysis. We recommend using commercial images, such as movie stills or stock photos, for AI captioning.

## Examples

<details><summary>Importing CSV into New Database</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_01.png?raw=true"> </p>

</p>
</details>

<details><summary>Using Custom Column Types</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE \
  --column-types "number,multi_select" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_02.png?raw=true"> </p>

</p>
</details>

<details><summary>Importing CSV into Existing Database</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE \
  --url NOTION_URL test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_03.gif?raw=true"> </p>

</p>
</details>

<details><summary>Merging CSV with Existing Database</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE \
  --url NOTION_URL \
  --merge test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_04.gif?raw=true"> </p>

</p>
</details>

<details><summary>Merging CSV with Select Columns in Existing Database</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_ TOKEN_HERE \
  --url NOTION URL \
  --merge \
  --merge-only-column "Column 2" \
  --merge-onLy-column "Column 3" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_05.gif?raw=true"> </p>

</p>
</details>

<details><summary>Importing Rows with Images</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE \
--image-column "Image Column" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_06.gif?raw=true"> </p>

</p>
</details>

<details><summary>Importing Rows with Images (Multiple Image Column)</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE \
  --image-column "Colour Image" "Black & White Image" "Map" \
  --image-column-keep --mandatory-column "Cat ID" test.csv
```

Example CSV

```text
Cat ID,Animal Name,Location,Colour Image,Black & White Image,Map
1,Lion,Namibia,Colour/lion.jpg,Black & White/lion.jpg,Map/Namibia.jpg
2,Tiger,India,Colour/tiger.jpg,Black & White/tiger.jpg,Map/India.jpg
3,Panther,India,Colour/panther.jpg,Black & White/panther.jpg,Map/India.jpg
4,Snow Leopard,Nepal,Colour/snow_leopard.jpg,Black & White/snow_leopard.jpg,Map/Nepal.jpg
5,Cheetah,South Africa,Colour/cheetah.jpg,Black & White/cheetah.jpg,Map/South Africa.jpg
6,Puma,South America,Colour/puma.jpg,Black & White/puma.jpg,Map/South America.jpg
7,Jaguar,Brazil,Colour/jaguar.jpg,Black & White/jaguar.jpg,Map/Brazil.jpg
```

Example Folder Structure

```text
├─ Data/
│  ├─ test.csv
│  ├─ Black & White/
│  │  ├─ cheetah.jpg
│  │  ├─ jaguar.jpg
│  │  ├─ lion.jpg
│  │  ├─ panther.jpg
│  │  ├─ puma.jpg
│  │  ├─ snow_leopard.jpg
│  │  ├─ tiger.jpg
│  ├─ Colour/
│  │  ├─ cheetah.jpg
│  │  ├─ jaguar.jpg
│  │  ├─ lion.jpg
│  │  ├─ panther.jpg
│  │  ├─ puma.jpg
│  │  ├─ snow_leopard.jpg
│  │  ├─ tiger.jpg
│  ├─ Map/
│  │  ├─ Brazil.jpg
│  │  ├─ India.jpg
│  │  ├─ Namibia.jpg
│  │  ├─ Nepal.jpg
│  │  ├─ South Africa.jpg
│  │  ├─ South America.jpg
│  │  ├─ tiger.jpg
```

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_11.gif?raw=true"> </p>

</p>
</details>

<details><summary>Importing Rows with Emoji Icons</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE  \
  --icon-column "Icon Column" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_07.gif?raw=true"> </p>

</p>
</details>

<details><summary>Updating Emoji Icon Only for All Rows</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE \
  --url NOTION_URL \
  --default-icon 👍 \
  --merge \
  --merge-only-column "Key" test.csv
```
<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_08.gif?raw=true"> </p>

</p>
</details>

<details><summary>Importing JSON into Existing Database</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE \
  --url NOTION_URL \
  --mandatory-column "Cat ID" \
  --payload-key-column "Cat ID" \
  --merge JSON-Demo.json
```

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_09.gif?raw=true"> </p>

</p>
</details>

<details><summary>Importing JSON into Existing Database with a Different Key Column</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE \
  --url NOTION_URL \
  --mandatory-column "Cat ID" \
  --payload-key-column "Cat ID" \
  --rename-notion-key-column "Cat ID" "Anything ID" \
  --merge JSON-Demo.json
```

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_10.gif?raw=true"> </p>

</p>
</details>

<details><summary>Utilising Hugging Face's AI/ML Model to Automatically Analyse and Generate Captions from Images</summary>
<p>

```shell
csv2notion_neo --workspace YOUR_WORKSPACE_NAME_HERE --token YOUR_TOKEN_HERE --url NOTION_URL --hugging-face-token YOUR_HUGGING_FACE_TOKEN_HERE \
  --hf-model blip-image \
  --caption-column "Image Filename" "Frame Description" \
  --image-column "Image Filename" \
  --image-column-keep \
  --mandatory-column "Cat ID" \
  --merge big_cats.csv
```

<p align="center"> <img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/example_12.gif?raw=true"> </p>

</p>
</details>

## Utilised By

### [Marker Data](https://markerdata.theacharya.co)

<details><summary>Marker Data's Notion Panel</summary>
<p>

<p align="center"> <img src="https://github.com/TheAcharya/MarkerData-Website/blob/main/docs/assets/md-database-settings_01.png?raw=true"> </p>

</p>
</details>

### [CommandPost](https://commandpost.io)

<details><summary>CommandPost's Notion Toolbox</summary>
<p>

<p align="center"> <img src="https://github.com/CommandPost/CommandPost-Website/blob/main/docs/static/toolbox-notion.png?raw=true"> </p>

</p>
</details>

## Credits

Original Idea and Workflow Architecture by [Vigneswaran Rajkumar](https://twitter.com/IAmVigneswaran)

Maintained by [Arjun Prakash](https://github.com/arjunprakash027) (1.0.0 ...)

Original Work by [Vladilen Zhdanov](https://github.com/vzhd1701)

Icon Design by [Bor Jen Goh](https://www.artstation.com/borjengoh)

## License

Licensed under the MIT license. See [LICENSE](https://github.com/TheAcharya/csv2notion-neo/blob/master/LICENSE) for details.

## Reporting Bugs

For bug reports, feature requests and other suggestions you can create [a new issue](https://github.com/TheAcharya/csv2notion-neo/issues) to discuss.
