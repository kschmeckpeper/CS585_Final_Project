# -*- coding: utf-8 -*-
import os, datetime, re

path = '/Users/EvanReiff/Desktop/Senior 1/CMPSCI 585/Project/reuters21578/'

pairs = {}

for filename in os.listdir(path):
    if filename.endswith('.sgm'): #reuters
        #print filename
        files = open(path + filename).read().strip()
        if files.find("<BODY>") != -1:
            d_start = files.find("<DATE>")
            d_end = files.find("</DATE")
            dt = files[d_start:d_end]
            date = re.search("(\d+)-(\w+)-(\d+)", dt).group(0)
            day = re.search("(\d+)", date).group(0)
            month = re.search("(\D+)", date).group(0)
            month = month[1:-1]
            year = 1987
            if month=="JAN":
                month = 1
            elif month=="FEB":
                month = 2
            elif month=="MAR":
                month = 3
            elif month=="APR":
                month = 4
            elif month=="MAY":
                month = 5
            elif month=="JUN":
                month = 6
            elif month=="JUL":
                month = 7
            elif month=="AUG":
                month = 8
            elif month=="SEP":
                month = 9
            elif month=="OCT":
                month = 10
            elif month=="NOV":
                month = 11
            elif month=="DEC":
                month = 12
            obj = datetime.date(year, month, int(day))
            c_start = files.find("<BODY>")
            c_end = files.find("Reuter")
            body = files[c_start:c_end]
            content = body[6:]
            pairs[obj] = content
print pairs