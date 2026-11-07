"""
Entity resolver and content classifier for PLN stories.
Links stories to UK Local Authorities, Countries, and Library branches from LibraryCommons,
and classifies stories into standardized library taxonomy categories, sector bodies, and financial amounts.
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
    StoryClassification,
)

def _clean_str(s: str) -> str:
    """Normalize string for comparison (lowercase, strip non-alphanumeric)."""
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()

class EntityResolver:
    CATEGORY_PATTERNS = [
        ("closures_and_threats", r"\b(clos(e|ed|ing|ure|ures)|threat(en|ened|s)?|ax(ed|ing)?)\b"),
        ("cuts_and_finance", r"\b(budget|cuts?|savings|saving|deficit|section 114|s114|bankruptcy|funding|capital|grant|investment)\b"),
        ("staffing_and_unions", r"\b(staff|staffing|unison|strike|strikes|job|jobs|redundanc(y|ies)|librarian|librarians)\b"),
        ("volunteers_and_community", r"\b(volunteer|volunteers|volunteering|community[- ](run|led)|handover|transferred)\b"),
        ("opening_hours", r"\b(hours|opening (hours|times)|reduced hours|expanded hours|staffed hours)\b"),
        ("unstaffed_open_plus", r"\b(unstaffed|staffless|open\+|open plus|openplus|automated access)\b"),
        ("refurbishment_and_new_builds", r"\b(refurbish(ment|ed)?|renovat(ion|ed)?|reopen(ed|ing)?|new (library|building)|revamp|facelift)\b"),
        ("book_bans_and_challenges", r"\b(book ban(s|ning)?|challenge(d|s)?|censorship|restricted|trans(gender)? books?|pride)\b"),
        ("campaigns_and_protests", r"\b(campaign(ers?|s)?|protest(ers?|s)?|demonstrat(ion|ors)?|petition|save our library|legal challenge)\b"),
        ("events_and_activities", r"\b(activities|event|events|author|workshop|exhibition|reading challenge|summer reading|club)\b"),
        ("digital_and_technology", r"\b(ai|artificial intelligence|digital|ebooks?|e-books?|computers?|wifi|wi-fi|podcasts?)\b"),
        ("mobile_and_outreach", r"\b(mobile (library|libraries)|van|mobiles|outreach|home library)\b"),
        ("governance_and_trusts", r"\b(trust|trusts|charitable trust|in-house|mutual|leisure trust|gll|greenwich leisure|libraries unlimited|aura)\b"),
        ("warm_spaces_and_wellbeing", r"\b(warm space(s)?|warm bank(s)?|warm welcome|wellbeing|cost of living|food bank)\b"),
        ("co_location", r"\b(co-locat(ed|ion|ing)?|hub|community hub|shared building|civic centre)\b"),
    ]

    # Category precedence for primary_category determination
    PRIMARY_PRIORITY = [
        "closures_and_threats",
        "cuts_and_finance",
        "book_bans_and_challenges",
        "unstaffed_open_plus",
        "volunteers_and_community",
        "staffing_and_unions",
        "opening_hours",
        "refurbishment_and_new_builds",
        "campaigns_and_protests",
        "mobile_and_outreach",
        "governance_and_trusts",
        "co_location",
        "digital_and_technology",
        "warm_spaces_and_wellbeing",
        "events_and_activities",
    ]

    SECTOR_BODIES = {
        "DCMS": r"\b(dcms|department for culture, media and sport)\b",
        "Arts Council England": r"\b(arts council|ace)\b",
        "CILIP": r"\b(cilip)\b",
        "Libraries Connected": r"\b(libraries connected|scl)\b",
        "The Library Campaign": r"\b(the library campaign)\b",
        "British Library": r"\b(british library)\b",
        "UNISON": r"\b(unison)\b",
        "The Reading Agency": r"\b(the reading agency|reading agency)\b",
        "Scottish Library and Information Council": r"\b(slic|scottish library and information council)\b",
        "Welsh Government": r"\b(welsh government|malg)\b"
    }

    FINANCIAL_REGEX = re.compile(
        r"([£\$€]\s?[0-9]+(?:[\.,][0-9]+)?\s?(?:m|k|million|billion|thousand)?)",
        re.IGNORECASE
    )

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

    def resolve(self, entity_raw: str, text: str, section: str) -> Tuple[EntityResolution, StoryClassification, List[str]]:
        """
        Given the raw entity heading, story body text, and section name,
        resolve entity type, country, library service, specific libraries, coordinates,
        classification metadata, and tags.
        """
        clean_entity = _clean_str(entity_raw)
        resolution = EntityResolution(entity_type="general")
        classification, tags = self._classify_story(text, section, entity_raw)

        # A. If international_news, prioritize country matching
        if section == "international_news":
            if clean_entity in self.countries_aliases:
                canonical_country = self.countries_aliases[clean_entity]
                cdata = self.countries_by_name.get(canonical_country, {})
                resolution.entity_type = "country" if cdata.get("code") != "GLOBAL" else "international"
                resolution.country = canonical_country
                resolution.country_code = cdata.get("code")
                return resolution, classification, tags

            # Check individual tokens in entity (e.g. "USA / National", "Australia - Sydney")
            for word in clean_entity.split():
                if len(word) >= 2 and word in self.countries_aliases:
                    canonical_country = self.countries_aliases[word]
                    cdata = self.countries_by_name.get(canonical_country, {})
                    resolution.entity_type = "country" if cdata.get("code") != "GLOBAL" else "international"
                    resolution.country = canonical_country
                    resolution.country_code = cdata.get("code")
                    return resolution, classification, tags

            # Scan snippet/entity for countries/states
            clean_intl_snippet = f" {clean_entity} {_clean_str(text[:250])} "
            for alias, canon in self.countries_aliases.items():
                if len(alias) >= 4 and f" {alias} " in clean_intl_snippet:
                    canonical_country = canon
                    cdata = self.countries_by_name.get(canonical_country, {})
                    resolution.entity_type = "country" if cdata.get("code") != "GLOBAL" else "international"
                    resolution.country = canonical_country
                    resolution.country_code = cdata.get("code")
                    return resolution, classification, tags

        # B. UK Local Authority Match (prioritized for local_news, changes, etc.)
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
                combined_search = f" {clean_entity} {_clean_str(text[:250])} "
                for lib in self.all_libraries:
                    lname = _clean_str(lib["name"])
                    if len(lname) >= 7 and lname not in ["central library", "community library", "mobile library"]:
                        if f" {lname} " in combined_search:
                            acode = lib.get("authority_code")
                            if acode and acode in self.authorities_by_code:
                                matched_auth = self.authorities_by_code[acode]
                                confidence = "fuzzy"
                                break

            # If still not matched, check if an authority name appears in the snippet/source citation
            if not matched_auth and section in ["local_news", "changes"]:
                clean_snippet = f" {_clean_str(text[:250])} "
                for alias, canon in self.authorities_aliases.items():
                    if len(alias) >= 5 and f" {alias} " in clean_snippet:
                        matched_auth = self.authorities_by_name.get(canon)
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

            return resolution, classification, tags

        # D. If in international news and not yet matched, scan snippet for countries/states
        if section == "international_news":
            clean_intl_snippet = f" {clean_entity} {_clean_str(text[:250])} "
            for alias, canon in self.countries_aliases.items():
                if len(alias) >= 4 and f" {alias} " in clean_intl_snippet:
                    canonical_country = canon
                    cdata = self.countries_by_name.get(canonical_country, {})
                    resolution.entity_type = "country" if cdata.get("code") != "GLOBAL" else "international"
                    resolution.country = canonical_country
                    resolution.country_code = cdata.get("code")
                    return resolution, classification, tags

        # E. Fallback: check if raw entity contains any national bodies
        if any(term in clean_entity for term in ["dcms", "arts council", "cilip", "british library", "the reading agency", "libraries connected"]):
            resolution.entity_type = "national"
            resolution.country = "United Kingdom"
            resolution.country_code = "GB"

        return resolution, classification, tags

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

            short_name = re.sub(r"\b(library|community library|hub|branch)\b", "", clean_full).strip()

            matched = False
            if clean_full and f" {clean_full} " in clean_text_spaced:
                matched = True
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

    def _classify_story(self, text: str, section: str, entity_raw: str) -> Tuple[StoryClassification, List[str]]:
        """Extract taxonomy categories, change_type, sector bodies, money mentions, and tags."""
        combined_text = f"{entity_raw} {text}"
        low = combined_text.lower()

        # 1. Categories
        categories = []
        for cat_name, pattern in self.CATEGORY_PATTERNS:
            if re.search(pattern, low):
                categories.append(cat_name)

        # 2. Primary category by precedence
        primary_category = None
        for p_cat in self.PRIMARY_PRIORITY:
            if p_cat in categories:
                primary_category = p_cat
                break

        # 3. Change Type (specifically for changes section)
        change_type = None
        if section == "changes":
            if "unstaffed_open_plus" in categories:
                change_type = "unstaffed_open_plus"
            elif "closures_and_threats" in categories:
                change_type = "closure"
            elif "volunteers_and_community" in categories:
                change_type = "community_handover"
            elif "cuts_and_finance" in categories or "opening_hours" in categories:
                change_type = "reduction_or_cut"
            elif "refurbishment_and_new_builds" in categories:
                change_type = "investment_or_expansion"
            else:
                change_type = "other"

        # 4. Sector bodies mentioned
        sector_bodies = []
        for body_name, pattern in self.SECTOR_BODIES.items():
            if re.search(pattern, low):
                sector_bodies.append(body_name)

        # 5. Financial mentions
        raw_money = self.FINANCIAL_REGEX.findall(combined_text)
        # Clean up whitespace inside extracted amounts (e.g. "£ 1m" -> "£1m")
        financial_mentions = [re.sub(r"\s+", "", m) for m in raw_money]

        classification = StoryClassification(
            categories=categories,
            primary_category=primary_category,
            change_type=change_type,
            sector_bodies_mentioned=sector_bodies,
            financial_mentions=financial_mentions
        )

        return classification, categories
