#!/usr/bin/env python

import os
import utils

from argparse import ArgumentParser
from signal import SIGINT
from matchers.exact_matcher import ExactMatcher


root_dir = "."


def parse_arguments():
    parser = ArgumentParser(description="Search for files or text in files")
    parser.add_argument('search_terms', metavar='SEARCH_TERM', type=str, nargs='+',
                        help='Terms you are searching for')
    parser.add_argument('--ignore-case', '-i', action="store_true", default=False,
                        help='Ignore case distinctions, so that characters that differ only in case match each other.')
    arguments = parser.parse_args()
    return arguments


def get_matcher(arguments):
    return ExactMatcher(case_insensitive=arguments.ignore_case)


def highlight(matcher, text, highlight_text):
    indexes = matcher.indexesOf(text, highlight_text)
    return utils.highlight(text, indexes)

if __name__ == "__main__":
    try:
        arguments = parse_arguments()
        matcher = get_matcher(arguments)

        for path, directories, files in os.walk(root_dir):
            for file in files:
                if matcher.matches(file, arguments.search_terms):
                    print(os.path.join(path, highlight(matcher, file, arguments.search_terms)))

            for directory in directories:
                if matcher.matches(directory, arguments.search_terms):
                    print(os.path.join(path, highlight(matcher, directory, arguments.search_terms)))


    except KeyboardInterrupt:
        exit(SIGINT)

