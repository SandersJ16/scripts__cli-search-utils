#!/usr/bin/env python

import pytest
#from .context import utils
import utils

@pytest.mark.parametrize(["indicies", "expected_indicies"], [
    ([], []),                                                        # No indexes
    ([(0, 1)], [(0, 1)]),                                            # Single index
    ([(0, 1), (2, 3)], [(0, 1), (2, 3)]),                            # Multiple non-overlapping indexes
    ([(0, 3), (1, 4)], [(0, 4)]),                                    # Two overlapping indexes
    ([(0, 3), (3, 4)], [(0, 4)]),                                    # Two adjacent indexes
    ([(2, 5), (1, 9)], [(1, 9)]),                                    # Index Nested in another
    ([(1, 4), (2, 5), (8, 10), (7, 12), (0, 3)], [(0, 5), (7, 12)])  # Multiple overlapping, nested indexes
])
def test_simplify_indexes(indicies, expected_indicies):
    assert utils.simplify_indexes(indicies) == expected_indicies


HIGHLIGHT_STARTER = "\033[%s" % utils.HIGHTLIGHT_COLOR
HIGHLIGHT_ENDER = "\033[%s" % utils.STOP_COLOR
@pytest.mark.parametrize(["text", "indexes", "highlighted_text"], [
    ("This is a test", [], "This is a test"),
    ("This is a test", [(0, 14)], f"{HIGHLIGHT_STARTER}This is a test{HIGHLIGHT_ENDER}"),
    ("This is a test", [(5, 7)], f"This {HIGHLIGHT_STARTER}is{HIGHLIGHT_ENDER} a test"),
    ("This is a test", [(0, 4), (10, 14)], f"{HIGHLIGHT_STARTER}This{HIGHLIGHT_ENDER} is a {HIGHLIGHT_STARTER}test{HIGHLIGHT_ENDER}")
])
def test_highlight(text, indexes, highlighted_text):
    assert utils.highlight(text, indexes) == highlighted_text


if __name__ == "__main__":
    exit(pytest.main())
