# Changelog

### 1.2.3

**🎉 Released:**
- 6th February 2024

**🔨 Improvements:**
- Added support for attaching multiple Notion blocks (#14)
- Added support for having multiple image attachment with sub-folders (#14)

**🐞 Bug Fix:**
- Improved logic and funcations for multiple image attachment columns (#14)

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
