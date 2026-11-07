import json
import glob

def detailed_inspection():
    by_section = {}
    unmatched_by_sec = {}

    for f in glob.glob("data/stories/*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            stories = json.load(fp)
        for s in stories:
            sec = s["section"]
            by_section[sec] = by_section.get(sec, 0) + 1
            res = s.get("resolution", {})
            if sec in ["local_news", "changes"]:
                if not res.get("library_service"):
                    unmatched_by_sec.setdefault(sec, []).append(s)
            elif sec == "international_news":
                if not res.get("country"):
                    unmatched_by_sec.setdefault(sec, []).append(s)
            else:
                if not (res.get("library_service") or res.get("country") or res.get("entity_type") == "national"):
                    unmatched_by_sec.setdefault(sec, []).append(s)

    print("=== TOTAL STORIES BY SECTION ===")
    for sec in sorted(by_section.keys()):
        count = by_section[sec]
        unmatched = len(unmatched_by_sec.get(sec, []))
        matched = count - unmatched
        pct = (matched / count) * 100 if count else 0
        print(f"  {sec:<20}: {matched:>4} / {count:>4} matched ({pct:.1f}%)")

    # International unmatched country
    intl_no_country = []
    for f in glob.glob("data/stories/*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            for s in json.load(fp):
                if s["section"] == "international_news" and not s.get("resolution", {}).get("country"):
                    intl_no_country.append(s)

    print(f"\n=== INTERNATIONAL STORIES WITHOUT COUNTRY ({len(intl_no_country)}) ===")
    for s in intl_no_country[:25]:
        print(f"  Entity: '{s['entity_raw']}'")
        print(f"  Snippet: {s['text'][:120]}...\n")

if __name__ == "__main__":
    detailed_inspection()
