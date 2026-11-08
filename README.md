---
layout: default
title: Public Libraries News Scraper & Open Data Archive
description: Automated weekly pipeline and open data archive for Public Libraries News, tracking UK and international library developments.
---

# Public Libraries News Scraper & Open Data Archive

Automated weekly scraper and entity resolver for [Public Libraries News](https://www.publiclibrariesnews.com/) (PLN), curated by **Ian Anstice** in partnership with **The Library Campaign**.

Every week, Public Libraries News chronicles developments, funding changes, campaigns, and news stories across UK and international public libraries. This project automatically processes each new digest into structured open data, linking stories to local authorities and 4,200+ library branches from [LibraryCommons](https://github.com/LibrariesHacked/libraryon-commons).

Online documentation and web portal: **[https://librarieshacked.github.io/public-libraries-news/](https://librarieshacked.github.io/public-libraries-news/)**

## Quick Start: Choose Your Path

### For Library Users, Campaigners & Observers
If you want to view, download, or use the data without writing code:
* **Direct Data Downloads**:
  * [Latest Weekly Digest (`latest.json`)](https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/latest.json) — The newest post, editorial, and parsed stories.
  * [All Posts Catalog (`posts_index.json`)](https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/posts_index.json) — Full directory of every post since 2010.
  * [Yearly Story Archives (`data/stories/`)](https://github.com/LibrariesHacked/public-libraries-news/tree/main/data/stories) — JSON archives for each year (2010–2026).
* **Plain English Guides**:
  * [Overview & Architecture](docs/overview.md) — What the system does in simple terms with diagrams.
  * [Consuming the Data](docs/consuming-the-data.md) — How to download, view, or connect to the data.
* **Content License**: All news content is released under [Creative Commons Attribution (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). Attribution required to Ian Anstice and Public Libraries News. It would also be polite to reference that this is supported by The Library Campaign.

### For Developers, Data Engineers & Researchers
If you are integrating this data into applications or contributing to the codebase:
* **Architecture**: Built entirely with Python 3 standard library modules (`urllib.request`, `html.parser`, `dataclasses`). Zero external scraping dependencies.
* **Automated Scheduling**: Scheduled GitHub Actions workflow runs every Sunday at 21:00 UTC with incremental change detection.
* **Technical Guides**:
  * [Data Structure & Schema](docs/data-structure.md) — Post and story object schemas.
  * [Entity Matching](docs/entity-matching.md) — Authority GSS mapping and branch coordinate resolution.
  * [Automation & Scheduling](docs/automation.md) — GitHub Actions pipeline details.

## Documentation Index

* [Online Documentation Portal](index.md)
* [Project Overview](docs/overview.md) - How the system works with diagrams
* [Data Structure](docs/data-structure.md) - Guide to posts, stories, and schema specifications
* [Entity Matching](docs/entity-matching.md) - How councils, libraries, and countries are linked
* [Consuming the Data](docs/consuming-the-data.md) - How to load raw data files in JavaScript, Python, or cURL
* [Automation & Scheduling](docs/automation.md) - How the weekly GitHub Actions job runs

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development, testing, and exploration.

### Prerequisites

You only need **Python 3.8+** installed on your system.

```bash
python --version
```

The scraper is purposefully designed to run using Python's standard library, requiring zero third-party dependencies for normal operation.

### Installing

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/LibrariesHacked/public-libraries-news.git
   cd public-libraries-news
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Run an incremental check against the latest posts:
   ```bash
   python -m src.cli --mode incremental
   ```

## Running the Tests

The repository includes a comprehensive unit test suite to verify HTML parsing, section splitting, and entity resolution against councils and library branches.

To run all automated tests:

```bash
python -m unittest discover tests
```

### Break down into unit tests

The tests cover:
* **`tests/test_parser.py`**: Validates HTML section splitting (Editorial, Changes, Local news by authority, International news), link extraction, bold prefix parsing, and story ID generation.
* **`tests/test_resolver.py`**: Verifies exact and alias matching for UK local authorities, ONS/GSS codes, Scotland/Wales/Northern Ireland councils, international countries, and library branch identification from LibraryCommons.

```bash
python -m unittest tests/test_parser.py
python -m unittest tests/test_resolver.py
```

## Deployment

The live system is deployed as an automated **GitHub Action** that runs every Sunday at 21:00 UTC (9:00 PM UK time).

* **Trigger**: Automated schedule via `.github/workflows/scrape.yml` or manual trigger via GitHub's `workflow_dispatch`.
* **Idempotent**: Runs in incremental mode by default, querying recent posts and exiting immediately if no new or updated posts exist.
* **No AI dependencies**: The regular runs are deterministic, fast (< 10 seconds), and completely free to run.
* **GitHub Pages**: Deployed automatically via `.github/workflows/deploy-pages.yml` using the Cayman Jekyll theme.

## Built With

* [Python 3](https://www.python.org/) - Core scraping, parsing, and normalization pipeline
* [GitHub Actions](https://github.com/features/actions) - Automated Sunday evening execution
* [GitHub Pages](https://pages.github.com/) - Documentation and open data portal
* [LibraryCommons](https://github.com/LibrariesHacked/libraryon-commons) - Reference directory of 4,200+ UK public library branches
* [WordPress REST API](https://developer.wordpress.org/rest-api/) - Primary post syndication endpoint

## Contributors

See the list of [contributors](https://github.com/LibrariesHacked/public-libraries-news/contributors) who participated in this project.

## Licence

* **Code & Scripts**: Licensed under the [MIT License](LICENSE)
* **News Content**: Scraped text from Public Libraries News is licensed under the **Creative Commons Attribution (CC BY 4.0)** license.

## Acknowledgments

* **Ian Anstice** for founding and maintaining [Public Libraries News](https://www.publiclibrariesnews.com/) as an invaluable sector resource since 2010.
* **The Library Campaign** for their partnership in keeping Public Libraries News independent, active, and accessible
