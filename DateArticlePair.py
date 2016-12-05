# -*- coding: utf-8 -*-
""" Functions to read from the datasets and
output pairs of (date, text)
"""

import os
from dateutil.parser import parse

def read_reuters(path):
    """Extracts date,text pairs from all files in a folder.
    Assumes the files are in reuters format.
    """

    pairs = []

    for filename in os.listdir(path):
        if filename.endswith('.sgm'): #reuters
            #print filename
            curr_file = open(path + os.path.sep + filename).read().strip()

            curr_index = 0
            while curr_file.find("<REUTERS", curr_index) != -1:
                date_start = curr_file.find("<DATE>", curr_index)
                date_start = curr_file.find(">", date_start) + 1
                date_end = date_start + 11
                date_string = curr_file[date_start:date_end]
                date = parse(date_string)

                body_start = curr_file.find("<BODY>", curr_index) + 6
                body_end = curr_file.find("</BODY>", curr_index)

                curr_index = curr_file.find("</REUTERS>", curr_index) + 1

                if body_start > curr_index or body_start == -1 + 6:
                    continue

                text = curr_file[body_start:body_end]


                pairs.append((date, text))

    return pairs

if __name__ == '__main__':
    read_reuters('reuters')
