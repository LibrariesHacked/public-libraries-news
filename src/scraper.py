"""
Polite WordPress REST API scraper for Public Libraries News.
Fetches posts incrementally or in backfill mode.
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
import urllib.request
import urllib.error
from html import unescape

from .models import Post, EditorialContent, Attribution, PostStats
from .parser import PLNPostParser
from .resolver import EntityResolver
from .storage import PLNStorage

USER_AGENT = (
    "PublicLibrariesNewsBot/1.0 "
    "(+https://github.com/LibrariesHacked/public-libraries-news; info@librarieshacked.org)"
)

class PLNScraper:
    def __init__(
        self,
        base_url: str = "https://www.publiclibrariesnews.com",
        storage: Optional[PLNStorage] = None,
        resolver: Optional[EntityResolver] = None,
        rate_limit_delay: float = 1.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_endpoint = f"{self.base_url}/wp-json/wp/v2/posts"
        self.storage = storage or PLNStorage()
        self.resolver = resolver or EntityResolver()
        self.parser = PLNPostParser(resolver=self.resolver)
        self.rate_limit_delay = rate_limit_delay

    def _fetch_json(self, url: str) -> Optional[Any]:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                return json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 400:
                # WordPress pagination end returns 400 when page > total_pages
                return None
            print(f"HTTP Error {e.code} fetching {url}: {e.reason}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def process_raw_post(self, raw_post: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Convert WordPress REST post payload into Post model and Story items."""
        source_id = raw_post["id"]
        post_date = raw_post.get("date_gmt") or raw_post.get("date") or ""
        post_modified = raw_post.get("modified_gmt") or raw_post.get("modified") or post_date
        title = unescape(raw_post.get("title", {}).get("rendered", "Public Libraries News"))
        slug = raw_post.get("slug", "")
        url = raw_post.get("link", f"{self.base_url}/?p={source_id}")
        author_name = "Ian Anstice / The Library Campaign"

        content_html = raw_post.get("content", {}).get("rendered", "")

        try:
            editorial_dict, stories, sections_found = self.parser.parse_post(
                source_id=source_id,
                post_date=post_date,
                post_html=content_html
            )
        except Exception as e:
            print(f"Warning: Exception parsing post {source_id} ({slug}): {e}")
            editorial_dict = {"text": "", "html": ""}
            stories = []
            sections_found = []

        story_ids = [s["id"] for s in stories]

        # Compute post-level statistics
        authorities = set()
        libraries = set()
        countries = set()
        cat_counts: Dict[str, int] = {}

        for s in stories:
            res = s.get("resolution", {})
            auth = res.get("library_service")
            if auth and auth.get("name"):
                authorities.add(auth["name"])
            for lib in res.get("libraries_mentioned", []):
                libraries.add(lib["id"])
            if res.get("country"):
                countries.add(res["country"])

            for cat in s.get("classification", {}).get("categories", []):
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

        stats = PostStats(
            authorities_count=len(authorities),
            libraries_count=len(libraries),
            countries_count=len(countries),
            top_categories=dict(sorted(cat_counts.items(), key=lambda x: x[1], reverse=True))
        )

        post = Post(
            id=f"pln-post-{source_id}",
            source_id=source_id,
            url=url,
            slug=slug,
            title=title,
            date_published=post_date,
            date_modified=post_modified,
            author=author_name,
            editorial=EditorialContent(
                text=editorial_dict["text"],
                html=editorial_dict["html"]
            ),
            sections_found=sections_found,
            stories_count=len(stories),
            story_ids=story_ids,
            stats=stats,
            attribution=Attribution()
        )

        return post.to_dict(), stories

    def run_incremental(self, per_page: int = 10) -> int:
        """
        Check page 1 of recent posts. If all posts match the index, exit immediately.
        Otherwise parse new/updated posts and save them.
        Returns count of new/updated posts processed.
        """
        index = self.storage.load_index()
        url = f"{self.api_endpoint}?page=1&per_page={per_page}&orderby=date&order=desc"
        print(f"Checking for latest posts: {url}")

        raw_posts = self._fetch_json(url)
        if not raw_posts:
            print("No posts returned from API or unable to connect.")
            return 0

        updated_count = 0
        latest_post_saved = None
        latest_stories_saved = None

        for raw_post in raw_posts:
            source_id = raw_post["id"]
            modified = raw_post.get("modified_gmt") or raw_post.get("modified")

            # Check if post already recorded and not modified since
            if source_id in index and index[source_id].get("date_modified") == modified:
                continue

            print(f"Processing new/updated post {source_id}: {raw_post.get('slug')}")
            post_dict, stories = self.process_raw_post(raw_post)
            self.storage.save_post(post_dict, stories)

            # Keep track of latest for data/latest.json
            if latest_post_saved is None:
                latest_post_saved = post_dict
                latest_stories_saved = stories

            # Update index entry
            index[source_id] = {
                "id": post_dict["id"],
                "source_id": source_id,
                "date_published": post_dict["date_published"],
                "date_modified": post_dict["date_modified"],
                "title": post_dict["title"],
                "slug": post_dict["slug"],
                "url": post_dict["url"],
                "stories_count": len(stories),
            }
            updated_count += 1

        if updated_count > 0:
            self.storage.save_index(index)
            if latest_post_saved and latest_stories_saved is not None:
                self.storage.update_latest(latest_post_saved, latest_stories_saved)
            print(f"Updated {updated_count} posts successfully.")
        else:
            print("No new or modified posts found. Everything is up to date.")

        return updated_count

    def run_backfill(self, max_pages: Optional[int] = None, per_page: int = 50) -> int:
        """
        Paginate through all historical posts from the WordPress API.
        """
        index = self.storage.load_index()
        page = 1
        total_processed = 0
        latest_post_saved = None
        latest_stories_saved = None

        print(f"Starting historical backfill from page {page}...")

        while True:
            if max_pages and page > max_pages:
                print(f"Reached user page limit ({max_pages}). Stopping.")
                break

            url = f"{self.api_endpoint}?page={page}&per_page={per_page}&orderby=date&order=desc"
            print(f"Fetching page {page}: {url}")
            raw_posts = self._fetch_json(url)

            if not raw_posts or not isinstance(raw_posts, list) or len(raw_posts) == 0:
                print(f"Reached end of posts at page {page}.")
                break

            for raw_post in raw_posts:
                source_id = raw_post["id"]
                modified = raw_post.get("modified_gmt") or raw_post.get("modified")

                # Skip if already exists with same modified timestamp
                if source_id in index and index[source_id].get("date_modified") == modified:
                    continue

                post_dict, stories = self.process_raw_post(raw_post)
                self.storage.save_post(post_dict, stories)

                if latest_post_saved is None and page == 1:
                    latest_post_saved = post_dict
                    latest_stories_saved = stories

                index[source_id] = {
                    "id": post_dict["id"],
                    "source_id": source_id,
                    "date_published": post_dict["date_published"],
                    "date_modified": post_dict["date_modified"],
                    "title": post_dict["title"],
                    "slug": post_dict["slug"],
                    "url": post_dict["url"],
                    "stories_count": len(stories),
                }
                total_processed += 1

            self.storage.save_index(index)
            page += 1
            time.sleep(self.rate_limit_delay)

        if latest_post_saved and latest_stories_saved is not None:
            self.storage.update_latest(latest_post_saved, latest_stories_saved)

        print(f"Backfill complete! Processed {total_processed} posts in total.")
        return total_processed
