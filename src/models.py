"""
Data models for PLN Posts and Stories.

Defines typed dataclasses representing weekly posts, extracted stories,
entity resolutions, sector taxonomy classifications, and licensing metadata.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

@dataclass
class Attribution:
    """Legal attribution and licensing metadata preserving Ian Anstice / The Library Campaign credits."""
    source: str = "Public Libraries News"
    source_url: str = "https://www.publiclibrariesnews.com/"
    license: str = "CC BY 4.0"
    license_url: str = "https://creativecommons.org/licenses/by/4.0/"
    notes: str = "Content copyright Ian Anstice / The Library Campaign, licensed under Creative Commons Attribution."

@dataclass
class EditorialContent:
    """Weekly editorial introduction stored in both plain text and original HTML."""
    text: str
    html: str

@dataclass
class LinkItem:
    """Hyperlink extracted from story text with target URL, anchor text, and source domain."""
    url: str
    text: str
    domain: Optional[str] = None

@dataclass
class LibraryServiceRef:
    """Reference to a matched UK library authority with official GSS code and match confidence."""
    name: str
    gss_code: Optional[str] = None
    confidence: str = "exact"  # exact, alias, fuzzy, unmatched

@dataclass
class LibraryMention:
    """Specific public library building matched from LibraryCommons datasets."""
    id: str
    name: str
    postcode: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    status: Optional[str] = "Open"
    slug: Optional[str] = None

@dataclass
class Coordinates:
    """Geographic centroid or point coordinates (WGS84 latitude and longitude)."""
    latitude: float
    longitude: float

@dataclass
class EntityResolution:
    """Resolved geographic entity, country, library authority, and matched physical branches."""
    entity_type: str  # local_authority, country, national, general
    country: Optional[str] = None
    country_code: Optional[str] = None
    library_service: Optional[LibraryServiceRef] = None
    libraries_mentioned: List[LibraryMention] = field(default_factory=list)
    coordinates: Optional[Coordinates] = None

@dataclass
class StoryClassification:
    """Thematic taxonomy tags, change classifications, sector bodies, and financial amounts."""
    categories: List[str] = field(default_factory=list)
    primary_category: Optional[str] = None
    change_type: Optional[str] = None
    sector_bodies_mentioned: List[str] = field(default_factory=list)
    financial_mentions: List[str] = field(default_factory=list)

@dataclass
class StoryItem:
    """Discrete news item extracted from a post section with text, links, and resolution."""
    id: str
    post_id: str
    post_date: str
    section: str
    entity_raw: str
    text: str
    text_html: str
    links: List[LinkItem] = field(default_factory=list)
    resolution: EntityResolution = field(default_factory=lambda: EntityResolution(entity_type="general"))
    classification: StoryClassification = field(default_factory=StoryClassification)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize story instance to a standard dictionary representation."""
        return asdict(self)

@dataclass
class PostStats:
    """Aggregated statistics for a weekly post including distinct places and top categories."""
    authorities_count: int = 0
    libraries_count: int = 0
    countries_count: int = 0
    top_categories: Dict[str, int] = field(default_factory=dict)

@dataclass
class Post:
    """Complete weekly post record with editorial content, metadata, and story IDs."""
    id: str
    source_id: int
    url: str
    slug: str
    title: str
    date_published: str
    date_modified: str
    author: str
    editorial: EditorialContent
    sections_found: List[str]
    stories_count: int
    story_ids: List[str]
    stats: PostStats = field(default_factory=PostStats)
    attribution: Attribution = field(default_factory=Attribution)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize post instance to a standard dictionary representation."""
        return asdict(self)
