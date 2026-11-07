#!/usr/bin/env python3
"""
Compile raw library JSON files from LibraryCommons into an optimized lookup dataset.
"""

import json
import os
import sys

def build_libraries_lookup(source_dir: str, output_path: str):
    if not os.path.exists(source_dir):
        print(f"Directory {source_dir} not found")
        return

    libraries = []
    authorities = set()
    count = 0

    for entry in os.scandir(source_dir):
        if not entry.name.endswith(".json"):
            continue
        count += 1
        try:
            with open(entry.path, "r", encoding="utf-8") as f:
                item = json.load(f)
                data = item.get("data", {})
                name = data.get("Library name")
                if not name:
                    continue

                auth_name = data.get("Local authority")
                auth_code = data.get("Local authority code")
                if auth_name:
                    authorities.add(auth_name)

                libraries.append({
                    "id": item.get("id"),
                    "name": name.strip(),
                    "authority": auth_name.strip() if auth_name else None,
                    "authority_code": auth_code.strip() if auth_code else None,
                    "postcode": data.get("Postcode"),
                    "lat": data.get("Latitude"),
                    "lng": data.get("Longitude"),
                    "status": data.get("Status", "Open"),
                    "slug": item.get("slug")
                })
        except Exception as e:
            print(f"Error reading {entry.path}: {e}", file=sys.stderr)

    libraries.sort(key=lambda x: (x.get("authority") or "", x.get("name") or ""))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(libraries, out, indent=2, ensure_ascii=False)

    print(f"Successfully compiled {len(libraries)} libraries across {len(authorities)} authorities to {output_path}")

if __name__ == "__main__":
    src = os.path.join("temp_libraryon", "src", "content", "libraries")
    dest = os.path.join("data", "lookups", "libraries.json")
    build_libraries_lookup(src, dest)

