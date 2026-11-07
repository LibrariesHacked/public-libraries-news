---
layout: default
title: Project Overview & Architecture
description: Plain English explanation of how the Public Libraries News scraper and data pipeline works.
---

# Project Overview & Architecture

[🏠 Home](../index.md) · [Overview](overview.md) · [Data Structure](data-structure.md) · [Entity Matching](entity-matching.md) · [Consuming the Data](consuming-the-data.md) · [Automation](automation.md)

---

> **Who is this page for?**
> Anyone wanting to understand the purpose of this project, how weekly news roundups become structured data, and how the system operates without needing complicated artificial intelligence. Non-developers can read the summary and diagram below to see how it all fits together.

---

## What is this project?

Every week, [Public Libraries News](https://www.publiclibrariesnews.com/) (curated by **Ian Anstice** in partnership with **The Library Campaign**) publishes a comprehensive roundup of what is happening to public libraries across the United Kingdom and internationally.

This repository automatically reads each new post on Sunday evening, splits the news into individual, searchable stories, and links each story to:
* The relevant **Local Authority** (e.g. Birmingham, Barnsley, Edinburgh, Cardiff).
* Specific **Library Branches** mentioned (e.g. Harborne Library, Mitchell Library).
* The **Country** (for international stories such as the USA, Canada, or Australia).
* Specific **Sector Themes** (such as closures, budget cuts, strikes, refurbished buildings, or book challenges).

All the collected data is stored as plain, open data files directly inside this GitHub repository. Anyone can use this data for free to build maps, dashboards, research reports, or search tools.

---

## How It Works in Plain English

```mermaid
flowchart LR
    A["Weekly PLN Post<br/>(Published on Sunday)"] --> B["Automatic Reader<br/>(GitHub Action)"]
    B --> C["Split into Sections<br/>(Editorial, Changes, Local, International)"]
    C --> D["Match Places & Libraries<br/>(Using open council & library lists)"]
    D --> E["Save Open Data Files<br/>(Organized by year in this repo)"]
    E --> F["Ready for Websites, Maps & Dashboards"]
```

1. **Scheduled Check**: Every Sunday night at 9:00 PM (UK time), an automated process runs on GitHub.
2. **Checking for New News**: It asks the Public Libraries News website if a new weekly post has been published.
   * If there are **no new posts**, it quietly stops without changing anything.
   * If a **new post is found**, it reads the content.
3. **Organizing the Stories**: It reads the editorial notes, and then takes each item in sections like *Changes*, *Local news by authority*, and *International news*.
4. **Linking Names to Real Places**:
   * It recognizes the council name (e.g. "Cheshire West" is linked to *Cheshire West and Chester* and assigned official government code `E06000050`).
   * It scans the text to see if individual library buildings are mentioned (e.g. "Harborne Library").
   * It preserves all links to original sources, council minutes, and newspaper articles.
5. **Categorizing the Topic**: It checks what the story is about (e.g. a funding cut, a new library opening, or a volunteer campaign).
6. **Saving Open Files**: The structured files are committed right into the `data/` folder in this repository, ready for anyone to download or connect to.

---

## Why Pure Data (No AI Needed)?

We deliberately designed this system to run **purely from reliable code and open reference datasets**, without needing an artificial intelligence (AI) model:
* **Predictable & Transparent**: Library names and council areas are matched using clear lookup tables. You can always see exactly why a story was linked to a council.
* **100% Free to Run**: Because it does not use commercial AI tokens or paid APIs, this repository can run forever for free on GitHub Actions.
* **Lightning Fast**: An entire weekly roundup is processed and linked in less than one second.
* **Easy to Improve**: If a new council or nickname appears in a post, anyone can easily add it to the lookup file with a simple edit.

---

## Where to Go Next

* **Want to download or use the data?** See [Consuming the Data](consuming-the-data.md) for direct download links and simple instructions.
* **Want to see what information is inside each file?** See [Data Structure](data-structure.md) for field descriptions.
* **Curious how councils and libraries are matched?** See [Entity Matching](entity-matching.md).
* **Want to see how the automated schedule runs?** See [Automation & Scheduling](automation.md).

---

## Content License & Attribution

All news content extracted from Public Libraries News is made available under the **Creative Commons Attribution (CC BY 4.0)** license, respecting the work of Ian Anstice and The Library Campaign.

When using this data in your own applications, please include attribution:
> *Source: Public Libraries News (https://www.publiclibrariesnews.com/), curated by Ian Anstice / The Library Campaign.*
