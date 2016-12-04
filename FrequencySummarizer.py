#http://glowingpython.blogspot.com/2014/09/text-summarization-with-nltk.html

from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest

min_cut = 0.1
max_cut = 0.9
stopwords = set(stopwords.words('english') + list(punctuation))

def _compute_frequencies(word_sent):
    """
      Compute the frequency of each of word.
      Input:
       word_sent, a list of sentences already tokenized.
      Output:
       freq, a dictionary where freq[w] is the frequency of w.
    """
    freq = defaultdict(int)
    for s in word_sent:
        for word in s:
            if word not in stopwords:
                freq[word] += 1
    # frequencies normalization and fitering
    '''m = float(max(freq.values()))
    for w in freq.keys():
        freq[w] = freq[w]/m
        if freq[w] >= max_cut or freq[w] <= min_cut:
            del freq[w]'''
    return freq

def summarize(text, n):
    """
      Return a list of n sentences
      which represent the summary of text.
    """
    '''sents = sent_tokenize(text)
    assert n <= len(sents)
    word_sent = [word_tokenize(s.lower()) for s in sents]'''
    freq = _compute_frequencies(text)
    ranking = defaultdict(int)
    for i,sent in enumerate(text):
        for w in sent:
            if w in freq:
                ranking[i] += freq[w]
    sents_idx = _rank(ranking, n)
    return [text[j] for j in sents_idx]

def _rank(ranking, n):
    """ return the first n sentences with highest ranking """
    return nlargest(n, ranking, key=ranking.get)
