# Public Libraries News Scraper

Automated weekly scraper and entity resolver for [Public Libraries News](https://www.publiclibrariesnews.com/), tracking what is happening to public library services across the UK and internationally.

This project runs automatically every Sunday evening via GitHub Actions to pick up new weekly digests, extract the editorial commentary, and parse discrete news items from sections including **Changes**, **Local news by authority**, and **International news**. Extracted stories are matched against official UK local authorities and over 4,200 individual library branches from [LibraryCommons](https://github.com/LibrariesHacked/libraryon-commons).

---

## Documentation

Comprehensive plain-English guides and specifications:
* [Overview & Architecture](docs/overview.md) - How the system works in plain English with diagrams
* [Data Structure](docs/data-structure.md) - Guide to posts, stories, and schema specifications
* [Entity Matching](docs/entity-matching.md) - How councils, libraries, and countries are linked without AI
* [Automation & Scheduling](docs/automation.md) - How the weekly GitHub Actions job runs
* [Consuming the Data](docs/consuming-the-data.md) - How to load raw data files in JavaScript, Python, or cURL

---

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [Deployment](#deployment) for notes on how the automated pipeline runs.

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

3. Run an initial check:
   ```bash
   python -m src.cli --mode incremental
   ```

---

## Running the Tests

The repository includes a unit test suite to verify HTML parsing, section splitting, and entity resolution against councils and library branches.

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

---

## Deployment

The live system is deployed as an automated **GitHub Action** that runs every Sunday at 21:00 UTC (9:00 PM UK time).

* **Trigger**: Automated schedule via `.github/workflows/scrape.yml` or manual trigger via GitHub's `workflow_dispatch`.
* **Idempotent**: Runs in incremental mode by default, querying recent posts and exiting immediately if no new or updated posts exist.
* **No AI dependencies**: The regular runs are deterministic, fast (< 10 seconds), and completely free to run.

---

## Built With

* [Python 3](https://www.python.org/) - Core scraping, parsing, and normalization pipeline
* [GitHub Actions](https://github.com/features/actions) - Automated Sunday evening execution
* [LibraryCommons](https://github.com/LibrariesHacked/libraryon-commons) - Reference directory of 4,200+ UK public library branches
* [WordPress REST API](https://developer.wordpress.org/rest-api/) - Primary post syndication endpoint

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests to us.

If you notice a council name or alias that is not matching correctly, you can add it directly to `data/lookups/uk_authorities.json` via a pull request.

---

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/LibrariesHacked/public-libraries-news/tags).

---

## Authors

* **Dave Adair** - *Initial work & Architecture* - [Libraries Hacked](https://github.com/LibrariesHacked)

See also the list of [contributors](https://github.com/LibrariesHacked/public-libraries-news/contributors) who participated in this project.

---

## License

* **Code & Scripts**: Licensed under the [MIT License](LICENSE) or CC0 public dedication.
* **News Content**: Scraped text from Public Libraries News is licensed under the **Creative Commons Attribution (CC BY 4.0)** license.

---

## Acknowledgments

* **Ian Anstice** for founding and maintaining [Public Libraries News](https://www.publiclibrariesnews.com/) as an invaluable sector resource since 2010.
* **The Library Campaign** for their partnership in keeping Public Libraries News independent, active, and accessible.
* **LibraryOn / LibraryCommons** for open library branch location data.
