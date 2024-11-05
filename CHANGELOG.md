# Changelog

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
