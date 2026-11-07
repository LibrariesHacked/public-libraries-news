import json
import glob

def main():
    unmatched = []
    for f in glob.glob("data/stories/*.json"):
        stories = json.load(open(f, encoding="utf-8"))
        for s in stories:
            if s["section"] in ("local_news", "changes") and not s.get("resolution", {}).get("library_service"):
                unmatched.append((s["section"], s["entity_raw"], s["text"][:120], s.get("resolution")))

    print(f"Total unmatched local/changes: {len(unmatched)}")
    for section, entity, text, res in unmatched:
        print(f"[{section}] '{entity}' (res={res.get('entity_type')}) -> {text}")

if __name__ == "__main__":
    main()
