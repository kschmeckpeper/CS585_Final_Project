import DateEventPair
import timex
from collections import Counter

if __name__ == '__main__':
	pairs = DateEventPair.read_reuters('reuters/')
	
	date_counter = Counter()

	for pair in pairs:

		(tagged_text, dates) = timex.extract_dates(pair[1], pair[0])
		for date in dates:
			date_counter[date] += 1

	print date_counter.most_common()
	