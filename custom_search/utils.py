#!/usr/bin/env python

HIGHTLIGHT_COLOR = "01;31m" # Bold Red
STOP_COLOR = "0m"

def highlight2(matcher, text, highlight_text):
    indexes = matcher.indexesOf(text, highlight_text)
    return highlight(text, indexes)


def highlight(text, indexes):
    indexes = simplify_indexes(indexes)
    if len(indexes) == 0:
        return text

    highlight_starter = "\033[%s" % HIGHTLIGHT_COLOR
    highlight_ender = "\033[%s" % STOP_COLOR

    i = 0
    highlighted_text = ""
    for (start_index, end_index) in indexes:
        # Print previous text from last highlight
        highlighted_text += text[i:start_index]

        # Print Highlighted text
        highlighted_text += highlight_starter
        highlighted_text += text[start_index:end_index]
        highlighted_text += highlight_ender

        i = end_index

    # Print remainder of text
    highlighted_text += text[i:]
    return highlighted_text


def simplify_indexes(indexes):
    if len(indexes) in [0, 1]:
        return indexes

    simplified_indexes = []
    sorted_indexes = sorted(indexes)

    i = 1
    current_simplified_index_start = sorted_indexes[0][0]
    current_simplified_index_end = sorted_indexes[0][1]
    while True:
        index = sorted_indexes[i]
        if index[0] <= current_simplified_index_end:
            current_simplified_index_end = max(current_simplified_index_end, index[1])
        else:
            simplified_indexes.append((current_simplified_index_start, current_simplified_index_end))
            current_simplified_index_start = index[0]
            current_simplified_index_end = index[1]

        i += 1
        if i >= len(sorted_indexes):
            simplified_indexes.append((current_simplified_index_start, current_simplified_index_end))
            break

    return simplified_indexes
