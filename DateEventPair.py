# -*- coding: utf-8 -*-
import os, datetime, re
from dateutil.parser import parse
def read_reuters(path):
    pairs = []

    for filename in os.listdir(path):
        if filename.endswith('.sgm'): #reuters
            #print filename
            file = open(path + os.path.sep + filename).read().strip()

            curr_index = 0
            while file.find("<REUTERS", curr_index) != -1:
            	date_start = file.find("<DATE>", curr_index)
            	date_start = file.find(">", date_start) + 1
            	date_end = date_start + 11
            	date_string = file[date_start:date_end]
            	date = parse(date_string)
            	

            	body_start = file.find("<BODY>", curr_index) + 6
            	body_end = file.find("</BODY>", curr_index)
            	
            	curr_index = file.find("</REUTERS>", curr_index) + 1

            	if body_start > curr_index or body_start == -1:
            		continue

            	text = file[body_start:body_end]
            	
            	pairs.append((date, text))

    return pairs

if __name__ == '__main__':
    pairs = read_reuters('reuters')
    print pairs