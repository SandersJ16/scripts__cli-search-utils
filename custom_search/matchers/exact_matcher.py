#!/usr/bin/env python

class ExactMatcher():
    def matches(self, name, terms):
        matches = True
        for term in terms:
            if term not in name:
                matches = False
                break

        return matches

    def indexesOf(self, name, terms):
        indexes = []
        for term in terms:
            search_name = name
            offset = 0
            try:
                while search_name:
                    index = (search_name.index(term) + offset, search_name.index(term) + len(term) + offset)
                    indexes.append(index)
                    offset = index[0] + 1
                    search_name = name[offset:]
            except ValueError:
                pass
        return indexes
