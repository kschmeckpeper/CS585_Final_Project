"""Functions for calculating timelines based on counting"""
from collections import Counter
import DateEventPair
import timex

def select_best_dates(path, num_dates=None):
    """ Returns an ordered list of the most common dates
    in the files containted in the path.
    """

    pairs = DateEventPair.read_reuters(path)

    date_counter = Counter()

    for pair in pairs:
        (tagged_text, dates) = timex.extract_dates(pair[1], pair[0])

        month = pair[0].month()
        if len(month) == 1:
            month = "0" + month
        day = pair[0].day()
        if len(day) == 1:
            day = "0" + day
        date_counter["%s-%s-%s" % (pair[0].year(), month, day)] += 1
        for date in dates:
            date_counter[date] += 1

    if num_dates is None:
        return date_counter.most_common()
    else:
        return date_counter.most_common(num_dates)

if __name__ == '__main__':

    print select_best_dates('reuters/')
