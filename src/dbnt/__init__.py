"""DBNT - Do Better Next Time

Universal learning protocol for AI systems.
Not anger-driven. Signal-driven.
"""

from dbnt.core import (
    check_dissonance,
    encode_failure,
    encode_success,
    get_rules,
)
from dbnt.signals.detector import SignalStrength, SignalType, detect_signal

__version__ = "0.1.0"
__all__ = [
    "encode_success",
    "encode_failure",
    "check_dissonance",
    "get_rules",
    "detect_signal",
    "SignalType",
    "SignalStrength",
]
