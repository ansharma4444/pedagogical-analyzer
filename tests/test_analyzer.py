"""
Unit tests for analyzer.py

Run with:  pytest
(from the project root, with dependencies from requirements.txt and
requirements-dev.txt installed)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analyzer import get_cognitive_level, get_reading_grade, get_alignment_score, analyze_text


def test_cognitive_level_single_verb():
    result = get_cognitive_level("Please list the five main food groups.")
    assert result["level"] == "Remembering"


def test_cognitive_level_prefers_higher_order_on_tie():
    # "list" (Remembering) and "design" (Creating) each appear once.
    # Bloom's Taxonomy is cumulative, so the tie-break should favor Creating.
    text = "List the parts, then design a new model using them."
    result = get_cognitive_level(text)
    assert result["level"] == "Creating"


def test_cognitive_level_counts_not_first_match():
    # Two "Analyzing" verbs vs. one "Remembering" verb -> Analyzing should win,
    # which the old first-match implementation would have gotten wrong.
    text = "List the items. Compare and contrast them, then examine the results."
    result = get_cognitive_level(text)
    assert result["level"] == "Analyzing"


def test_cognitive_level_no_match_is_unclassified():
    result = get_cognitive_level("The sky is blue today.")
    assert result["level"] == "Unclassified"


def test_reading_grade_is_capped():
    dense_text = " ".join(
        ["Notwithstanding the aforementioned multifaceted epistemological considerations"] * 5
    )
    grade = get_reading_grade(dense_text, cap=12.0)
    assert grade <= 12.0


def test_reading_grade_simple_text_is_low():
    grade = get_reading_grade("The cat sat on the mat. The cat is fat.")
    assert grade < 4.0


def test_alignment_score_perfect_match():
    assert get_alignment_score(target_grade=5, reading_grade=5) == 100.0


def test_alignment_score_penalizes_mismatch():
    score = get_alignment_score(target_grade=3, reading_grade=8)
    assert score == 50.0  # 100 - (5 grades off * 10)


def test_alignment_score_floors_at_zero():
    score = get_alignment_score(target_grade=1, reading_grade=12)
    assert score == 0.0


def test_analyze_text_full_pipeline():
    record = analyze_text("Sample App", target_grade=5, text="List and describe the water cycle.")
    assert record["App Name"] == "Sample App"
    assert record["Target Grade"] == 5
    assert "Reading Grade" in record
    assert "Cognitive Level" in record
    assert "Alignment Score" in record
