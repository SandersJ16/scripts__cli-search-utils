#!/usr/bin/env python

def assert_indexesOf(matcher, name, terms, expected_indicies):
    assert matcher.indexesOf(name, terms) == expected_indicies

def assert_matches(matcher, name, terms, does_match):
    assert matcher.matches(name, terms) == does_match
