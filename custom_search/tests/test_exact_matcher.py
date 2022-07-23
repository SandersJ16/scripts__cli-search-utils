#!/usr/bin/env python

import pytest
from .utilities import assert_matches, assert_indexesOf
from matchers.exact_matcher import ExactMatcher

EXACT_MATCHER = ExactMatcher()
EXACT_MATCHER_CASE_INSENSITIVE = ExactMatcher(case_insensitive=True)

exact_matcher_matches_testcases = {
    "Exact full match":                       ("Test", ["Test"], True),
    "Case-insensitive match":                 ("Test", ["test"], False),
    "non-match":                              ("Test", ["bad"], False),
    "partial match":                          ("Test", ["est"], True),
    "Multiple partial matches":               ("Test", ["Te", "st"], True),
    "Multiple terms, some match some do not": ("Test", ["ba", "st"], False),
    "Multiple overlapping partial matches":   ("Test", ["es", "st"], True)
}
@pytest.mark.parametrize(["name", "terms", "does_match"],
    exact_matcher_matches_testcases.values(),
    ids=exact_matcher_matches_testcases.keys())
def test_exact_matcher_matches(name, terms, does_match):
    assert_matches(EXACT_MATCHER, name, terms, does_match)

exact_matcher_indexesOf_testcases = {
    "Full string match":                ("Test", ["Test"], [(0,4)]),
    "No match":                         ("Test", ["test"], []),
    "Parital match at start of string": ("Test", ["Te"], [(0,2)]),
    "Partial match at end of string":   ("Test", ["st"], [(2,4)]),
    "Multiple matches":                 ("Te Te hat", ["Te"], [(0,2), (3,5)]),
    "Multiple overlapping matches":     ("TeTeTeTe", ["eTe"], [(1,4), (3,6), (5,8)]),
    "mutliple adjacent matches":        ("Batman", ["Bat", "man"], [(0,3), (3,6)]),
    "multiple terms match":             ("TeTeTeTe", ["eTe" , "Te"], [(1,4), (3,6), (5,8), (0,2), (2,4), (4,6), (6,8)])
}
@pytest.mark.parametrize(["name", "terms", "expected_indicies"],
    exact_matcher_indexesOf_testcases.values(),
    ids=exact_matcher_indexesOf_testcases.keys())
def test_exact_matcher_indexesOf(name, terms, expected_indicies):
    assert_indexesOf(EXACT_MATCHER, name, terms, expected_indicies)


exact_matcher_case_insensitive_matches_testcases = {
    "Exact full match":                       ("Test", ["Test"], True),
    "Case-insensitive full match":            ("Test", ["test"], True),
    "non-match":                              ("Test", ["bad"], False),
    "partial match":                          ("TeSt", ["est"], True),
    "Multiple partial matches":               ("test", ["Te", "St"], True),
    "Multiple terms, some match some do not": ("TesT", ["ba", "st"], False),
    "Multiple overlapping partial matches":   ("Test", ["Es", "sT"], True)
}
@pytest.mark.parametrize(["name", "terms", "does_match"],
    exact_matcher_case_insensitive_matches_testcases.values(),
    ids=exact_matcher_case_insensitive_matches_testcases.keys())
def test_exact_matcher_case_insensitive_matches(name, terms, does_match):
    assert_matches(EXACT_MATCHER_CASE_INSENSITIVE, name, terms, does_match)

exact_matcher_case_insensitive_indexesOf_testcases = {
    "Full string match":                ("Test", ["Test"], [(0,4)]),
    "No match":                         ("Test", ["test"], [(0,4)]),
    "Parital match at start of string": ("Test", ["te"], [(0,2)]),
    "Partial match at end of string":   ("TeSt", ["st"], [(2,4)]),
    "Multiple matches":                 ("Te Te hat", ["te"], [(0,2), (3,5)]),
    "Multiple overlapping matches":     ("TeTeTeTe", ["etE"], [(1,4), (3,6), (5,8)]),
    "mutliple adjacent matches":        ("Batman", ["bat", "Man"], [(0,3), (3,6)]),
    "multiple terms match":             ("TeTeTeTe", ["etE" , "te"], [(1,4), (3,6), (5,8), (0,2), (2,4), (4,6), (6,8)])
}
@pytest.mark.parametrize(["name", "terms", "expected_indicies"],
    exact_matcher_case_insensitive_indexesOf_testcases.values(),
    ids=exact_matcher_case_insensitive_indexesOf_testcases.keys())
def test_exact_matcher_case_insensitive_indexesOf(name, terms, expected_indicies):
    assert_indexesOf(EXACT_MATCHER_CASE_INSENSITIVE, name, terms, expected_indicies)

if __name__ == "__main__":
    exit(pytest.main())
