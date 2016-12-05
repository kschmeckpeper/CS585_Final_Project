# Modified from nltk_contrib/timex.py

from dateutil.parser import parse
import nltk
import re
import string
import os
import sys
from datetime import timedelta

# Predefined strings.
numbers = "(^a(?=\s)|one|two|three|four|five|six|seven|eight|nine|ten| \
          eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen| \
          eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty| \
          ninety|hundred|thousand)"
day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
week_day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
month = "(january|february|march|april|may|june|july|august|september| october|november|december)"
dmy = "(year|day|week|month)"
rel_day = "(today|yesterday|tomorrow|tonight|tonite)"
exp1 = "(before|after|earlier|later|ago)"
exp2 = "(this|next|last)"
iso = "\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+"
year = "((?<=\s)\d{4}|^\d{4})"
regxp1 = "((\d+|(" + numbers + "[-\s]?)+) " + dmy + "s? " + exp1 + ")"
regxp2 = "(" + exp2 + " (" + dmy + "|" + week_day + "|" + month + "))"

reg1 = re.compile(regxp1, re.IGNORECASE)
reg2 = re.compile(regxp2, re.IGNORECASE)
reg3 = re.compile(rel_day, re.IGNORECASE)
reg4 = re.compile(iso)
reg5 = re.compile(year)

def tag(text):

    # Initialization
    timex_found = []

    # re.findall() finds all the substring matches, keep only the full
    # matching string. Captures expressions such as 'number of days' ago, etc.
    found = reg1.findall(text)
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # Variations of this thursday, next year, etc
    found = reg2.findall(text)
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # today, tomorrow, etc
    found = reg3.findall(text)
    for timex in found:
        timex_found.append(timex)

    # ISO
    found = reg4.findall(text)
    for timex in found:
        timex_found.append(timex)

    # Year
    found = reg5.findall(text)
    for timex in found:
        timex_found.append(timex)

    # Tag only temporal expressions which haven't been tagged.
    for timex in timex_found:
        text = re.sub(timex + '(?!</TIMEX2>)', '<TIMEX2>' + timex + '</TIMEX2>', text)

    return text

# Hash function for week days to simplify the grounding task.
# [Mon..Sun] -> [0..6]
hashweekdays = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6}

# Hash function for months to simplify the grounding task.
# [Jan..Dec] -> [1..12]
hashmonths = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12}

# Hash number in words into the corresponding integer value
def hashnum(number):
    if re.match(r'one|^a\b', number, re.IGNORECASE):
        return 1
    if re.match(r'two', number, re.IGNORECASE):
        return 2
    if re.match(r'three', number, re.IGNORECASE):
        return 3
    if re.match(r'four', number, re.IGNORECASE):
        return 4
    if re.match(r'five', number, re.IGNORECASE):
        return 5
    if re.match(r'six', number, re.IGNORECASE):
        return 6
    if re.match(r'seven', number, re.IGNORECASE):
        return 7
    if re.match(r'eight', number, re.IGNORECASE):
        return 8
    if re.match(r'nine', number, re.IGNORECASE):
        return 9
    if re.match(r'ten', number, re.IGNORECASE):
        return 10
    if re.match(r'eleven', number, re.IGNORECASE):
        return 11
    if re.match(r'twelve', number, re.IGNORECASE):
        return 12
    if re.match(r'thirteen', number, re.IGNORECASE):
        return 13
    if re.match(r'fourteen', number, re.IGNORECASE):
        return 14
    if re.match(r'fifteen', number, re.IGNORECASE):
        return 15
    if re.match(r'sixteen', number, re.IGNORECASE):
        return 16
    if re.match(r'seventeen', number, re.IGNORECASE):
        return 17
    if re.match(r'eighteen', number, re.IGNORECASE):
        return 18
    if re.match(r'nineteen', number, re.IGNORECASE):
        return 19
    if re.match(r'twenty', number, re.IGNORECASE):
        return 20
    if re.match(r'thirty', number, re.IGNORECASE):
        return 30
    if re.match(r'forty', number, re.IGNORECASE):
        return 40
    if re.match(r'fifty', number, re.IGNORECASE):
        return 50
    if re.match(r'sixty', number, re.IGNORECASE):
        return 60
    if re.match(r'seventy', number, re.IGNORECASE):
        return 70
    if re.match(r'eighty', number, re.IGNORECASE):
        return 80
    if re.match(r'ninety', number, re.IGNORECASE):
        return 90
    if re.match(r'hundred', number, re.IGNORECASE):
        return 100
    if re.match(r'thousand', number, re.IGNORECASE):
      return 1000

# Takes in an article's text and its publication date
# Returns - (tagged_text, dates)
#   tagged_text - the tagged text with the absolute dates
#   dates - a list of all strings describing all the dates apearing in the text
#
# Both use the same format of strings to describe dates
#   The strings describing the dates may have different formats based on how
#   accurate they are.
#   EX.
#       '2002' is accurate to the nearest year, for instance from the phrase 'last year'
#       '2016-10' is accurate to the nearest month
#       '2016W42' is accurate to the nearest week
#       '2016-11-04' is accurate to the nearest day


# Uses the base_date to calculate the absolute date
# of relative dates given in the text
def extract_dates(text, base_date):
    dates = []

    tagged_text = tag(text)
    sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    sentences = sentence_detector.tokenize(tagged_text.strip())

    for sentence in sentences:
        # Removes invalid sentences
        if ("       " in sentence or
                "....." in sentence or
                "(continued)" in sentence.lower() or
                sentence[0:3] == "Shr" or
                sentence[0:9] == "Group shr" or
                sentence[0:4] == "Qtly" or
                sentence[0:5] == "Qtrly" or
                sentence[0:4] == "Oper" or
                sentence[0:4] == "Unit" or
                sentence[0:6].lower() == "reuter"):
            continue

        # Maybe split sentences based on following regex
        # [a-zA-Z][.][.][.][A-Z]
        # if ... continues to be a problem

        # Find all identified timex and put them into a list
        timex_regex = re.compile(r'<TIMEX2>.*?</TIMEX2>', re.DOTALL)
        timex_found = timex_regex.findall(sentence)
        timex_found = map(lambda timex:re.sub(r'</?TIMEX2.*?>', '', timex), \
                    timex_found)

        # Calculate the new date accordingly
        for timex in timex_found:
            day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
            week_day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
            month = "(january|february|march|april|may|june|july|august|september| october|november|december)"
            dmy = "(year|day|week|month)"
            rel_day = "(today|yesterday|tomorrow|tonight|tonite)"
            exp1 = "(before|after|earlier|later|ago)"
            exp2 = "(this|next|last)"

            timex_val = 'UNKNOWN' # Default value

            timex_ori = timex   # Backup original timex for later substitution

            # If numbers are given in words, hash them into corresponding numbers.
            # eg. twenty five days ago --> 25 days ago
            if re.search(numbers, timex, re.IGNORECASE):
                split_timex = re.split(r'\s(?=days?|months?|years?|weeks?)', \
                                                                  timex, re.IGNORECASE)
                value = split_timex[0]
                unit = split_timex[1]
                num_list = map(lambda s:hashnum(s),re.findall(numbers + '+', \
                                              value, re.IGNORECASE))
                timex = `sum(num_list)` + ' ' + unit

            # If timex matches ISO format, remove 'time' and reorder 'date'
            if re.match(r'\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+', timex):
                dmy = re.split(r'\s', timex)[0]
                dmy = re.split(r'/|-', dmy)
                timex_val = str(dmy[2]) + '-' + str(dmy[1]) + '-' + str(dmy[0])

            # Specific dates
            elif re.match(r'\d{4}', timex):
                timex_val = str(timex)
                # print "1", timex_val

            # Relative dates
            elif re.match(r'tonight|tonite|today', timex, re.IGNORECASE):
                timex_val = str(base_date)
            elif re.match(r'yesterday', timex, re.IGNORECASE):
                timex_val = str(base_date + timedelta(days=-1))
            elif re.match(r'tomorrow', timex, re.IGNORECASE):
                timex_val = str(base_date + timedelta(days=+1))

            # Weekday in the previous week.
            elif re.match(r'last ' + week_day, timex, re.IGNORECASE):
                day = hashweekdays[timex.split()[1].lower()]
                curr_day = base_date.weekday()
                timex_val = str(base_date + timedelta(days=-7+(day-curr_day)%7))
                # print "Weekdays may not behave as desired"
                # print timex, day, curr_day, base_date, timex_val, (-7+(day-curr_day)%7)

            # Weekday in the current week.
            elif re.match(r'this ' + week_day, timex, re.IGNORECASE):
                day = hashweekdays[timex.split()[1].lower()]
                curr_day = base_date.weekday()
                timex_val = str(base_date + timedelta(days=(day-curr_day)%7))
                # print "Weekdays may not behave as desired"
                # print timex, day, curr_day, base_date, timex_val, ((day-curr_day)%7)

            # Weekday in the following week.
            elif re.match(r'next ' + week_day, timex, re.IGNORECASE):
                day = hashweekdays[timex.split()[1].lower()]
                curr_day = base_date.weekday()
                timex_val = str(base_date + timedelta(days=7+(day-curr_day)%7))
                # print "Weekdays may not behave as desired"
                # print timex, day, curr_day, base_date, timex_val, ((day-curr_day)%7)

            # Last, this, next week.
            elif re.match(r'last week', timex, re.IGNORECASE):
                year = (base_date + timedelta(weeks=-1)).year

                # iso_week returns a triple (year, week, day) hence, retrieve
                # only week value.
                week = (base_date + timedelta(weeks=-1)).isocalendar()[1]
                timex_val = str(year) + 'W' + str(week)
            elif re.match(r'this week', timex, re.IGNORECASE):
                year = (base_date + timedelta(weeks=0)).year
                week = (base_date + timedelta(weeks=0)).isocalendar()[1]
                timex_val = str(year) + 'W' + str(week)
            elif re.match(r'next week', timex, re.IGNORECASE):
                year = (base_date + timedelta(weeks=+1)).year
                week = (base_date + timedelta(weeks=+1)).isocalendar()[1]
                timex_val = str(year) + 'W' + str(week)

            # Month in the previous year.
            elif re.match(r'last ' + month, timex, re.IGNORECASE):
                month = hashmonths[timex.split()[1].lower()]
                timex_val = str(base_date.year - 1) + '-' + str(month)

            # Month in the current year.
            elif re.match(r'this ' + month, timex, re.IGNORECASE):
                month = hashmonths[timex.split()[1].lower()]
                timex_val = str(base_date.year) + '-' + str(month)

            # Month in the following year.
            elif re.match(r'next ' + month, timex, re.IGNORECASE):
                month = hashmonths[timex.split()[1].lower()]
                timex_val = str(base_date.year + 1) + '-' + str(month)
            elif re.match(r'last month', timex, re.IGNORECASE):

                # Handles the year boundary.
                if base_date.month == 1:
                    timex_val = str(base_date.year - 1) + '-' + '12'
                else:
                    timex_val = str(base_date.year) + '-' + str(base_date.month - 1)
            elif re.match(r'this month', timex, re.IGNORECASE):
                    timex_val = str(base_date.year) + '-' + str(base_date.month)
            elif re.match(r'next month', timex, re.IGNORECASE):

                # Handles the year boundary.
                if base_date.month == 12:
                    timex_val = str(base_date.year + 1) + '-' + '1'
                else:
                    timex_val = str(base_date.year) + '-' + str(base_date.month + 1)
            elif re.match(r'last year', timex, re.IGNORECASE):
                timex_val = str(base_date.year - 1)
            elif re.match(r'this year', timex, re.IGNORECASE):
                timex_val = str(base_date.year)
            elif re.match(r'next year', timex, re.IGNORECASE):
                timex_val = str(base_date.year + 1)
            elif re.match(r'\d+ days? (ago|earlier|before)', timex, re.IGNORECASE):

                # Calculate the offset by taking '\d+' part from the timex.
                offset = int(re.split(r'\s', timex)[0])
                timex_val = str(base_date + timedelta(days=-offset))
            elif re.match(r'\d+ days? (later|after)', timex, re.IGNORECASE):
                offset = int(re.split(r'\s', timex)[0])
                timex_val = str(base_date + timedelta(days=+offset))
            elif re.match(r'\d+ weeks? (ago|earlier|before)', timex, re.IGNORECASE):
                offset = int(re.split(r'\s', timex)[0])
                year = (base_date + timedelta(weeks=-offset)).year
                week = (base_date + \
                                timedelta(weeks=-offset)).isocalendar()[1]
                timex_val = str(year) + 'W' + str(week)
            elif re.match(r'\d+ weeks? (later|after)', timex, re.IGNORECASE):
                offset = int(re.split(r'\s', timex)[0])
                year = (base_date + timedelta(weeks=+offset)).year
                week = (base_date + timedelta(weeks=+offset)).isocalendar()[1]
                timex_val = str(year) + 'W' + str(week)
            elif re.match(r'\d+ months? (ago|earlier|before)', timex, re.IGNORECASE):
                extra = 0
                offset = int(re.split(r'\s', timex)[0])

                # Checks if subtracting the remainder of (offset / 12) to the base month
                # crosses the year boundary.
                if (base_date.month - offset % 12) < 1:
                    extra = 1

                # Calculate new values for the year and the month.
                year = str(base_date.year - offset // 12 - extra)
                month = str((base_date.month - offset % 12) % 12)

                # Fix for the special case.
                if month == '0':
                    month = '12'
                timex_val = year + '-' + month
            elif re.match(r'\d+ months? (later|after)', timex, re.IGNORECASE):
                extra = 0
                offset = int(re.split(r'\s', timex)[0])
                if (base_date.month + offset % 12) > 12:
                    extra = 1
                year = str(base_date.year + offset // 12 + extra)
                month = str((base_date.month + offset % 12) % 12)
                if month == '0':
                    month = '12'
                timex_val = year + '-' + month
            elif re.match(r'\d+ years? (ago|earlier|before)', timex, re.IGNORECASE):
                offset = int(re.split(r'\s', timex)[0])
                timex_val = str(base_date.year - offset)
            elif re.match(r'\d+ years? (later|after)', timex, re.IGNORECASE):
                offset = int(re.split(r'\s', timex)[0])
                timex_val = str(base_date.year + offset)

            # Remove 'time' from timex_val.
            # For example, If timex_val = 2000-02-20 12:23:34.45, then
            # timex_val = 2000-02-20
            timex_val = re.sub(r'\s.*', '', timex_val)

            # dates.append((timex_val, sentence))
            # Substitute tag+timex in the text with grounded tag+timex.
            sentence_with_tags = re.sub('<TIMEX2>' + timex_ori + '</TIMEX2>', '<TIMEX2 val=\"' \
                + timex_val + '\">' + timex_ori + '</TIMEX2>', sentence)

            sentence_with_tags = re.sub('[\\n]', ' ', sentence_with_tags)
            #sentence_with_tags = sentence_with_tags.translate(None, "\\ ")

            dates.append((timex_val, sentence_with_tags))


    return dates



####

def demo():
    import nltk
    text = nltk.corpus.abc.raw('rural.txt')[:10000]
    print tag(text)







if __name__ == '__main__':
    # print len(nltk.corpus.abc.raw('rural.txt'))
    # nltk.download()
    text = nltk.corpus.abc.raw('rural.txt')

    basedate = parse("Wednesday")
    dates = extract_dates(text, basedate)
    print dates
