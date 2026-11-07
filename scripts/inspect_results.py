"""
Dataset inspection script for parsed stories and posts.

Inspects parsed posts and stories to verify entity resolution rates, link extraction,
clean text formatting, and unresolved entity outliers.
"""

import json
import glob
import re

def analyze_all():
    """Inspect recently parsed posts and stories to report resolution and formatting quality.

    Checks resolved authority counts, international country coverage, branch mentions,
    and identifies any story entities failing resolution.
    """
    posts = glob.glob("data/posts/*/*.json")
    print(f"Total Posts Loaded: {len(posts)}\n")

    total_stories = 0
    resolved_auth = 0
    resolved_country = 0
    with_libs = 0
    with_links = 0
    unstripped_dashes = 0
    unresolved_entities = set()

    for p_path in sorted(posts)[-5:]:
        with open(p_path, "r", encoding="utf-8") as f:
            post = json.load(f)

        print(f"Sample Post {post['source_id']} ({post['date_published'][:10]}): {post['title'][:50]}...")
        print(f"  Stories: {post['stories_count']} | Sections: {post['sections_found']}")

    stories_files = glob.glob("data/stories/*.json")
    for s_file in stories_files:
        with open(s_file, "r", encoding="utf-8") as f:
            stories = json.load(f)
            total_stories += len(stories)
            for s in stories:
                res = s.get("resolution", {})
                if res.get("library_service"):
                    resolved_auth += 1
                elif s["section"] in ["local_news", "changes"]:
                    unresolved_entities.add((s["section"], s["entity_raw"]))

                if res.get("country"):
                    resolved_country += 1

                if res.get("libraries_mentioned"):
                    with_libs += 1

                if s.get("links"):
                    with_links += 1

                if re.match(r"^[\s\u2013\u2014\-:]", s.get("text", "")):
                    unstripped_dashes += 1

    print("\n--- AGGREGATE METRICS ---")
    print(f"Total Stories Parsed: {total_stories}")
    print(f"Stories with Resolved UK Authority: {resolved_auth}")
    print(f"Stories with Resolved Country: {resolved_country}")
    print(f"Stories with Libraries Mentioned: {with_libs}")
    print(f"Stories with Hyperlinks: {with_links}")
    print(f"Stories with leading dash in text: {unstripped_dashes}")

    if unresolved_entities:
        print(f"\nUnresolved entities in Local News / Changes ({len(unresolved_entities)}):")
        for sec, ent in sorted(unresolved_entities)[:25]:
            print(f"  [{sec}] '{ent}'")

if __name__ == "__main__":
    analyze_all()
