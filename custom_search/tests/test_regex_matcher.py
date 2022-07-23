#!/usr/bin/env python

import pytest
from .utilities import assert_matches, assert_indexesOf
from matchers.regex_matcher import RegexMatcher
from .test_exact_matcher import exact_matcher_matches_testcases, exact_matcher_case_insensitive_matches_testcases


REGEX_MATCHER = RegexMatcher()
REGEX_MATCHER_CASE_INSENSITIVE = RegexMatcher(case_insensitive=True)

regex_matcher_matches_testcases = {
    "Single character wildcard":                 ("A", [r"."], True),
    "Multiple character wildcard":               ("AB", [r"."], True),
    "Dot-star wild card":                        ("ABC", [r".*"], True),
    "Beginning and Ending Anchors":              ("flat house", [r"^flat house$"], True),
    "End anchor must match end of line":         ("flat house", [r"flat$"], False),
    "Beginning anchor must match start of line": ("flat house", [r"^house"], False),
    "Multiple same word matches":                ("flat house", [r"^flat", r"f\w+"], True),
    "Some patterns match some do not":           ("flat house", [r"^flat", r"NoMatch"], False),
}
@pytest.mark.parametrize(["name", "terms", "does_match"],
    list(exact_matcher_matches_testcases.values()) + list(regex_matcher_matches_testcases.values()),
    ids=list(exact_matcher_matches_testcases.keys()) + list(regex_matcher_matches_testcases.keys()))
def test_regex_matcher_matches(name, terms, does_match):
    assert_matches(REGEX_MATCHER, name, terms, does_match)


regex_matcher_case_insensitive_matches_testcases = {
    "Explicit uppercase range matches":          ("words", [r"[A-Z]+"], True),
    "Beginning and Ending Anchors":              ("flat house", [r"^Flat House$"], True),
    "Multiple same word matches":                ("flat house", [r"^flAt", r"F\w+"], True),
}
@pytest.mark.parametrize(["name", "terms", "does_match"],
    list(exact_matcher_case_insensitive_matches_testcases.values()) + list(regex_matcher_case_insensitive_matches_testcases.values()),
    ids=list(exact_matcher_case_insensitive_matches_testcases.keys()) + list(regex_matcher_case_insensitive_matches_testcases.keys()))
def test_regex_matcher_matches(name, terms, does_match):
    assert_matches(REGEX_MATCHER_CASE_INSENSITIVE, name, terms, does_match)

regex_matcher_indexesOf_testcases = {
    "Wildcard star matches everything": ("this is stuff", [r".*"], [(0,13)]),
    "Wildcard plus matches everything": ("this is stuff", [r".+"], [(0,13)]),
    "Star is greedy":                   ("staff fighter", [r"sta.*f"], [(0,7)]),
    "Plus is greedy":                   ("staff fighter", [r"sta.+f"], [(0,7)]),
    "Non-greedy Star":                  ("staff fighter", [r"sta.*?f"], [(0,4)]),
    "Non-greedy plus":                  ("staff fighter", [r"sta.+?f"], [(0,5)]),
    "Multiple Matches":                 ("poke the paire", [r"p\w{2,3}e"], [(0,4), (9,14)]),
    "Multiple Regexes Match":           ("poke the paire", [r"p\w{2,3}e", r"the ?"], [(0,4), (9,14), (5,9)]),
}
@pytest.mark.parametrize(["name", "terms", "expected_indicies"],
    regex_matcher_indexesOf_testcases.values(),
    ids=regex_matcher_indexesOf_testcases.keys())
def test_regex_matcher_indexesOf(name, terms, expected_indicies):
    assert_indexesOf(REGEX_MATCHER, name, terms, expected_indicies)

if __name__ == "__main__":
    exit(pytest.main())
