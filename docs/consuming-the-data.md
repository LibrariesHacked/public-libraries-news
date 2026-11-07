---
layout: default
title: Consuming the Data
description: How to download, query, and integrate Public Libraries News datasets in your own apps, maps, and reports.
---

# Consuming the Data

[🏠 Home](../index.md) · [Overview](overview.md) · [Data Structure](data-structure.md) · [Entity Matching](entity-matching.md) · [Consuming the Data](consuming-the-data.md) · [Automation](automation.md)

---

> **Who is this page for?**
> * **Library users, researchers & campaigners**: Jump to **Direct Downloads & Non-Developer Tools** to download files and open them in Excel, Google Sheets, or free online tools without writing any code.
> * **Web developers & data scientists**: Jump to **Developer Integration** for direct CDN endpoints and ready-to-use code snippets in JavaScript, Python, and cURL.

---

## Direct Downloads & Non-Developer Tools

All data in this repository is completely public and can be downloaded directly without needing an API key or account.

### Direct File Links

| Resource | Direct Download Link | What It Contains |
|---|---|---|
| **Latest Digest** | [`data/latest.json`](https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/latest.json) | The newest weekly post, editorial, and parsed stories. |
| **All Posts Index** | [`data/posts_index.json`](https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/posts_index.json) | Catalog of every weekly post published since 2010. |
| **2024 Stories** | [`data/stories/2024.json`](https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/stories/2024.json) | All parsed stories published during 2024. |
| **2023 Stories** | [`data/stories/2023.json`](https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/stories/2023.json) | All parsed stories published during 2023. |
| **UK Council Lookup** | [`data/lookups/uk_authorities.json`](https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/lookups/uk_authorities.json) | List of UK councils, ONS/GSS codes, and nicknames. |
| **UK Libraries Lookup** | [`data/lookups/libraries.json`](https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/lookups/libraries.json) | 4,200+ UK public library branches with map coordinates. |

### How to Open JSON Without Coding

1. **In Google Sheets**:
   * Install the free *API Connector* or *JSON Get* add-on, paste the Direct Download URL above, and it will expand the news items into rows and columns.
2. **In Microsoft Excel**:
   * Go to the **Data** tab -> **Get Data** -> **From File** -> **From JSON**.
   * Select your downloaded `.json` file to convert stories into an Excel table.
3. **In Your Web Browser**:
   * Click any of the links above to view the raw data. In modern browsers (Firefox, Chrome, Edge), JSON is displayed in a collapsible tree that you can search with `Ctrl+F`.

---

## Developer Integration

The datasets are served from GitHub's raw CDN and are accessible via standard HTTP `GET` requests from web applications, mobile apps, or backend servers.

### In JavaScript (Fetch API)

```javascript
// Load the latest weekly digest and print local news stories
async function loadLatestNews() {
  const url = "https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/latest.json";
  const response = await fetch(url);
  const data = await response.json();

  console.log(`Latest edition: ${data.latest_post.title}`);
  
  data.stories.forEach(story => {
    const council = story.resolution?.library_service?.name || story.entity_raw;
    const branches = story.resolution?.libraries_mentioned?.map(b => b.name).join(", ");
    
    console.log(`[${story.section}] ${council} ${branches ? '(' + branches + ')' : ''}: ${story.text}`);
  });
}

loadLatestNews();
```

---

### In Python (pandas / requests)

```python
import pandas as pd
import requests

# Load all 2024 stories into a pandas DataFrame
url = "https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/stories/2024.json"
stories = requests.get(url).json()

df = pd.DataFrame(stories)
print(f"Total stories loaded: {len(df)}")
print(df[["post_date", "section", "entity_raw", "text"]].head())

# Filter for stories tagged with cuts or closures
cuts_and_closures = df[df["classification"].apply(
    lambda c: any(cat in c.get("categories", []) for cat in ["cuts_and_finance", "closures_and_threats"])
)]
print(f"Total cut and closure stories in 2024: {len(cuts_and_closures)}")
```

---

### In cURL / Command Line

```bash
# Get the title and story count of the latest post
curl -s https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/latest.json | jq '{title: .latest_post.title, count: .latest_post.stories_count}'

# Search for stories mentioning Birmingham in 2024
curl -s https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/stories/2024.json | jq '.[] | select(.resolution.library_service.name == "Birmingham City Council") | {date: .post_date, text: .text}'
```

---

## Attribution Requirement

All news text in this archive is distributed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

When using this data in your website, map, dashboard, or research report, please include attribution:
> *News stories sourced from Public Libraries News (https://www.publiclibrariesnews.com/), curated by Ian Anstice in partnership with The Library Campaign.*
