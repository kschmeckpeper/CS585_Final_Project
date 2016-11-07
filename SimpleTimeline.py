"""Functions for calculating timelines based on counting"""
from collections import Counter
from dateutil.parser import parse
import datetime
import DateEventPair
import timex

def remove_invalid_dates(filter, string, counter):
    """ Checks to see if the date string is valid.
    If the string is valid, adds 1 to that key in the counter

    If filter is false, will not check if the string is valid

    Currently only checks to see if year is in the correct range
    """
    if not filter:
        counter[string] += 1
    else:
        try:
            date = int(string[0:4])
            if 1900 < date and date < 2100:
                counter[string] += 1
        except ValueError:
            pass

def select_best_dates(path, num_dates=None, use_article_date=1, filter_dates=False):
    """ Returns an ordered list of the most common dates
    in the files containted in the path.

    use_article_date
    0 - never use article date
    1 - use article date when the article contains no other dates
    2 - always use article date
    """

    pairs = DateEventPair.read_reuters(path)

    date_counter = Counter()

    for pair in pairs:
        (tagged_text, dates) = timex.extract_dates(pair[1], pair[0])
        
        if use_article_date == 2 or (use_article_date == 1 and len(dates) == 0):
            remove_invalid_dates(filter_dates, "%s" % (pair[0].date()), date_counter)

        for date in dates:
            remove_invalid_dates(filter_dates, date, date_counter)

    if num_dates is None:
        return date_counter.most_common()
    else:
        return date_counter.most_common(num_dates)

if __name__ == '__main__':

    print select_best_dates('reuters/', filter_dates=True)
