#!/usr/bin/env python

import pytest
from matchers.exact_matcher import ExactMatcher

EXACT_MATCHER = ExactMatcher()

@pytest.mark.parametrize(["name", "terms", "does_match"], [
    ("Test", ["Test"], True),      # Exact full match
    ("Test", ["test"], False),     # Case-insensitive Match
    ("Test", ["bad"], False),      # non-match
    ("Test", ["est"], True),       # partial match
    ("Test", ["Te", "st"], True),  # Multiple partial matches
    ("Test", ["ba", "st"], False), # Multiple terms, some match some do not
    ("Test", ["es", "st"], True)   # Multiple overlapping partial matches
])
def test_exact_matcher_matches(name, terms, does_match):
    assert_matches(EXACT_MATCHER, name, terms, does_match)

@pytest.mark.parametrize(["name", "terms", "expected_indicies"], [
    ("Test", ["Test"], [(0,4)]),
    ("Test", ["test"], []),
    ("Test", ["Te"], [(0,2)]),
    ("Test", ["st"], [(2,4)]),
    ("Te Te hat", ["Te"], [(0,2), (3,5)]),
    ("TeTeTeTe", ["eTe"], [(1,4), (3,6), (5,8)]),
    ("Batman", ["Bat", "man"], [(0,3), (3,6)]),
    ("TeTeTeTe", ["eTe" , "Te"], [(1,4), (3,6), (5,8), (0,2), (2,4), (4,6), (6,8)])
])
def test_exact_mathcer_indexesOf(name, terms, expected_indicies):
    assert_indexesOf(EXACT_MATCHER, name, terms, expected_indicies)

def assert_indexesOf(matcher, name, terms, expected_indicies):
    assert matcher.indexesOf(name, terms) == expected_indicies

def assert_matches(matcher, name, terms, does_match):
    assert matcher.matches(name, terms) == does_match

if __name__ == "__main__":
    exit(pytest.main())
