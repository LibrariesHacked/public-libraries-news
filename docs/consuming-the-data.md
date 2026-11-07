# Consuming the Data

All data in this repository is completely public and can be loaded directly by any website, dashboard, or analytical notebook without needing an API key.

---

## Direct Data URLs

You can fetch files directly from GitHub's raw CDN or via jsDelivr:

| Resource | GitHub Raw URL | Description |
|---|---|---|
| **Latest Stories** | `https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/latest.json` | The most recent weekly post and its parsed stories |
| **All Posts Index** | `https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/posts_index.json` | Catalog of all posts with dates, titles, and story counts |
| **Yearly Stories** | `https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/stories/2024.json` | Array of all stories from a specific year |
| **UK Council Lookup** | `https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/lookups/uk_authorities.json` | All UK library authorities and GSS codes |
| **UK Libraries Lookup**| `https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/lookups/libraries.json` | Over 4,200 UK library branches with coordinates |

---

## Code Examples

### In JavaScript / Web Browser (Fetch API)

```javascript
// Fetch the latest library news stories
async function loadLatestNews() {
  const url = "https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/latest.json";
  const response = await fetch(url);
  const data = await response.json();

  console.log(`Latest post: ${data.latest_post.title}`);
  data.stories.forEach(story => {
    console.log(`[${story.section}] ${story.entity_raw}: ${story.text}`);
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
print(df[["post_date", "section", "entity_raw", "text"]].head())

# Filter for stories with closures or cuts
cuts_df = df[df["tags"].apply(lambda tags: "cuts" in tags or "closures" in tags)]
print(f"Total cut/closure stories in 2024: {len(cuts_df)}")
```

---

### In cURL / Command Line

```bash
curl -s https://raw.githubusercontent.com/LibrariesHacked/public-libraries-news/main/data/latest.json | jq '.latest_post.title'
```
