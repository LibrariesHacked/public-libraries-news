---
layout: default
title: Contributing
description: Guidelines for contributing authority aliases, library branch updates, and code improvements.
---

# Contributing to Public Libraries News Scraper

[🏠 Home](index.md) · [Overview](docs/overview.md) · [Data Structure](docs/data-structure.md) · [Entity Matching](docs/entity-matching.md) · [Consuming the Data](docs/consuming-the-data.md) · [Automation](docs/automation.md)

---

We welcome contributions from library campaigners, sector observers, data analysts, and developers.

## How Can I Contribute?

### 1. Adding or Correcting Authority Aliases
If you notice that a story in Public Libraries News refers to a council or authority by a name or acronym that isn't recognized:
1. Open `data/lookups/uk_authorities.json`.
2. Find the relevant council entry.
3. Add the alternative name or spelling to the `"aliases"` array.
4. Submit a Pull Request.

### 2. Updating Library Branches
The library lookup table in `data/lookups/libraries.json` is compiled from [LibrariesHacked/libraryon-commons](https://github.com/LibrariesHacked/libraryon-commons). If a library is missing or has outdated coordinates, contributing directly to LibraryCommons ensures all related projects benefit from the fix.

### 3. Reporting Issues
If a specific weekly post has a unique layout variation that our parser struggles with, please open an Issue with:
* The link to the Public Libraries News post.
* The section or story that was missed or improperly parsed.

---

## Code Style & Testing
Before submitting a pull request with code changes:
* Ensure all tests pass:
  ```bash
  python -m unittest discover tests
  ```
* Adhere to the code style: classes, methods, and files must have concise docstrings describing *what* and *why* in a few sentences.
* Keep dependencies minimal. The core scraper is designed to run cleanly on the standard Python library without external package requirements.
