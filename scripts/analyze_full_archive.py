import json
import glob
import os
from collections import Counter

def main():
    story_files = sorted(glob.glob("data/stories/*.json"))
    post_index_path = "data/posts_index.json"

    with open(post_index_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    total_posts = len(posts)
    earliest_post = posts[-1] if posts else None
    latest_post = posts[0] if posts else None

    print(f"=== POSTS SUMMARY ===")
    print(f"Total posts indexed: {total_posts}")
    if earliest_post and latest_post:
        print(f"Date range: {earliest_post['date_published'][:10]} to {latest_post['date_published'][:10]}")

    total_stories = 0
    by_year = {}
    by_section = Counter()
    matched_by_sec = Counter()
    unmatched_local = Counter()
    unmatched_changes = Counter()
    unmatched_intl = Counter()
    unmatched_national = Counter()
    library_matches_count = 0
    cat_counter = Counter()
    change_type_counter = Counter()
    sector_body_counter = Counter()

    for sf in story_files:
        year = os.path.basename(sf).replace(".json", "")
        with open(sf, "r", encoding="utf-8") as f:
            stories = json.load(f)

        by_year[year] = len(stories)
        total_stories += len(stories)

        for s in stories:
            sec = s["section"]
            by_section[sec] += 1
            res = s.get("resolution", {})
            cls_obj = s.get("classification", {})

            # Match checking
            is_matched = False
            if sec in ["local_news", "changes"]:
                if res.get("library_service"):
                    is_matched = True
                    matched_by_sec[sec] += 1
                else:
                    if sec == "local_news":
                        unmatched_local[s.get("entity_raw", "")] += 1
                    else:
                        unmatched_changes[s.get("entity_raw", "")] += 1
            elif sec == "international_news":
                if res.get("country"):
                    is_matched = True
                    matched_by_sec[sec] += 1
                else:
                    unmatched_intl[s.get("entity_raw", "")] += 1
            else:
                if res.get("library_service") or res.get("country") or res.get("entity_type") == "national":
                    is_matched = True
                    matched_by_sec[sec] += 1
                else:
                    unmatched_national[s.get("entity_raw", "")] += 1

            # Library branches
            if res.get("libraries_mentioned"):
                library_matches_count += 1

            # Taxonomy
            for cat in cls_obj.get("categories", []):
                cat_counter[cat] += 1
            if cls_obj.get("change_type"):
                change_type_counter[cls_obj["change_type"]] += 1
            for body in cls_obj.get("sector_bodies_mentioned", []):
                sector_body_counter[body] += 1

    print(f"\n=== STORIES BY YEAR ({len(by_year)} years) ===")
    for yr in sorted(by_year.keys()):
        print(f"  {yr}: {by_year[yr]:>5} stories")
    print(f"  TOTAL STORIES: {total_stories:,}")

    print(f"\n=== ENTITY MATCHING BY SECTION ===")
    for sec in sorted(by_section.keys()):
        cnt = by_section[sec]
        m = matched_by_sec[sec]
        pct = (m / cnt) * 100 if cnt else 0
        print(f"  {sec:<20}: {m:>6,} / {cnt:>6,} ({pct:.1f}%)")

    print(f"\n=== SPECIFIC LIBRARY BRANCHES (from LibraryCommons) ===")
    lib_pct = (library_matches_count / total_stories) * 100 if total_stories else 0
    print(f"  Stories linked to specific library buildings: {library_matches_count:,} ({lib_pct:.1f}%)")

    print(f"\n=== TOP 20 UNMATCHED ENTITIES IN LOCAL NEWS ===")
    for ent, count in unmatched_local.most_common(20):
        print(f"  {count:>4}x  '{ent}'")

    print(f"\n=== TOP 15 UNMATCHED ENTITIES IN CHANGES ===")
    for ent, count in unmatched_changes.most_common(15):
        print(f"  {count:>4}x  '{ent}'")

    print(f"\n=== TOP 15 UNMATCHED ENTITIES IN INTERNATIONAL NEWS ===")
    for ent, count in unmatched_intl.most_common(15):
        print(f"  {count:>4}x  '{ent}'")

    print(f"\n=== TOP CATEGORIES ===")
    for cat, count in cat_counter.most_common(15):
        pct = (count / total_stories) * 100 if total_stories else 0
        print(f"  {cat:<30}: {count:>6,} ({pct:.1f}%)")

    print(f"\n=== CHANGE TYPES ===")
    for ct, count in change_type_counter.most_common():
        print(f"  {ct:<30}: {count:>6,}")

    print(f"\n=== SECTOR BODIES MENTIONED ===")
    for sb, count in sector_body_counter.most_common():
        print(f"  {sb:<30}: {count:>6,}")

if __name__ == "__main__":
    main()
