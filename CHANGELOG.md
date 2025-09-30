# Changelog

### 2.0.0

**🎉 Released:**
- TBD

**🔨 Improvements:**
- Migrated from unofficial Notion private API to official [Notion API](https://developers.notion.com/)
- Integrated [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) library for official API support
- Changed authentication from `token_v2` session cookies to official Notion integration tokens
- Made `--url` parameter mandatory for all operations (database URL or page URL required)
- Automatic database creation is no longer supported
- Standardised API interactions following official Notion specifications (#54)
- Better error handling with official API error codes and responses
- Improved file upload reliability using official `file_uploads` endpoints
- Better rate limiting using official API guidelines (#56)
- Added `--delete-all-database-entries`: Archive all entries within a specified database with progress tracking (#48)
- Enhanced URL validation with `Notion.so` domain and protocol validation
- Improved `--token` format validation with user-friendly error messages
- Added comprehensive test suite with 73 test methods across 18 test categories (#17)
- Upgraded from Python 3.8 to Python 3.9
- Updated to latest security patches across most dependencies
- Improved build reproducibility across environments
- Enhanced ephemeral build `local-test-build.sh` reliability
- Improved codebase formatting

---

### 1.3.6

**🎉 Released:**
- 26th June 2025

**🐞 Bug Fix:**
- Fixed a CRDT-related issue in `submitTransaction` that was preventing payloads from being uploaded

---

### 1.3.5

**🎉 Released:**
- 25th April 2025

**🐞 Bug Fix:**
- Fixed issue where Notion API rate limits triggered `HTTPError: 500 Server Error: Internal Server` (#54)

---

### 1.3.4

**🎉 Released:**
- 17th February 2025

**🔨 Improvements:**
- Updated dependencies packages

**🐞 Bug Fix:**
- Fixed can't able to upload images due to Notion API changes (#46)

---

### 1.3.3

**🎉 Released:**
- 11th November 2024

**🔨 Improvements:**
- Added `--delimiter`: Delimiter that is used to separate columns and rows in csv file if none is provided, `,` is taken as default (#43)

---

### 1.3.2

**🎉 Released:**
- 5th November 2024

**🔨 Improvements:**
- Updated dependencies packages
- Improved logic when `-url` and `-merge` is not provided (#41)

**🐞 Bug Fix:**
- Fixed can't able to create new Notion Database (#39)
- Fixed image uploading when using `--image-column-mode cover` (#40)

---

### 1.3.1

**🎉 Released:**
- 21st June 2024

**🔨 Improvements:**
- Improved log output for `--workspace`

---

### 1.3.0

**🎉 Released:**
- 3rd June 2024

**🔨 Improvements:**
- Automatically analyse and generate captions for images using Hugging Face's open-source AI/ML models (#25)
- Added `--hugging-face-token`: Hugging Face token to use image captioning model online
- Added `--hf-model `: Provide the model used for generating caption <`vit-gpt2` | `blip-image` | `git-large`> (defaults: `vit-gpt2`)
- Added `--caption-column`: Provide both image column and column where caption would be written

---

### 1.2.6

**🎉 Released:**
- 19th May 2024

**🔨 Improvements:**
- Improved log output for `--rename-notion-key-column` (#35)

---

### 1.2.5

**🎉 Released:**
- 10th May 2024

**🔨 Improvements:**
- Improved image and icon upload logic (#32)
- Improved `--payload-key-column` logic (#33)
- Updated dependencies packages

**🐞 Bug Fix:**
- Fixed can't able to upload images due to Notion API changes (#32)
- Fixed can't duplicate item within Notion when using CSV2Notion Neo (#3)

---

### 1.2.4

**🎉 Released:**
- 12th February 2024

**🔨 Improvements:**
- Added logic for `--merge-only-column` for `.json` data (#27)
- Improved log output with `--verbose` augmentation

**🐞 Bug Fix:**
- Fixed image check before getting cover image (#28)
- Fixed `key_column` error (#29)

---

### 1.2.3

**🎉 Released:**
- 6th February 2024

**🔨 Improvements:**
- Added support for attaching multiple Notion blocks (#14)
- Added support for having multiple image attachment with sub-folders (#14)

**🐞 Bug Fix:**
- Improved logic and functions for multiple image attachment columns (#14)

---

### 1.2.2

**🎉 Released:**
- 27th January 2024

**🔨 Improvements:**
- Added new macOS pkg release with notarization ticket stapled

**🐞 Bug Fix:**
- Fixed multiple image upload (#23)

---

### 1.2.1

**🎉 Released:**
- 19th January 2024

**🐞 Bug Fix:**
- Fixed multiple image upload (#21)

---

### 1.2.0

**🎉 Released:**
- 15th January 2024

**🔨 Improvements:**
- Added direct integration of notion-py package for increased flexibility for futures enhancements (#18)
- Added ability to add multiple image attachment columns (#14)
- Added `--workspace` : active Notion workspace name
- Added codesign and notarization to macOS binary
  
---

### 1.1.2

**🎉 Released:**
- 5th January 2024

**🐞 Bug Fix:**
- Improved error handling of property mismatch (#16)

---

### 1.1.1

**🎉 Released:**
- 21st December 2023

**🐞 Bug Fix:**
- Fixed conversion of integers into strings

---

### 1.1.0

**🎉 Released:**
- 20th December 2023

**🔨 Improvements:**
- Added `.json` support for [MarkersExtractor](https://github.com/TheAcharya/MarkersExtractor) (#9)
- Added `--payload-key-column` : define key column in JSON payload (#12)
- Added CSV2Notion Neo version number in log file (#11)
- Added `--rename-notion-key-column` : rename the key column in the file to a different key column in Notion (#12)
- Improved legibility of warning log

---

### 1.0.2

**🎉 Released:**
- 30th November 2023

**🐞 Bug Fix:**
- Add missing imports
- Fixed avoid sending big payload on views update (#8)

---

### 1.0.1

**🎉 Released:**
- 23rd October 2023

This is the first public release of **CSV2Notion Neo**!

**🔨 Improvements:**
- Added repository URL within `--help` (#5)
- Updated repository's CI test workflows

---

### 1.0.0
**🎉 Released:**
- 15th October 2023

This is the first public pre-release of **CSV2Notion Neo**!

**🐞 Bug Fix:**
- Fixed batch uploading Icon Image
- Fixed batch uploading Images from CSV
