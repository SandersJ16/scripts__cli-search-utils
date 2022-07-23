#!/usr/bin/env python

import pytest
from matchers.exact_matcher import ExactMatcher
from matchers.regex_matcher import RegexMatcher

EXACT_MATCHER = ExactMatcher()
EXACT_MATCHER_CASE_INSENSITIVE = ExactMatcher(case_insensitive=True)
REGEX_MATCHER = RegexMatcher()
REGEX_MATCHER_CASE_INSENSITIVE = RegexMatcher(case_insensitive=True)

def assert_indexesOf(matcher, name, terms, expected_indicies):
    assert matcher.indexesOf(name, terms) == expected_indicies

def assert_matches(matcher, name, terms, does_match):
    assert matcher.matches(name, terms) == does_match

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
#@pytest.mark.parametrize(["name", "terms", "expected_indicies"],
#    list(exact_matcher_indexesOf_testcases.values()) + list(regex_matcher_indexesOf_testcases.values()),
#    ids=list(exact_matcher_indexesOf_testcases.keys()) + list(regex_matcher_indexesOf_testcases.keys()))
@pytest.mark.parametrize(["name", "terms", "expected_indicies"],
    regex_matcher_indexesOf_testcases.values(),
    ids=regex_matcher_indexesOf_testcases.keys())
def test_regex_matcher_indexesOf(name, terms, expected_indicies):
    assert_indexesOf(REGEX_MATCHER, name, terms, expected_indicies)

if __name__ == "__main__":
    exit(pytest.main())
