"""Functions for calculating timelines based on counting"""
from collections import Counter
from collections import defaultdict
import DateEventPair
import timex
import re
from nltk.tokenize import word_tokenize

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

def count_word_word_matrix(corpus, dist=7):
    """ Returns a dictionary of dictionaries, both indexed on words
    Each of the secondary dictionaries should contain the number of
    times that the current key occurs near the key for the entire
    dictionary in the training corpus.
    """
    
    matrix = {}
    is_number = re.compile("\d")

    for article_index in range(len(corpus)):
        tokens = word_tokenize(corpus[article_index][1])
        for count in range(len(tokens)):
            word = tokens[count].lower()
            
            if bool(is_number.search(word)):
                word = "<NUMBER>"

            if word not in matrix:
                matrix[word] = defaultdict(int)
            low = count-dist
            high = count+dist
            tmp = low
            while tmp <= high:
                if tmp < 0:
                    matrix[word][" "] += 1
                elif tmp >= len(tokens):
                    matrix[word][" "] += 1
                else:
                    if bool(is_number.search(tokens[tmp])):
                        matrix[word]["<NUMBER>"] += 1
                    else:
                        matrix[word][tokens[tmp].lower()] += 1
                tmp += 1
    return matrix

def calc_word_similarity(first_word, second_word, matrix):
    first_word = first_word.lower()
    second_word = second_word.lower()
    
    if first_word not in matrix or second_word not in matrix:
        return 0

    first_dot_second = 0.0
    first_length = 0.0

    for key in matrix[first_word]:
        first_dot_second += matrix[first_word][key] * matrix[second_word][key]
        first_length += matrix[first_word][key]**2

    second_length = 0.0
    for key in matrix[second_word]:
        second_length += matrix[second_word][key]**2

    return first_dot_second / (first_length * second_length)

def calc_sentence_similarity(first_sentence, second_sentence, matrix):
    first_tokens = word_tokenize(first_sentence)
    second_tokens = word_tokenize(second_sentence)

    total_similarity = 0.0

    for token in first_tokens:
        best_word_similarity = 0.0

        for canidate in second_tokens:
            similarity = calc_word_similarity(token, canidate, matrix)
            if similarity > best_word_similarity:
                best_word_similarity = similarity
        total_similarity += best_word_similarity

    return total_similarity / len(first_tokens)

def summarize(sentences, matrix):

    best_sentence_similarity = 0
    best_sentence = ""
    outer_count = 0
    
    for canidate_sentence in sentences:
        print canidate_sentence
        total_similarity = 0
        count = 0
        for sentence in sentences:
            total_similarity += calc_sentence_similarity(canidate_sentence, sentence, matrix)
            count += 1
            print "Checked ", count, "/", len(sentences)

        if total_similarity > best_sentence_similarity:
            best_sentence = canidate_sentence
            best_sentence_similarity = total_similarity
        print "Outer count ", outer_count, "/", len(sentences)

    return best_sentence

def select_best_dates(path, num_dates=None, use_article_date=1, filter_dates=False):
    """ Returns an ordered list of the most common dates and a 1 sentence summary
    in the files containted in the path.

    use_article_date
    0 - never use article date
    1 - use article date when the article contains no other dates
    2 - always use article date
    """

    pairs = DateEventPair.read_reuters(path)
    matrix = count_word_word_matrix(pairs)
    date_counter = Counter()

    sentence_list = {}

    for pair in pairs:
        dates = timex.extract_dates(pair[1], pair[0])

        if use_article_date == 2 or (use_article_date == 1 and len(dates) == 0):
            remove_invalid_dates(filter_dates, "%s" % (pair[0].date()), date_counter)

        for date in dates:
            remove_invalid_dates(filter_dates, date[0], date_counter)
            if date[0] not in sentence_list:
                sentence_list[date[0]] = []
            sentence_list[date[0]].append(date[1])

    dates_to_return = date_counter.most_common()

    if num_dates is not None:
        dates_to_return = date_counter.most_common(num_dates)

    date_with_summarization = []

    for date in dates_to_return:
        print date
        date_with_summarization.append((date[0], date[1], summarize(sentence_list[date[0]], matrix)))

    return date_with_summarization

if __name__ == '__main__':

    print select_best_dates('reuters/', filter_dates=True)
