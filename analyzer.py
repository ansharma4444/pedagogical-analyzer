"""
analyzer.py
Core analysis logic for the Pedagogical Alignment Dashboard.

This module is intentionally decoupled from Streamlit so it can be unit
tested and reused (e.g. in a CLI script or a future API) without needing
a running web app.
"""

import re
from typing import Dict

import textstat

# Bloom's Taxonomy verb bank, ordered from lowest to highest cognitive demand.
# Order matters for tie-breaking: if a passage matches verbs from more than
# one level an equal number of times, we lean towards the higher-order level,
# since Bloom's levels are cumulative and higher-order verbs are rarer,
# more deliberate choices by a content author.
BLOOMS_TAXONOMY = {
    "Remembering":   ["list", "memorize", "state", "define", "repeat", "name", "recall"],
    "Understanding": ["describe", "explain", "identify", "locate", "report", "summarize", "discuss"],
    "Applying":      ["calculate", "solve", "illustrate", "use", "demonstrate", "apply", "implement"],
    "Analyzing":     ["compare", "contrast", "examine", "question", "test", "differentiate", "analyze"],
    "Evaluating":    ["judge", "select", "critique", "justify", "recommend", "assess", "argue"],
    "Creating":      ["design", "construct", "develop", "formulate", "investigate", "create", "compose"],
}

LEVEL_ORDER = list(BLOOMS_TAXONOMY.keys())  # low -> high cognitive demand


def get_cognitive_level(text: str) -> Dict[str, object]:
    """
    Score a passage against Bloom's Taxonomy verb lists.

    The original prototype returned the FIRST keyword match found, which is
    unstable: it depends on dict iteration order and a single stray word can
    misclassify an entire passage. This version instead counts ALL verb hits
    per level (using word-boundary regex so "test" doesn't match "testing"
    incorrectly, etc.), then reports the level with the most hits. Ties are
    broken in favor of the higher cognitive level.

    Returns:
        {
          "level": winning Bloom's level (str), or "Unclassified" if no
                   taxonomy verbs were found at all,
          "scores": raw hit counts per level, for transparency/debugging
        }
    """
    text_lower = text.lower()
    scores = {}
    for level, verbs in BLOOMS_TAXONOMY.items():
        count = 0
        for verb in verbs:
            count += len(re.findall(rf"\b{re.escape(verb)}\w*\b", text_lower))
        scores[level] = count

    max_score = max(scores.values())
    if max_score == 0:
        return {"level": "Unclassified", "scores": scores}

    best_level = max(
        (level for level, score in scores.items() if score == max_score),
        key=lambda lvl: LEVEL_ORDER.index(lvl),
    )
    return {"level": best_level, "scores": scores}


def get_reading_grade(text: str, cap: float = 12.0) -> float:
    """
    Compute the Flesch-Kincaid grade level of a passage, floored at 0 and
    capped at `cap` so a very short or very dense passage doesn't distort
    the dashboard's 1-12 grade scale.
    """
    raw_grade = textstat.flesch_kincaid_grade(text)
    return round(max(0.0, min(cap, raw_grade)), 1)


def get_alignment_score(target_grade: float, reading_grade: float) -> float:
    """
    Score how well a text's actual reading grade matches its intended
    audience's target grade. 100 = perfect match; score drops 10 points
    per grade level of mismatch, floored at 0.
    """
    return round(max(0.0, 100 - abs(target_grade - reading_grade) * 10), 1)


def analyze_text(app_name: str, target_grade: int, text: str) -> Dict[str, object]:
    """
    Run the full analysis pipeline on one piece of lesson content and
    return a single flat result record.
    """
    reading_grade = get_reading_grade(text)
    cognitive = get_cognitive_level(text)
    alignment_score = get_alignment_score(target_grade, reading_grade)

    return {
        "App Name": app_name,
        "Target Grade": target_grade,
        "Reading Grade": reading_grade,
        "Cognitive Level": cognitive["level"],
        "Cognitive Scores": cognitive["scores"],
        "Alignment Score": alignment_score,
    }
