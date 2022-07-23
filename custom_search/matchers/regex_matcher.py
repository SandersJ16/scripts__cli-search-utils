#!/usr/bin/env python

import regex as re
import operator
from functools import reduce, lru_cache

class RegexMatcher():
    def __init__(self, *, case_insensitive=False, advanced=True):
        self.re_matches = {}
        self.flags = []
        if case_insensitive:
            self.flags.append(re.IGNORECASE)

        if advanced:
            self.flags.append(re.VERSION1)

    def _getFlags(self):
        flags_value = 0
        if len(self.flags):
            flags_value = reduce(operator.or_, self.flags)

        return flags_value

    @lru_cache(128)
    def _getMatches(self, term, name):
        re_matches = []
        for match in re.finditer(term, name, flags=self._getFlags()):
            if len(match.group()):
                re_matches.append(match)
        return re_matches


    def matches(self, name, terms):
        matches = True
        for term in terms:
            re_matches = self._getMatches(term, name)
            if not len(re_matches):
                matches = False
                break

        return matches
                

    def indexesOf(self, name, terms):
        indexes = []
        for term in terms:
            for match in self._getMatches(term, name):
                indexes.append(match.span())
        return indexes
