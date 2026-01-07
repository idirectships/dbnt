"""Tests for signal detection."""

from dbnt.signals.detector import SignalStrength, SignalType, detect_signal


class TestPositiveSignals:
    """Test positive signal detection."""

    def test_strong_perfect(self):
        signal = detect_signal("that's perfect")
        assert signal.type == SignalType.POSITIVE
        assert signal.strength == SignalStrength.STRONG
        assert signal.weight == 1.5

    def test_strong_ship_it(self):
        signal = detect_signal("ship it!")
        assert signal.type == SignalType.POSITIVE
        assert signal.strength == SignalStrength.STRONG

    def test_strong_exactly_right(self):
        signal = detect_signal("exactly what I needed")
        assert signal.type == SignalType.POSITIVE
        assert signal.strength == SignalStrength.STRONG

    def test_moderate_great(self):
        signal = detect_signal("great, thanks!")
        assert signal.type == SignalType.POSITIVE
        assert signal.strength == SignalStrength.MODERATE
        assert signal.weight == 1.2

    def test_moderate_that_works(self):
        signal = detect_signal("that works")
        assert signal.type == SignalType.POSITIVE
        assert signal.strength == SignalStrength.MODERATE


class TestNegativeSignals:
    """Test negative signal detection - no anger required."""

    def test_strong_wrong(self):
        signal = detect_signal("that's wrong")
        assert signal.type == SignalType.NEGATIVE
        assert signal.strength == SignalStrength.STRONG
        assert signal.weight == 1.0

    def test_strong_fix_this(self):
        signal = detect_signal("fix this please")
        assert signal.type == SignalType.NEGATIVE
        assert signal.strength == SignalStrength.STRONG

    def test_moderate_not_quite(self):
        signal = detect_signal("not quite what I meant")
        assert signal.type == SignalType.NEGATIVE
        assert signal.strength == SignalStrength.MODERATE
        assert signal.weight == 0.8

    def test_moderate_hmm(self):
        signal = detect_signal("hmm, try again")
        assert signal.type == SignalType.NEGATIVE
        assert signal.strength == SignalStrength.MODERATE

    def test_mild_feedback_detected(self):
        """No yelling required - mild feedback works."""
        signal = detect_signal("that's not quite right")
        assert signal.type == SignalType.NEGATIVE


class TestNeutralSignals:
    """Test neutral signal detection."""

    def test_ok(self):
        signal = detect_signal("ok")
        assert signal.type == SignalType.NEUTRAL
        assert signal.strength == SignalStrength.WEAK
        assert signal.weight == 0.0

    def test_sure(self):
        signal = detect_signal("sure")
        assert signal.type == SignalType.NEUTRAL

    def test_no_match(self):
        signal = detect_signal("let me explain the situation")
        assert signal.type == SignalType.NEUTRAL
        assert not signal.should_encode()


class TestShouldEncode:
    """Test encoding decisions."""

    def test_strong_positive_encodes(self):
        signal = detect_signal("perfect!")
        assert signal.should_encode()

    def test_moderate_negative_encodes(self):
        signal = detect_signal("not quite")
        assert signal.should_encode()

    def test_neutral_does_not_encode(self):
        signal = detect_signal("ok")
        assert not signal.should_encode()

    def test_random_text_does_not_encode(self):
        signal = detect_signal("here is some code")
        assert not signal.should_encode()
