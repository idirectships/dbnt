"""Signal detection - recognize positive/negative feedback without requiring anger."""

import re
from dataclasses import dataclass
from enum import Enum


class SignalType(Enum):
    """Type of signal detected."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SignalStrength(Enum):
    """Strength of detected signal."""

    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


@dataclass
class Signal:
    """Detected signal from user input."""

    type: SignalType
    strength: SignalStrength
    match: str | None = None
    weight: float = 1.0

    def should_encode(self) -> bool:
        """Whether this signal should create a rule."""
        if self.type == SignalType.NEUTRAL:
            return False
        return self.strength in (SignalStrength.STRONG, SignalStrength.MODERATE)


# Signal patterns - no yelling required
POSITIVE_STRONG = [
    r"\bperfect\b",
    r"\bexactly\s+(what\s+i\s+)?(needed|wanted|right)\b",
    r"\bship\s*it\b",
    r"\bnailed\s*it\b",
    r"\bthat'?s?\s*it\b",
    r"\blove\s*it\b",
]

POSITIVE_MODERATE = [
    r"\bgreat\b",
    r"\bnice\b",
    r"\bgood\s*(job|work)?\b",
    r"\bthanks?\b.*\b(works?|working)\b",
    r"\byes!?\b",
    r"\bawesome\b",
    r"\bthat\s*works\b",
]

NEGATIVE_STRONG = [
    r"\bwrong\b",
    r"\bno[,.]?\s*(that'?s?\s*)?(not|wrong)\b",
    r"\bfix\s*(this|it|that)\b",
    r"\bbroken\b",
    r"\bfailed?\b",
    r"\bdoesn'?t\s*work\b",
]

NEGATIVE_MODERATE = [
    r"\bhmm+\b",
    r"\bnot\s*quite\b",
    r"\btry\s*again\b",
    r"\bnot\s*(what|right)\b",
    r"\bclose\s*but\b",
    r"\balmost\b",
]

NEUTRAL = [
    r"^ok$",
    r"^sure$",
    r"^fine$",
    r"^k$",
]


def _match_patterns(text: str, patterns: list[str]) -> str | None:
    """Check if text matches any pattern, return the match."""
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def detect_signal(text: str) -> Signal:
    """
    Detect signal type and strength from user input.

    No anger required - works with mild feedback:
    - "that's not quite right" → NEGATIVE (moderate)
    - "perfect" → POSITIVE (strong)
    - "ok" → NEUTRAL (weak)

    Args:
        text: User input text

    Returns:
        Signal with type, strength, and encoding weight
    """
    # Check positive strong (1.5x weight)
    match = _match_patterns(text, POSITIVE_STRONG)
    if match:
        return Signal(
            type=SignalType.POSITIVE,
            strength=SignalStrength.STRONG,
            match=match,
            weight=1.5,
        )

    # Check positive moderate (1.2x weight)
    match = _match_patterns(text, POSITIVE_MODERATE)
    if match:
        return Signal(
            type=SignalType.POSITIVE,
            strength=SignalStrength.MODERATE,
            match=match,
            weight=1.2,
        )

    # Check negative strong (1.0x weight)
    match = _match_patterns(text, NEGATIVE_STRONG)
    if match:
        return Signal(
            type=SignalType.NEGATIVE,
            strength=SignalStrength.STRONG,
            match=match,
            weight=1.0,
        )

    # Check negative moderate (0.8x weight)
    match = _match_patterns(text, NEGATIVE_MODERATE)
    if match:
        return Signal(
            type=SignalType.NEGATIVE,
            strength=SignalStrength.MODERATE,
            match=match,
            weight=0.8,
        )

    # Check neutral
    match = _match_patterns(text, NEUTRAL)
    if match:
        return Signal(
            type=SignalType.NEUTRAL,
            strength=SignalStrength.WEAK,
            match=match,
            weight=0.0,
        )

    # Default: neutral, no encoding
    return Signal(
        type=SignalType.NEUTRAL,
        strength=SignalStrength.WEAK,
        weight=0.0,
    )
