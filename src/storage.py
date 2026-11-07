"""
Storage manager for PLN data files, partitions, and indexes.

Manages reading, writing, and atomic updating of weekly post files,
yearly story partitions, catalog indexes, and quick-feed summaries.
"""

import json
import os
from typing import Dict, List, Optional, Any

class PLNStorage:
    """Handles file persistence for weekly posts, yearly story partitions, and manifests.
    
    Provides isolated file write operations and keeps catalog indexes synchronized.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """Initialize storage directories and file paths under the target data directory.
        
        Args:
            base_dir: Optional root path for data storage; defaults to the repo's data/ folder.
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.base_dir = os.path.abspath(base_dir)
        self.posts_dir = os.path.join(self.base_dir, "posts")
        self.stories_dir = os.path.join(self.base_dir, "stories")
        self.index_file = os.path.join(self.base_dir, "posts_index.json")
        self.latest_file = os.path.join(self.base_dir, "latest.json")

        os.makedirs(self.posts_dir, exist_ok=True)
        os.makedirs(self.stories_dir, exist_ok=True)

    def load_index(self) -> Dict[int, Dict[str, Any]]:
        """Load manifest of already scraped posts, keyed by source_id."""
        if not os.path.exists(self.index_file):
            return {}
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {item["source_id"]: item for item in data}
        except Exception:
            return {}

    def save_index(self, index_dict: Dict[int, Dict[str, Any]]):
        """Save sorted manifest of all posts."""
        items = list(index_dict.values())
        # Sort descending by publication date
        items.sort(key=lambda x: x.get("date_published", ""), reverse=True)
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

    def save_post(self, post_dict: Dict[str, Any], stories: List[Dict[str, Any]]):
        """Save post JSON and append stories to corresponding year partition."""
        date_str = post_dict.get("date_published", "")
        year = date_str[:4] if len(date_str) >= 4 else "unknown"
        post_id = post_dict["id"]
        source_id = post_dict["source_id"]
        date_prefix = date_str[:10] if len(date_str) >= 10 else "undated"

        # 1. Save individual post file in data/posts/YYYY/
        year_posts_dir = os.path.join(self.posts_dir, year)
        os.makedirs(year_posts_dir, exist_ok=True)
        post_filename = f"{date_prefix}-pln-{source_id}.json"
        post_path = os.path.join(year_posts_dir, post_filename)

        with open(post_path, "w", encoding="utf-8") as f:
            json.dump(post_dict, f, indent=2, ensure_ascii=False)

        # 2. Append/Update stories in data/stories/YYYY.json
        year_stories_path = os.path.join(self.stories_dir, f"{year}.json")
        existing_stories: List[Dict[str, Any]] = []
        if os.path.exists(year_stories_path):
            try:
                with open(year_stories_path, "r", encoding="utf-8") as f:
                    existing_stories = json.load(f)
            except Exception:
                existing_stories = []

        # Remove previous stories for this post_id if re-parsing/updating
        filtered = [s for s in existing_stories if s.get("post_id") != post_id]
        filtered.extend(stories)
        # Sort stories by post_date desc, then story id asc
        filtered.sort(key=lambda s: (s.get("post_date", ""), s.get("id", "")), reverse=True)

        with open(year_stories_path, "w", encoding="utf-8") as f:
            json.dump(filtered, f, indent=2, ensure_ascii=False)

    def update_latest(self, post_dict: Dict[str, Any], stories: List[Dict[str, Any]]):
        """Write data/latest.json containing the latest post and its stories."""
        latest_data = {
            "latest_post": post_dict,
            "stories_count": len(stories),
            "stories": stories
        }
        with open(self.latest_file, "w", encoding="utf-8") as f:
            json.dump(latest_data, f, indent=2, ensure_ascii=False)
