"""
Unit tests for EntityResolver (UK Local Authorities, Countries, Libraries).
"""

import unittest
from src.resolver import EntityResolver

class TestEntityResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = EntityResolver()

    def test_uk_authority_exact(self):
        res, tags = self.resolver.resolve("Barnsley", "The council is proposing new services.", "local_news")
        self.assertEqual(res.entity_type, "local_authority")
        self.assertEqual(res.country, "England")
        self.assertEqual(res.country_code, "GB")
        self.assertIsNotNone(res.library_service)
        self.assertEqual(res.library_service.name, "Barnsley")
        self.assertEqual(res.library_service.gss_code, "E08000016")

    def test_uk_authority_alias(self):
        res, _ = self.resolver.resolve("Cheshire West", "News from Chester libraries.", "changes")
        self.assertEqual(res.entity_type, "local_authority")
        self.assertEqual(res.library_service.name, "Cheshire West and Chester")

        res_rct, _ = self.resolver.resolve("RCT", "Welsh council updates.", "local_news")
        self.assertEqual(res_rct.country, "Wales")
        self.assertEqual(res_rct.library_service.name, "Rhondda Cynon Taf")

    def test_scotland_and_ni(self):
        res_scot, _ = self.resolver.resolve("Aberdeen", "Aberdeen central library news.", "local_news")
        self.assertEqual(res_scot.country, "Scotland")

        res_ni, _ = self.resolver.resolve("Libraries NI", "Northern Ireland network news.", "local_news")
        self.assertEqual(res_ni.country, "Northern Ireland")

    def test_country_matching(self):
        res_us, _ = self.resolver.resolve("USA", "American Library Association reports challenge.", "international_news")
        self.assertEqual(res_us.entity_type, "country")
        self.assertEqual(res_us.country, "United States")
        self.assertEqual(res_us.country_code, "US")

        res_ca, _ = self.resolver.resolve("Canada", "Toronto library system extends weekend hours.", "international_news")
        self.assertEqual(res_ca.country, "Canada")
        self.assertEqual(res_ca.country_code, "CA")

    def test_library_branch_matching(self):
        text = "Staff and campaigners gathered outside Harborne Library to protest against proposed reductions in hours."
        res, tags = self.resolver.resolve("Birmingham", text, "local_news")
        self.assertEqual(res.entity_type, "local_authority")
        self.assertEqual(res.library_service.name, "Birmingham")
        # Harborne Library should be matched from the libraries lookup
        matched_names = [lib.name for lib in res.libraries_mentioned]
        self.assertTrue(any("Harborne" in name for name in matched_names))
        # Tags should detect campaign and hours
        self.assertIn("campaign", tags)
        self.assertIn("opening_hours", tags)

    def test_tag_extraction(self):
        text = "Proposals have been published for library closures and major budget cuts following consultation."
        _, tags = self.resolver.resolve("Unknown Council", text, "changes")
        self.assertIn("closures", tags)
        self.assertIn("cuts", tags)
        self.assertIn("consultation", tags)

if __name__ == "__main__":
    unittest.main()
