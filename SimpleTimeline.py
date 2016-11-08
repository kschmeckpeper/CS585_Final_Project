"""Functions for calculating timelines based on counting"""
from collections import Counter
import DateEventPair
import timex

def add_date(string, counter, timespan=0):
    """ Adds the date to the counter
    Timespan defines the timespan that the timeline is using
    0 - Days
    1 - Weeks
    2 - Months
    3 - Years

    add_date will remove all dates with less precision,
    and put all dates with more precision into the correct bin
    """

    if timespan == 0:
        # Only use the strings with the day specified
        if len(string) == 10:
            counter[string] += 1
    else:
        print "Timespans of weeks, months, and years are not implemented yet"


def remove_invalid_dates(should_filter, string, counter):
    """ Checks to see if the date string is valid.
    If the string is valid, adds 1 to that key in the counter

    If filter is false, will not check if the string is valid

    Currently only checks to see if year is in the correct range
    """
    if not should_filter:
        counter[string] += 1
    else:
        try:
            date = int(string[0:4])
            if date > 1900 and date < 2100:
                add_date(string, counter)
        except ValueError:
            pass

def select_best_dates(path, num_dates=None, use_article_date=1, filter_dates=False):
    """ Returns an ordered list of the most common dates and a 1 sentence summary
    in the files containted in the path.

    use_article_date
    0 - never use article date
    1 - use article date when the article contains no other dates
    2 - always use article date
    """

    pairs = DateEventPair.read_reuters(path)

    date_counter = Counter()


    # Summary is currently found by taking the sentence surrounding the
    # last mention of each date
    basic_summaries = {}

    for pair in pairs:
        dates = timex.extract_dates(pair[1], pair[0])

        if use_article_date == 2 or (use_article_date == 1 and len(dates) == 0):
            remove_invalid_dates(filter_dates, "%s" % (pair[0].date()), date_counter)

        for date in dates:
            remove_invalid_dates(filter_dates, date[0], date_counter)
            basic_summaries[date[0]] = date[1]

    dates_to_return = date_counter.most_common()

    if num_dates is not None:
        dates_to_return = date_counter.most_common(num_dates)

    date_with_summarization = []

    for date in dates_to_return:
        date_with_summarization.append((date[0], date[1], basic_summaries[date[0]]))

    return date_with_summarization

if __name__ == '__main__':

    print select_best_dates('reuters/', filter_dates=True)
