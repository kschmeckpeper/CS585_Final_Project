"""Functions for calculating timelines based on counting"""
from collections import Counter
from dateutil.parser import parse
import datetime
import DateEventPair
import timex

def select_best_dates(path, num_dates=None, use_article_date=1):
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
            date_counter["%s" % (pair[0].date())] += 1

        for date in dates:
            date_counter[date] += 1

    if num_dates is None:
        return date_counter.most_common()
    else:
        return date_counter.most_common(num_dates)

if __name__ == '__main__':

    print select_best_dates('reuters/')
