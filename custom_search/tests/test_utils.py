#!/usr/bin/env python

import pytest
#from .context import utils
import utils

simplify_indexes_testcases = {
    "No indexes": ([], []),
    "Single index": ([(0, 1)], [(0, 1)]),
    "Multiple non-overlapping indexes": ([(0, 1), (2, 3)], [(0, 1), (2, 3)]),
    "Two overlapping indexes": ([(0, 3), (1, 4)], [(0, 4)]),
    "Two adjacent indexes": ([(0, 3), (3, 4)], [(0, 4)]),
    "Index nested in another": ([(2, 5), (1, 9)], [(1, 9)]),
    "Multiple overlapping, nested indexes": ([(1, 4), (2, 5), (8, 10), (7, 12), (0, 3)], [(0, 5), (7, 12)])
}
@pytest.mark.parametrize(["indicies", "expected_indicies"], simplify_indexes_testcases.values(), ids=simplify_indexes_testcases.keys())
def test_simplify_indexes(indicies, expected_indicies):
    assert utils.simplify_indexes(indicies) == expected_indicies


HIGHLIGHT_STARTER = "\033[%s" % utils.HIGHTLIGHT_COLOR
HIGHLIGHT_ENDER = "\033[%s" % utils.STOP_COLOR
highlight_test_cases = {
    "No highlighting": ("This is a test", [], "This is a test"),
    "All h0ighlighted": ("This is a test", [(0, 14)], f"{HIGHLIGHT_STARTER}This is a test{HIGHLIGHT_ENDER}"),
    "Partially highlighted": ("This is a test", [(5, 7)], f"This {HIGHLIGHT_STARTER}is{HIGHLIGHT_ENDER} a test"),
    "Multiple highlights": ("This is a test", [(0, 4), (10, 14)], f"{HIGHLIGHT_STARTER}This{HIGHLIGHT_ENDER} is a {HIGHLIGHT_STARTER}test{HIGHLIGHT_ENDER}")
}
@pytest.mark.parametrize(["text", "indexes", "highlighted_text"], highlight_test_cases.values(), ids=highlight_test_cases.keys())
def test_highlight(text, indexes, highlighted_text):
    assert utils.highlight(text, indexes) == highlighted_text


if __name__ == "__main__":
    exit(pytest.main())
