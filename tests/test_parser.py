"""
Unit tests for PLNPostParser.

Validates HTML section segmentation, story entity extraction, hyperlink harvesting,
and integration with EntityResolver.
"""

import unittest
from src.parser import PLNPostParser
from src.resolver import EntityResolver

SAMPLE_POST_HTML = """
<p><strong>Editorial</strong></p>
<p>Welcome to this week's news summary. We have seen widespread discussions on the statutory superintendence role of the DCMS.</p>

<p><strong>Changes</strong></p>
<ul>
  <li><strong>Barnsley</strong> – Proposals have been published to adjust opening times (<a href="https://example.com/barnsley">Council Notice</a>).</li>
  <li><strong>Cheshire East</strong> — Transfer of community facilities is underway.</li>
</ul>

<p><strong>Local news by authority</strong></p>
<p><strong>Birmingham</strong> – Public consultation continues over library provision (<a href="https://example.com/bham">Birmingham Mail</a>).</p>
<p><strong>Brighton and Hove</strong> - City library services celebrate national reading month.</p>

<p><strong>International news</strong></p>
<p><strong>USA</strong> – American libraries celebrate Banned Books Week (<a href="https://ala.org">ALA</a>).</p>
<p><strong>Canada</strong> – Toronto public library launches summer technology hubs.</p>
"""

class TestPostParser(unittest.TestCase):
    """Test suite verifying HTML parsing, section splitting, and story item generation."""

    def setUp(self):
        """Initialize parser instance backed by the default entity resolver."""
        resolver = EntityResolver()
        self.parser = PLNPostParser(resolver=resolver)

    def test_parse_post(self):
        """Verify that posts are correctly split into editorial commentary and discrete stories."""
        editorial, stories, sections = self.parser.parse_post(
            source_id=99999,
            post_date="2024-10-20T18:00:00Z",
            post_html=SAMPLE_POST_HTML
        )

        # Check Editorial
        self.assertIn("Welcome to this week's news summary", editorial["text"])
        self.assertIn("statutory superintendence", editorial["text"])

        # Check Sections found
        self.assertIn("editorial", sections)
        self.assertIn("changes", sections)
        self.assertIn("local_news", sections)
        self.assertIn("international_news", sections)

        # Check Stories Count
        self.assertEqual(len(stories), 6)

        # Check a specific story in Changes
        barnsley_story = next(s for s in stories if s["entity_raw"] == "Barnsley")
        self.assertEqual(barnsley_story["section"], "changes")
        self.assertEqual(barnsley_story["id"], "pln-story-99999-changes-001")
        self.assertEqual(len(barnsley_story["links"]), 1)
        self.assertEqual(barnsley_story["links"][0]["url"], "https://example.com/barnsley")
        self.assertEqual(barnsley_story["links"][0]["domain"], "example.com")
        self.assertEqual(barnsley_story["resolution"]["library_service"]["name"], "Barnsley")
        self.assertEqual(barnsley_story["resolution"]["library_service"]["gss_code"], "E08000016")
        self.assertIn("opening_hours", barnsley_story["classification"]["categories"])

        # Check International News
        usa_story = next(s for s in stories if s["entity_raw"] == "USA")
        self.assertEqual(usa_story["section"], "international_news")
        self.assertEqual(usa_story["resolution"]["entity_type"], "country")
        self.assertEqual(usa_story["resolution"]["country"], "United States")
        self.assertEqual(usa_story["resolution"]["country_code"], "US")
        self.assertEqual(usa_story["links"][0]["url"], "https://ala.org")

if __name__ == "__main__":
    unittest.main()
