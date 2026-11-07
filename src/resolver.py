"""
Entity resolver for linking PLN stories to UK Local Authorities,
Countries, and specific Library branches from LibraryCommons.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple, Any

from .models import (
    EntityResolution,
    LibraryServiceRef,
    LibraryMention,
    Coordinates,
)

def _clean_str(s: str) -> str:
    """Normalize string for comparison (lowercase, strip non-alphanumeric)."""
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()

class EntityResolver:
    def __init__(self, lookups_dir: Optional[str] = None):
        if lookups_dir is None:
            lookups_dir = os.path.join(os.path.dirname(__file__), "..", "data", "lookups")

        self.lookups_dir = os.path.abspath(lookups_dir)
        self.authorities_by_name: Dict[str, Dict[str, Any]] = {}
        self.authorities_by_code: Dict[str, Dict[str, Any]] = {}
        self.authorities_aliases: Dict[str, str] = {}  # clean_alias -> canonical_name
        self.countries_by_name: Dict[str, Dict[str, Any]] = {}
        self.countries_aliases: Dict[str, str] = {}
        self.libraries_by_auth_code: Dict[str, List[Dict[str, Any]]] = {}
        self.all_libraries: List[Dict[str, Any]] = []

        self._load_lookups()

    def _load_lookups(self):
        # 1. UK Authorities
        auth_path = os.path.join(self.lookups_dir, "uk_authorities.json")
        if os.path.exists(auth_path):
            with open(auth_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for auth in data.get("authorities", []):
                    canonical_name = auth["name"]
                    self.authorities_by_name[canonical_name] = auth
                    if auth.get("gss_code"):
                        self.authorities_by_code[auth["gss_code"]] = auth

                    clean_name = _clean_str(canonical_name)
                    self.authorities_aliases[clean_name] = canonical_name

                    for alias in auth.get("aliases", []):
                        self.authorities_aliases[_clean_str(alias)] = canonical_name

        # 2. Countries
        country_path = os.path.join(self.lookups_dir, "countries.json")
        if os.path.exists(country_path):
            with open(country_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for country in data.get("countries", []):
                    c_name = country["name"]
                    self.countries_by_name[c_name] = country
                    self.countries_aliases[_clean_str(c_name)] = c_name
                    for alias in country.get("aliases", []):
                        self.countries_aliases[_clean_str(alias)] = c_name

        # 3. Libraries (LibraryCommons)
        lib_path = os.path.join(self.lookups_dir, "libraries.json")
        if os.path.exists(lib_path):
            with open(lib_path, "r", encoding="utf-8") as f:
                self.all_libraries = json.load(f)
                for lib in self.all_libraries:
                    acode = lib.get("authority_code")
                    if acode:
                        self.libraries_by_auth_code.setdefault(acode, []).append(lib)

    def resolve(self, entity_raw: str, text: str, section: str) -> Tuple[EntityResolution, List[str]]:
        """
        Given the raw entity heading, story body text, and section name,
        resolve entity type, country, library service, specific libraries, coordinates, and tags.
        """
        clean_entity = _clean_str(entity_raw)
        resolution = EntityResolution(entity_type="general")
        tags = self._extract_tags(text)

        # A. Check if section is international or entity matches a known country
        is_international = section == "international_news" or clean_entity in self.countries_aliases
        if is_international and clean_entity in self.countries_aliases:
            canonical_country = self.countries_aliases[clean_entity]
            cdata = self.countries_by_name.get(canonical_country, {})
            resolution.entity_type = "country"
            resolution.country = canonical_country
            resolution.country_code = cdata.get("code")
            return resolution, tags

        # B. UK Local Authority Match
        matched_auth = None
        confidence = "exact"

        if clean_entity in self.authorities_aliases:
            canon_name = self.authorities_aliases[clean_entity]
            matched_auth = self.authorities_by_name.get(canon_name)
            confidence = "exact" if clean_entity == _clean_str(canon_name) else "alias"
        else:
            # Try fuzzy word-boundary match (e.g. "Birmingham City Council" -> "Birmingham")
            for alias, canon in self.authorities_aliases.items():
                if len(alias) >= 4 and (f" {alias} " in f" {clean_entity} " or clean_entity.startswith(alias)):
                    matched_auth = self.authorities_by_name.get(canon)
                    confidence = "fuzzy"
                    break

            # If in local news or changes and still not matched, check if a known library branch is mentioned
            if not matched_auth and section in ["local_news", "changes"] and len(clean_entity) > 3:
                combined_search = f" {clean_entity} {_clean_str(text[:200])} "
                for lib in self.all_libraries:
                    lname = _clean_str(lib["name"])
                    if len(lname) >= 8 and lname not in ["central library", "community library", "mobile library"]:
                        if f" {lname} " in combined_search:
                            acode = lib.get("authority_code")
                            if acode and acode in self.authorities_by_code:
                                matched_auth = self.authorities_by_code[acode]
                                confidence = "fuzzy"
                                break

        if matched_auth:
            resolution.entity_type = "local_authority"
            resolution.country = matched_auth.get("country", "England")
            resolution.country_code = "GB"
            resolution.library_service = LibraryServiceRef(
                name=matched_auth["name"],
                gss_code=matched_auth.get("gss_code"),
                confidence=confidence
            )
            if matched_auth.get("lat") and matched_auth.get("lng"):
                resolution.coordinates = Coordinates(
                    latitude=matched_auth["lat"],
                    longitude=matched_auth["lng"]
                )

            # C. Match Specific Libraries under this Authority
            auth_code = matched_auth.get("gss_code")
            if auth_code and auth_code in self.libraries_by_auth_code:
                auth_libs = self.libraries_by_auth_code[auth_code]
                resolution.libraries_mentioned = self._match_libraries_in_text(text, auth_libs)

            return resolution, tags

        # D. If not matched to UK Authority, check if it's international
        if clean_entity in self.countries_aliases:
            canonical_country = self.countries_aliases[clean_entity]
            cdata = self.countries_by_name.get(canonical_country, {})
            resolution.entity_type = "country"
            resolution.country = canonical_country
            resolution.country_code = cdata.get("code")
            return resolution, tags

        # E. Fallback: check if raw entity contains any national bodies
        if any(term in clean_entity for term in ["dcms", "arts council", "cilip", "british library", "the reading agency"]):
            resolution.entity_type = "national"
            resolution.country = "United Kingdom"
            resolution.country_code = "GB"

        return resolution, tags

    def _match_libraries_in_text(self, text: str, candidates: List[Dict[str, Any]]) -> List[LibraryMention]:
        """Check candidates to see if any branch names appear in the story text."""
        mentions: List[LibraryMention] = []
        clean_text_spaced = f" {_clean_str(text)} "
        seen_ids = set()

        for lib in candidates:
            lib_id = lib.get("id")
            if not lib_id or lib_id in seen_ids:
                continue

            full_name = lib.get("name", "")
            clean_full = _clean_str(full_name)

            # E.g. "Harborne Library" -> also consider "Harborne" if > 4 chars and not a generic word
            short_name = re.sub(r"\b(library|community library|hub|branch)\b", "", clean_full).strip()

            matched = False
            # Check full name: e.g. "harborne library"
            if clean_full and f" {clean_full} " in clean_text_spaced:
                matched = True
            # Check short name if distinctive (e.g. "harborne", "selly oak")
            elif len(short_name) >= 5 and short_name not in ["central", "branch", "mobile", "community"]:
                if f" {short_name} library" in clean_text_spaced or f" {short_name} " in clean_text_spaced:
                    matched = True

            if matched:
                seen_ids.add(lib_id)
                mentions.append(LibraryMention(
                    id=lib_id,
                    name=full_name,
                    postcode=lib.get("postcode"),
                    lat=lib.get("lat"),
                    lng=lib.get("lng"),
                    status=lib.get("status", "Open"),
                    slug=lib.get("slug")
                ))

        return mentions

    def _extract_tags(self, text: str) -> List[str]:
        """Extract thematic tags based on story keywords."""
        tags = []
        low = text.lower()
        patterns = {
            "closures": r"\b(closure|closures|closing|closed)\b",
            "cuts": r"\b(cut|cuts|budget|savings|section 114|deficit)\b",
            "opening_hours": r"\b(hours|opening hours|opening times|reduced hours)\b",
            "consultation": r"\b(consultation|consulting|survey|feedback)\b",
            "unstaffed_access": r"\b(unstaffed|open\+|open plus|automated access)\b",
            "volunteers": r"\b(volunteer|volunteers|community-run|community led|handover)\b",
            "refurbishment": r"\b(refurbishment|refurbished|renovation|reopened|reopening|new library)\b",
            "campaign": r"\b(campaign|campaigners|protest|demonstration|petition|rally)\b",
            "industrial_action": r"\b(strike|strikes|industrial action|unison)\b",
            "mobile_libraries": r"\b(mobile library|mobile libraries|mobiles)\b",
        }
        for tag, pattern in patterns.items():
            if re.search(pattern, low):
                tags.append(tag)
        return tags
