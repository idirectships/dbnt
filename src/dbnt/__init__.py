"""DBNT - Do Better Next Time

Universal learning protocol for AI systems.
Not anger-driven. Signal-driven.
"""

from dbnt.core import (
    encode_failure,
    encode_success,
    check_dissonance,
    get_rules,
)
from dbnt.signals.detector import detect_signal, SignalType, SignalStrength

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
