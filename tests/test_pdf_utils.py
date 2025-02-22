import pytest
from pdf_highlighter.core.pdf_utils import rgb_to_hex, HighlightState

def test_rgb_to_hex():
    assert rgb_to_hex((1, 0, 0)) == "#ff0000"  # Red
    assert rgb_to_hex((0, 1, 0)) == "#00ff00"  # Green
    assert rgb_to_hex((0, 0, 1)) == "#0000ff"  # Blue
    assert rgb_to_hex(None) == "none"

    with pytest.raises(ValueError):
        rgb_to_hex((2, 0, 0))  # Invalid RGB values

def test_highlight_state():
    assert HighlightState.ADDED.value == "added"
    assert HighlightState.REMOVED.value == "removed"
    assert HighlightState.NO_COLOR.value == "no_color"
    assert HighlightState.ERROR.value == "error"