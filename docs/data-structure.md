# Data Structure

All data produced by the scraper is stored in simple, human-readable **JSON** files inside the `data/` folder. This page explains what the files contain and how they are organized.

---

## Folder Organization

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

## 1. Weekly Posts (`data/posts/YYYY/...`)

Each file in `data/posts/` corresponds to a single weekly edition of Public Libraries News.

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

## 2. Individual Stories (`data/stories/YYYY.json`)

Each item in `data/stories/` is a single news snippet extracted from a section like **Changes**, **Local news by authority**, or **International news**.

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
      "url": "https://www.birminghammail.co.uk/...",
      "text": "reductions in staffing and hours",
      "domain": "birminghammail.co.uk"
    }
  ],
  "resolution": {
    "entity_type": "local_authority",
    "country": "England",
    "country_code": "GB",
    "library_service": {
      "name": "Birmingham",
      "gss_code": "E08000025",
      "confidence": "exact"
    },
    "libraries_mentioned": [
      {
        "id": "lib_79b27a76-4ad4-41c2-8089-d371cefe66c2",
        "name": "Harborne Library",
        "postcode": "B17 9QG",
        "lat": 52.4601,
        "lng": -1.9610,
        "status": "Open",
        "slug": "harborne-library"
      }
    ],
    "coordinates": {
      "latitude": 52.4862,
      "longitude": -1.8904
    }
  },
  "classification": {
    "categories": [
      "campaigns_and_protests",
      "opening_hours",
      "staffing_and_unions"
    ],
    "primary_category": "campaigns_and_protests",
    "change_type": "reduction_or_cut",
    "sector_bodies_mentioned": [
      "UNISON"
    ],
    "financial_mentions": [
      "£2.3m"
    ]
  },
  "tags": [
    "campaigns_and_protests",
    "opening_hours",
    "staffing_and_unions"
  ]
}
```

---

## 3. Schema Definitions

Formal schema specifications for developers building integrations are provided under `schemas/`:
* [Post Schema (post.schema.json)](../schemas/post.schema.json)
* [Story Schema (story.schema.json)](../schemas/story.schema.json)
