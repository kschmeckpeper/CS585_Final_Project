import DateEventPair
import timex
from collections import Counter

def select_best_dates(path, num_dates=None):
	pairs = DateEventPair.read_reuters(path)
	
	date_counter = Counter()

	for pair in pairs:

		(tagged_text, dates) = timex.extract_dates(pair[1], pair[0])
		for date in dates:
			date_counter[date] += 1

	if num_dates	== None:
		return date_counter.most_common()
	else:
		return date_counter.most_common(num_dates)

if __name__ == '__main__':

	print select_best_dates('reuters/')
	
	