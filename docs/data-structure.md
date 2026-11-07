---
layout: default
title: Data Structure & Schemas
description: Complete field specifications and JSON schemas for Public Libraries News posts, stories, and lookup tables.
---

# Data Structure & Schemas

[🏠 Home](../index.md) · [Overview](overview.md) · [Data Structure](data-structure.md) · [Entity Matching](entity-matching.md) · [Consuming the Data](consuming-the-data.md) · [Automation](automation.md)

---

> **Who is this page for?**
> * **Library users & researchers**: Read the **Folder Overview** and field descriptions to understand what information is stored in each file.
> * **Developers & analysts**: Review the JSON schemas, nested objects (`resolution`, `classification`), and data types to build your applications or queries.

---

## Folder Organization

All data produced by the scraper is stored in simple, human-readable **JSON** files inside the `data/` folder:

```
data/
├── posts/                  # Full weekly roundup files, organized by year
│   ├── 2024/
│   │   ├── 2024-10-20-pln-12345.json
│   │   └── ...
├── stories/                # All individual news stories grouped by year
│   ├── 2024.json
│   └── ...
├── lookups/                # Reference dictionaries used for matching
│   ├── uk_authorities.json # UK council names, aliases, and government codes
│   ├── libraries.json      # UK public libraries from LibraryCommons
│   └── countries.json      # International country names and codes
├── latest.json             # Quick feed of the most recent post and its stories
└── posts_index.json        # Compact catalog of every post published since 2010
```

---

## 1. Quick Feed (`data/latest.json`)

If you are building a website widget or just want to see the latest news, `data/latest.json` is the easiest file to use. It contains:
1. `latest_post`: High-level information about the newest weekly edition (title, date, editorial text).
2. `stories`: A list of all individual stories extracted from that edition, fully resolved to councils and branches.

---

## 2. Weekly Posts (`data/posts/YYYY/...`)

Each file in `data/posts/` corresponds to a single weekly edition of Public Libraries News.

### Post Schema

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique post identifier (e.g. `"pln-post-12345"`). |
| `source_id` | integer | Original WordPress post ID on publiclibrariesnews.com. |
| `url` | string | Direct web URL to the original post on the PLN website. |
| `slug` | string | URL slug of the post. |
| `title` | string | Title of the weekly digest (e.g. `"Public Libraries News – 20th October 2024"`). |
| `date_published` | string | ISO 8601 publication timestamp. |
| `date_modified` | string | ISO 8601 last-modified timestamp on WordPress. |
| `author` | string | Original author attribution (`"Ian Anstice / The Library Campaign"`). |
| `editorial` | object | Contains plain `text` and cleaned `html` for the weekly editorial opening commentary. |
| `sections_found` | array | List of sections detected (e.g. `["editorial", "changes", "local_news", "international_news"]`). |
| `stories_count` | integer | Total number of individual news stories parsed from this edition. |
| `story_ids` | array | List of story IDs contained in this post. |
| `stats` | object | Summary counts of unique authorities, library branches, countries, and top categories. |
| `attribution` | object | Standard CC BY 4.0 license metadata and credit links. |

### Post Example

```json
{
  "id": "pln-post-12345",
  "source_id": 12345,
  "url": "https://www.publiclibrariesnews.com/2024/10/20/roundup-example/",
  "slug": "roundup-example",
  "title": "Public Libraries News – 20th October 2024",
  "date_published": "2024-10-20T18:00:00Z",
  "date_modified": "2024-10-21T09:00:00Z",
  "author": "Ian Anstice / The Library Campaign",
  "editorial": {
    "text": "Plain text of the weekly editorial commentary...",
    "html": "<p>HTML format of the weekly editorial...</p>"
  },
  "sections_found": [
    "editorial",
    "changes",
    "local_news",
    "international_news"
  ],
  "stories_count": 18,
  "story_ids": [
    "pln-story-12345-local-001",
    "pln-story-12345-local-002"
  ],
  "stats": {
    "authorities_count": 12,
    "libraries_count": 6,
    "countries_count": 3,
    "top_categories": {
      "cuts_and_finance": 8,
      "closures_and_threats": 5,
      "campaigns_and_protests": 3
    }
  },
  "attribution": {
    "source": "Public Libraries News",
    "source_url": "https://www.publiclibrariesnews.com/",
    "license": "CC BY 4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/"
  }
}
```

---

## 3. Individual Stories (`data/stories/YYYY.json`)

Each item in `data/stories/` represents a single story snippet.

### Story Schema

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique story identifier (e.g. `"pln-story-12345-local-001"`). |
| `post_id` | string | Reference to the parent post ID. |
| `post_date` | string | Publication date of the parent post (`YYYY-MM-DD`). |
| `section` | string | Section origin: `"changes"`, `"local_news"`, `"international_news"`, or `"editorial"`. |
| `entity_raw` | string | Raw entity heading extracted from the beginning of the story (e.g. `"Birmingham"`, `"USA"`). |
| `text` | string | Clean plain text of the news item, with leading hyphens and HTML tags stripped. |
| `text_html` | string | Sanitized HTML fragment preserving external hyperlinks. |
| `links` | array | List of extracted links, each with `url`, link `text`, and parsed `domain`. |
| `resolution` | object | Resolved geographic and organisational metadata (see below). |
| `classification` | object | Thematic categories, change types, and sector mentions (see below). |

### Nested Resolution Object (`resolution`)

| Field | Type | Description |
|---|---|---|
| `entity_type` | string | `"local_authority"`, `"country"`, `"sector_body"`, or `"other"`. |
| `country` | string | Country name (e.g. `"England"`, `"Scotland"`, `"Wales"`, `"United States"`). |
| `library_service` | object | Matched UK library authority: `code` (GSS/ONS code), `name`, `nation`, `coordinates`. |
| `libraries_mentioned` | array | List of specific library branches detected in the text, with `id`, `name`, `postcode`, and `coordinates`. |

### Nested Classification Object (`classification`)

| Field | Type | Description |
|---|---|---|
| `categories` | array | List of applicable themes from the 15 sector taxonomy categories (e.g. `cuts_and_finance`, `staffing_and_unions`). |
| `change_type` | string or null | Sub-category for Changes items: `closure`, `reduction_or_cut`, `community_handover`, `investment_or_expansion`, `unstaffed_open_plus`, or `other`. |
| `sector_bodies` | array | Organisations referenced in the story (e.g. `"Arts Council England"`, `"CILIP"`, `"DCMS"`, `"UNISON"`). |
| `financial_mentions`| array | Currency figures extracted from text (e.g. `["£1.2m", "£350,000"]`). |

### Story Example

```json
{
  "id": "pln-story-12345-local-001",
  "post_id": "pln-post-12345",
  "post_date": "2024-10-20",
  "section": "local_news",
  "entity_raw": "Birmingham",
  "text": "Campaigners and local residents gathered outside Harborne Library to protest proposed reductions in staffing and hours.",
  "text_html": "Campaigners and local residents gathered outside Harborne Library to protest proposed <a href=\"https://...\">reductions in staffing and hours</a>.",
  "links": [
    {
      "url": "https://www.birminghammail.co.uk/news/midlands-news/example-123",
      "text": "reductions in staffing and hours",
      "domain": "birminghammail.co.uk"
    }
  ],
  "resolution": {
    "entity_type": "local_authority",
    "country": "England",
    "library_service": {
      "code": "E08000025",
      "name": "Birmingham City Council",
      "nation": "England",
      "coordinates": {
        "latitude": 52.4862,
        "longitude": -1.8904
      }
    },
    "libraries_mentioned": [
      {
        "id": "birmingham-harborne-library",
        "name": "Harborne Library",
        "postcode": "B17 9QG",
        "status": "Open",
        "coordinates": {
          "latitude": 52.4601,
          "longitude": -1.9610
        }
      }
    ]
  },
  "classification": {
    "categories": [
      "cuts_and_finance",
      "campaigns_and_protests",
      "opening_hours",
      "staffing_and_unions"
    ],
    "change_type": null,
    "sector_bodies": [],
    "financial_mentions": []
  }
}
```

---

## 4. Posts Index (`data/posts_index.json`)

A compact index of all 3,000+ posts, ordered chronologically (newest first). Used by the scraper for fast incremental checks and by web applications to browse the full archive:

```json
[
  {
    "id": "pln-post-12345",
    "source_id": 12345,
    "title": "Public Libraries News – 20th October 2024",
    "url": "https://www.publiclibrariesnews.com/2024/10/20/roundup-example/",
    "date_published": "2024-10-20T18:00:00Z",
    "date_modified": "2024-10-21T09:00:00Z",
    "stories_count": 18
  }
]
```
