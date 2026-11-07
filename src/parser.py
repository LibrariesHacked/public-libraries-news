"""
HTML Parser for Public Libraries News weekly posts.
Splits posts into standard sections (Editorial, Changes, Local news, International news)
and extracts discrete story items with links and entity headings.
"""

from html import unescape
from html.parser import HTMLParser
import re
from typing import Dict, List, Optional, Tuple, Any
import urllib.parse

class HTMLTextExtractor(HTMLParser):
    """Extract plain text, clean HTML, and hyperlinks from an HTML fragment."""
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.links = []
        self._current_link = None
        self._current_link_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "a" and "href" in attrs_dict:
            self._current_link = attrs_dict["href"]
            self._current_link_text = []
        elif tag in ["p", "br", "li", "div", "h1", "h2", "h3", "h4"]:
            self.text_parts.append(" ")

    def handle_endtag(self, tag):
        if tag == "a" and self._current_link:
            link_text = "".join(self._current_link_text).strip()
            if self._current_link and link_text:
                domain = None
                try:
                    parsed = urllib.parse.urlparse(self._current_link)
                    domain = parsed.netloc.lower().replace("www.", "")
                except Exception:
                    pass
                self.links.append({
                    "url": self._current_link,
                    "text": link_text,
                    "domain": domain
                })
            self._current_link = None
            self._current_link_text = []
        elif tag in ["p", "br", "li", "div", "h1", "h2", "h3", "h4"]:
            self.text_parts.append(" ")

    def handle_data(self, data):
        self.text_parts.append(data)
        if self._current_link is not None:
            self._current_link_text.append(data)

    def get_text(self) -> str:
        raw = "".join(self.text_parts)
        # Collapse multiple whitespace/newlines
        return re.sub(r"\s+", " ", raw).strip()

def extract_text_and_links(html_snippet: str) -> Tuple[str, List[Dict[str, str]]]:
    parser = HTMLTextExtractor()
    parser.feed(html_snippet)
    return parser.get_text(), parser.links

def clean_html_fragment(html_snippet: str) -> str:
    """Sanitize HTML fragment, preserving basic links and emphasis while stripping layout tags."""
    # Remove unwanted style and script tags
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html_snippet, flags=re.DOTALL | re.IGNORECASE)
    # Strip span and font tags but keep contents
    s = re.sub(r"</?(span|font|div)[^>]*>", "", s, flags=re.IGNORECASE)
    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s

class PLNPostParser:
    """Parses full WordPress post content into structured sections and stories."""

    SECTION_PATTERNS = [
        ("editorial", r"^(editorial|editorial and national)\b"),
        ("changes", r"^(changes by local authority|changes)\b"),
        ("local_news", r"^(local news by authority|local news)\b"),
        ("international_news", r"^(international news|international)\b"),
        ("national_news", r"^(national news|national)\b"),
        ("ideas", r"^(ideas|ideas and projects)\b"),
    ]

    SEPARATORS_PATTERN = re.compile(r"\s*(?:[\u2013\u2014\-:]|&ndash;|&mdash;)\s*")

    def __init__(self, resolver=None):
        self.resolver = resolver

    def parse_post(self, source_id: int, post_date: str, post_html: str) -> Tuple[Dict[str, str], List[Dict[str, Any]], List[str]]:
        """
        Parses post HTML.
        Returns:
            editorial_dict: {"text": "...", "html": "..."}
            stories: list of story dicts
            sections_found: list of section names found
        """
        blocks = self._split_into_blocks(post_html)
        current_section = "editorial"
        sections_found = set(["editorial"])
        stories_by_section: Dict[str, List[Dict[str, Any]]] = {
            "editorial": [],
            "changes": [],
            "local_news": [],
            "international_news": [],
            "national_news": [],
            "ideas": [],
            "other": []
        }

        editorial_html_parts = []

        for block in blocks:
            # Check if this block is a section heading
            detected_section = self._detect_section_heading(block)
            if detected_section:
                current_section = detected_section
                sections_found.add(current_section)
                continue

            if current_section == "editorial":
                text, links = extract_text_and_links(block)
                if text:
                    editorial_html_parts.append(block)
                continue

            # Parse story item
            parsed_item = self._parse_story_block(block, current_section)
            if parsed_item:
                stories_by_section[current_section].append(parsed_item)

        # Assemble editorial
        full_editorial_html = "\n".join(editorial_html_parts)
        editorial_text, _ = extract_text_and_links(full_editorial_html)

        # Assemble and number stories
        all_stories = []
        section_code_map = {
            "changes": "changes",
            "local_news": "local",
            "international_news": "intl",
            "national_news": "natl",
            "ideas": "ideas",
            "other": "other"
        }

        for sec_name, items in stories_by_section.items():
            if sec_name == "editorial":
                continue
            code = section_code_map.get(sec_name, "story")
            for idx, item in enumerate(items, 1):
                story_id = f"pln-story-{source_id}-{code}-{idx:03d}"
                entity_raw = item["entity_raw"]
                text = item["text"]
                text_html = item["text_html"]
                links = item["links"]

                # Resolve entity and classification if resolver is provided
                resolution_dict = {"entity_type": "general", "libraries_mentioned": []}
                classification_dict = {
                    "categories": [],
                    "primary_category": None,
                    "change_type": None,
                    "sector_bodies_mentioned": [],
                    "financial_mentions": []
                }
                tags = []
                if self.resolver:
                    res, cls_obj, tags = self.resolver.resolve(entity_raw, text, sec_name)
                    # Convert resolution to dict
                    resolution_dict = {
                        "entity_type": res.entity_type,
                        "country": res.country,
                        "country_code": res.country_code,
                        "library_service": {
                            "name": res.library_service.name,
                            "gss_code": res.library_service.gss_code,
                            "confidence": res.library_service.confidence
                        } if res.library_service else None,
                        "libraries_mentioned": [
                            {
                                "id": lib.id,
                                "name": lib.name,
                                "postcode": lib.postcode,
                                "lat": lib.lat,
                                "lng": lib.lng,
                                "status": lib.status,
                                "slug": lib.slug
                            } for lib in res.libraries_mentioned
                        ],
                        "coordinates": {
                            "latitude": res.coordinates.latitude,
                            "longitude": res.coordinates.longitude
                        } if res.coordinates else None
                    }
                    classification_dict = {
                        "categories": cls_obj.categories,
                        "primary_category": cls_obj.primary_category,
                        "change_type": cls_obj.change_type,
                        "sector_bodies_mentioned": cls_obj.sector_bodies_mentioned,
                        "financial_mentions": cls_obj.financial_mentions
                    }

                all_stories.append({
                    "id": story_id,
                    "post_id": f"pln-post-{source_id}",
                    "post_date": post_date[:10] if len(post_date) >= 10 else post_date,
                    "section": sec_name,
                    "entity_raw": entity_raw,
                    "text": text,
                    "text_html": text_html,
                    "links": links,
                    "resolution": resolution_dict,
                    "classification": classification_dict,
                    "tags": tags
                })

        editorial_dict = {
            "text": editorial_text,
            "html": clean_html_fragment(full_editorial_html)
        }

        return editorial_dict, all_stories, sorted(list(sections_found))

    def _split_into_blocks(self, html: str) -> List[str]:
        """Split HTML into logical block units (paragraphs, list items, headings)."""
        # Split on block-level HTML tags
        parts = re.split(r"(<(?:p|h[1-6]|li)[^>]*>.*?</(?:p|h[1-6]|li)>)", html, flags=re.DOTALL | re.IGNORECASE)
        blocks = []
        for p in parts:
            p = p.strip()
            if p and not re.match(r"^<(?:ul|ol|div)[^>]*>$", p, flags=re.IGNORECASE):
                blocks.append(p)
        return blocks

    def _detect_section_heading(self, block: str) -> Optional[str]:
        """Check if a block is a section heading."""
        text, _ = extract_text_and_links(block)
        clean = text.lower().strip()
        # Strip numbering or punctuation
        clean = re.sub(r"^[0-9\.\-\s]+", "", clean).strip()

        for section_key, pattern in self.SECTION_PATTERNS:
            if re.match(pattern, clean, flags=re.IGNORECASE):
                return section_key

        return None

    def _parse_story_block(self, block: str, section: str) -> Optional[Dict[str, Any]]:
        """
        Extract entity prefix, story body, and links from a block.
        Format typically: <p><strong>Entity Name</strong> – Story text... <a href="..."></a></p>
        """
        # 1. Look for bold tag prefix: <strong>...</strong> or <b>...</b>
        match_bold = re.search(r"<(?:strong|b)>([^<]+)</(?:strong|b)>\s*(?:[\u2013\u2014\-:]|&ndash;|&mdash;)?\s*(.*)", block, flags=re.DOTALL | re.IGNORECASE)

        if match_bold:
            entity_raw = unescape(match_bold.group(1)).strip()
            # Clean entity of any leading/trailing punctuation or separators
            entity_raw = re.sub(r"^(?:[\s\u2013\u2014\-:]|&ndash;|&mdash;|&#8211;|&#8212;)+", "", entity_raw).strip()
            entity_raw = re.sub(r"(?:[\s\u2013\u2014\-:]|&ndash;|&mdash;|&#8211;|&#8212;)+$", "", entity_raw).strip()
            body_html = match_bold.group(2).strip()

            # Sometimes the separator is inside or outside the bold tag
            body_html = re.sub(r"^(?:[\s\u2013\u2014\-:]|&ndash;|&mdash;|&#8211;|&#8212;)+", "", body_html).strip()
            text, links = extract_text_and_links(body_html)
            text = re.sub(r"^[\s\u2013\u2014\-:]+", "", text).strip()
            body_html = re.sub(r"^(?:[\s\u2013\u2014\-:]|&ndash;|&mdash;|&#8211;|&#8212;)+", "", body_html).strip()

            if len(entity_raw) > 0 and len(text) > 10:
                # If entity_raw is 1-2 chars and not US/UK, it's a drop cap or stray punctuation
                if len(entity_raw) <= 2 and entity_raw.upper() not in ["US", "UK"]:
                    full_text, links = extract_text_and_links(block)
                    clean_full = re.sub(r"^[\s\u2013\u2014\-:]+", "", full_text).strip()
                    parts = self.SEPARATORS_PATTERN.split(clean_full, maxsplit=1)
                    if len(parts) == 2 and len(parts[0].strip()) <= 40 and len(parts[1].strip()) > 10:
                        return {
                            "entity_raw": parts[0].strip(),
                            "text": re.sub(r"^[\s\u2013\u2014\-:]+", "", parts[1].strip()).strip(),
                            "text_html": clean_html_fragment(block),
                            "links": links
                        }
                    else:
                        return {
                            "entity_raw": clean_full[:30].strip(),
                            "text": clean_full,
                            "text_html": clean_html_fragment(block),
                            "links": links
                        }

                return {
                    "entity_raw": entity_raw,
                    "text": text,
                    "text_html": clean_html_fragment(body_html),
                    "links": links
                }

        # 2. Fallback: split on separator if no strong/b tag, but contains dash
        text, links = extract_text_and_links(block)
        parts = self.SEPARATORS_PATTERN.split(text, maxsplit=1)
        if len(parts) == 2 and len(parts[0].strip()) <= 40 and len(parts[1].strip()) > 10:
            entity_raw = parts[0].strip()
            story_text = re.sub(r"^[\s\u2013\u2014\-:]+", "", parts[1].strip()).strip()
            return {
                "entity_raw": entity_raw,
                "text": story_text,
                "text_html": clean_html_fragment(block),
                "links": links
            }

        return None
