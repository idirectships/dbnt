"""Tests for DBNT transcript extraction."""

import json

from dbnt.extract import (
    ExtractedLearning,
    LearningType,
    _score_importance,
    extract_from_text,
    extract_from_transcript,
    format_transcript,
)


class TestScoreImportance:
    """Test importance scoring."""

    def test_critical_keywords_boost(self):
        assert _score_importance("critical security bug found") >= 8

    def test_trivial_keywords_reduce(self):
        assert _score_importance("minor trivial change") <= 3

    def test_baseline_score(self):
        assert _score_importance("regular learning about stuff") == 5

    def test_clamped_to_range(self):
        # Even with many keywords, should not exceed 10
        score = _score_importance("critical bug security breaking error failed mistake")
        assert 1 <= score <= 10


class TestExtractFromText:
    """Test regex-based extraction."""

    def test_explicit_learning(self):
        text = "learned: Always use timezone-aware datetimes in Python"
        results = extract_from_text(text)
        assert len(results) == 1
        assert results[0].type == LearningType.APPROACH
        assert "timezone" in results[0].text

    def test_decision_pattern(self):
        text = "We decided to use bun instead of npm for all projects."
        results = extract_from_text(text)
        assert len(results) == 1
        assert results[0].type == LearningType.DECISION
        assert "Decision:" in results[0].text

    def test_correction_pattern(self):
        text = "DBNT - Protocol: Always use feature branches for changes"
        results = extract_from_text(text)
        assert any(item.type == LearningType.CORRECTION for item in results)
        correction = [item for item in results if item.type == LearningType.CORRECTION][0]
        assert correction.importance == 8

    def test_mistake_pattern(self):
        text = "that's wrong, you should use feature branches"
        results = extract_from_text(text)
        assert len(results) >= 1
        assert any(item.type == LearningType.MISTAKE for item in results)

    def test_multiple_extractions(self):
        text = """learned: Always validate inputs at boundaries
decided to use dataclasses for config objects.
DBNT - Security: Use environment variables for API keys"""
        results = extract_from_text(text)
        assert len(results) >= 3  # May get extra from overlapping patterns
        types = {item.type for item in results}
        assert LearningType.APPROACH in types
        assert LearningType.DECISION in types
        assert LearningType.CORRECTION in types

    def test_dedup(self):
        text = """learned: Always use UTC datetimes
learned: Always use UTC datetimes"""
        results = extract_from_text(text)
        assert len(results) == 1

    def test_short_text_filtered(self):
        text = "learned: short"
        results = extract_from_text(text)
        assert len(results) == 0  # Below 15 char minimum

    def test_empty_text(self):
        results = extract_from_text("")
        assert results == []

    def test_no_matches(self):
        text = "Just a regular conversation about the weather."
        results = extract_from_text(text)
        assert results == []

    def test_insight_keyword(self):
        text = "insight: The retry pattern works best with exponential backoff"
        results = extract_from_text(text)
        assert len(results) == 1

    def test_key_takeaway(self):
        text = "key takeaway: Always test edge cases with empty inputs"
        results = extract_from_text(text)
        assert len(results) == 1


class TestFormatTranscript:
    """Test JSONL transcript formatting."""

    def test_basic_messages(self):
        lines = [
            json.dumps({"message": {"role": "user", "content": "Hello"}}),
            json.dumps({"message": {"role": "assistant", "content": "Hi there"}}),
        ]
        result = format_transcript("\n".join(lines))
        assert "user: Hello" in result
        assert "assistant: Hi there" in result

    def test_skips_thinking_blocks(self):
        lines = [
            json.dumps({"message": {"role": "assistant", "content": [
                {"type": "thinking", "text": "internal thought"},
                {"type": "text", "text": "visible response"},
            ]}}),
        ]
        result = format_transcript("\n".join(lines))
        assert "internal thought" not in result
        assert "visible response" in result

    def test_truncates_tool_results(self):
        long_result = "x" * 1000
        lines = [
            json.dumps({"message": {"role": "assistant", "content": [
                {"type": "tool_result", "content": long_result},
            ]}}),
        ]
        result = format_transcript("\n".join(lines))
        assert len(result) < 1000

    def test_respects_max_chars(self):
        lines = [
            json.dumps({"message": {"role": "user", "content": "x" * 500}})
            for _ in range(50)
        ]
        result = format_transcript("\n".join(lines), max_chars=1000)
        assert len(result) <= 1100  # Small buffer for truncation marker

    def test_empty_transcript(self):
        result = format_transcript("")
        assert result == ""

    def test_invalid_json_lines_skipped(self):
        lines = [
            "not json",
            json.dumps({"message": {"role": "user", "content": "valid"}}),
        ]
        result = format_transcript("\n".join(lines))
        assert "valid" in result


class TestExtractFromTranscript:
    """Test end-to-end transcript extraction."""

    def test_end_to_end(self):
        lines = [
            json.dumps({"message": {"role": "user", "content": "learned: Always use bun instead of npm"}}),
            json.dumps({"message": {"role": "assistant", "content": "Noted, using bun."}}),
        ]
        results = extract_from_transcript("\n".join(lines))
        assert len(results) == 1
        assert "bun" in results[0].text


class TestExtractedLearning:
    """Test ExtractedLearning dataclass."""

    def test_to_dict(self):
        learning = ExtractedLearning(
            text="Use UTC datetimes",
            type=LearningType.APPROACH,
            importance=7.0,
            source="transcript",
        )
        d = learning.to_dict()
        assert d["text"] == "Use UTC datetimes"
        assert d["type"] == "approach"
        assert d["importance"] == 7.0
