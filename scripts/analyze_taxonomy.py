"""
Story taxonomy analysis script.

Tests regex pattern coverage across historical story corpora to validate classification
keyword rules for library campaigns, funding, governance, and events.
"""

import json
import glob
import re
from collections import Counter

def analyze():
    """Scan story texts across data partitions to evaluate category keyword frequency.

    Runs regex patterns against combined entity and story text to measure potential
    tagging volume across defined taxonomy buckets.
    """
    words = Counter()
    bigrams = Counter()
    total_stories = 0

    # Specific pattern match counters
    categories = {
        "cuts_and_finance": Counter(),
        "closures_and_threats": Counter(),
        "staffing_and_unions": Counter(),
        "volunteers_and_community": Counter(),
        "opening_hours": Counter(),
        "unstaffed_open_plus": Counter(),
        "refurbishment_and_new_builds": Counter(),
        "campaigns_and_protests": Counter(),
        "book_bans_and_challenges": Counter(),
        "events_and_activities": Counter(),
        "digital_and_technology": Counter(),
        "mobile_and_outreach": Counter(),
        "governance_and_trusts": Counter(),  # mutuals, trusts, returning in-house
        "warm_spaces_and_wellbeing": Counter(),
        "co_location": Counter()
    }

    category_regex = {
        "cuts_and_finance": r"\b(budget|cuts?|savings|saving|deficit|section 114|s114|bankruptcy|funding|capital|grant|investment)\b",
        "closures_and_threats": r"\b(clos(e|ed|ing|ure|ures)|threat(en|ened|s)?|ax(ed|ing)?)\b",
        "staffing_and_unions": r"\b(staff|staffing|unison|strike|strikes|job|jobs|redundanc(y|ies)|librarian|librarians)\b",
        "volunteers_and_community": r"\b(volunteer|volunteers|volunteering|community[- ](run|led)|handover|transferred)\b",
        "opening_hours": r"\b(hours|opening (hours|times)|opening|reduced hours|expanded hours)\b",
        "unstaffed_open_plus": r"\b(unstaffed|staffless|open\+|open plus|openplus|automated access)\b",
        "refurbishment_and_new_builds": r"\b(refurbish(ment|ed)?|renovat(ion|ed)?|reopen(ed|ing)?|new (library|building)|revamp|facelift)\b",
        "campaigns_and_protests": r"\b(campaign(ers?|s)?|protest(ers?|s)?|demonstrat(ion|ors)?|petition|save our library|legal challenge)\b",
        "book_bans_and_challenges": r"\b(book ban(s|ning)?|challenge(d|s)?|censorship|restricted|trans(gender)? books?|pride)\b",
        "events_and_activities": r"\b(activities|event|events|author|workshop|exhibition|reading challenge|summer reading|club)\b",
        "digital_and_technology": r"\b(ai|artificial intelligence|digital|ebooks?|e-books?|computers?|wifi|wi-fi|podcasts?)\b",
        "mobile_and_outreach": r"\b(mobile (library|libraries)|van|mobiles|outreach|home library)\b",
        "governance_and_trusts": r"\b(trust|trusts|charitable trust|in-house|mutual|leisure trust|gll|greenwich leisure|libraries unlimited|aura)\b",
        "warm_spaces_and_wellbeing": r"\b(warm space(s)?|warm bank(s)?|warm welcome|wellbeing|cost of living|food bank)\b",
        "co_location": r"\b(co-locat(ed|ion|ing)?|hub|community hub|shared building|civic centre)\b"
    }

    cat_counts = Counter()

    for f in glob.glob("data/stories/*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            stories = json.load(fp)
            total_stories += len(stories)
            for s in stories:
                text = (s.get("entity_raw", "") + " " + s.get("text", "")).lower()
                for cat, pat in category_regex.items():
                    if re.search(pat, text):
                        cat_counts[cat] += 1

    print(f"Total Stories Analyzed: {total_stories}\n")
    print("=== FREQUENCY OF POTENTIAL CATEGORIES / TOPICS ===")
    for cat, count in cat_counts.most_common():
        pct = (count / total_stories) * 100
        print(f"  {cat:<30}: {count:>4} stories ({pct:.1f}%)")

if __name__ == "__main__":
    analyze()
