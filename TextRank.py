"""
Code from https://github.com/ayushkalani/TextRank-Summarization/blob/master/textrank.py


https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf

The MIT License (MIT)

Copyright (c) 2016 ayushkalani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import nltk
import itertools
from operator import itemgetter
import networkx as nx
import os

#apply syntactic filters based on POS tags
def filter_for_tags(tagged, tags=['NN', 'JJ', 'NNP']):
    return [item for item in tagged if item[1] in tags]

def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]

def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def lDistance(firstString, secondString):
    "Function to find the Levenshtein distance between two words/sentences - gotten from http://rosettacode.org/wiki/Levenshtein_distance#Python"
    if len(firstString) > len(secondString):
        firstString, secondString = secondString, firstString
    distances = range(len(firstString) + 1)
    for index2, char2 in enumerate(secondString):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(firstString):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1], distances[index1+1], newDistances[-1])))
        distances = newDistances
    return distances[-1]

def buildGraph(nodes):
    "nodes - list of hashables that represents the nodes of the graph"
    #itertools generate all possible combinations ex {1,2,3} itertools.combinations(array,2)=1,2 1,3 2,3
    gr = nx.Graph() #initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    #add edges to the graph (weighted by Levenshtein distance)
    for pair in nodePairs:
        firstString = pair[0]
        secondString = pair[1]
        levDistance = lDistance(firstString, secondString)
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr

def extractKeyphrases(text):
    #tokenize the text using nltk
    wordTokens = nltk.word_tokenize(text)

    #assign POS tags to the words in the text
    tagged = nltk.pos_tag(wordTokens)
    textlist = [x[0] for x in tagged]
    
    tagged = filter_for_tags(tagged)
    tagged = normalize(tagged)
    #print tagged

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

   #this will be used to determine adjacent words in order to construct keyphrases with two words

    graph = buildGraph(word_set_list)

    #pageRank - initial value of 1.0, error tolerance of 0,0001, 
    #nx.pagerank()-returns the page rank of the nodes in the graph in thr form of a dictionary of nodes with pagerank as value 
    calculated_page_rank = nx.pagerank(graph, weight='weight')
    #print calculated_page_rank

    #most important words in ascending order of importance
    keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)
    # print keyphrases
    #the number of keyphrases returned will be relative to the size of the text (a third of the number of vertices)
    aThird = len(word_set_list) / 3
    keyphrases = keyphrases[0:aThird+1]

    #take keyphrases with multiple words into consideration as done in the paper - if two words are adjacent in the text and are selected as keywords, join them
    #together
    modifiedKeyphrases = set([])
    dealtWith = set([]) #keeps track of individual keywords that have been joined to form a keyphrase
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]
        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith: 
                modifiedKeyphrases.add(firstWord)

            #if this is the last word in the text, and it is a keyword,
            #it definitely has no chance of being a keyphrase at this point    
            if j == len(textlist)-1 and secondWord in keyphrases and secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord)
        
        i = i + 1
        j = j + 1
        
    return modifiedKeyphrases

def extractSentences(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentenceTokens = sent_detector.tokenize(text.strip())
    return extractSentencesFromSentenceTokens(sentenceTokens)

def extractSentencesFromSentenceTokens(sentenceTokens):
    graph = buildGraph(sentenceTokens)

    calculated_page_rank = nx.pagerank(graph, weight='weight')

    #most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

    #return a 100 word summary
    # summary = ' '.join(sentences)
    # summaryWords = summary.split()
    # summaryWords = summaryWords[0:101]
    # summary = ' '.join(summaryWords)

    return sentences[0]
    # return summary

def writeFiles(summary, keyphrases, fileName):
    "outputs the keyphrases and summaries to appropriate files"
    print "Generating output to " + 'keywords/' + fileName
    keyphraseFile = open('keywords/' + fileName, 'w')
    for keyphrase in keyphrases:
        keyphraseFile.write(keyphrase + '\n')
    keyphraseFile.close()

    print "Generating output to " + 'summaries/' + fileName
    summaryFile = open('summaries/' + fileName, 'w')
    summaryFile.write(summary)
    summaryFile.close()

    print "-"


if __name__ == '__main__':
    text="""BankAmerica Corp is not under
    pressure to act quickly on its proposed equity offering and
    would do well to delay it because of the stock's recent poor
    performance, banking analysts said.
        Some analysts said they have recommended BankAmerica delay
    its up to one-billion-dlr equity offering, which has yet to be
    approved by the Securities and Exchange Commission.
        BankAmerica stock fell this week, along with other banking
    issues, on the news that Brazil has suspended interest payments
    on a large portion of its foreign debt.
        The stock traded around 12, down 1/8, this afternoon,
    after falling to 11-1/2 earlier this week on the news.
        Banking analysts said that with the immediate threat of the
    First Interstate Bancorp &lt;I> takeover bid gone, BankAmerica is
    under no pressure to sell the securities into a market that
    will be nervous on bank stocks in the near term.
        BankAmerica filed the offer on January 26. It was seen as
    one of the major factors leading the First Interstate
    withdrawing its takeover bid on February 9.
        A BankAmerica spokesman said SEC approval is taking longer
    than expected and market conditions must now be re-evaluated.
        "The circumstances at the time will determine what we do,"
    said Arthur Miller, BankAmerica's Vice President for Financial
    Communications, when asked if BankAmerica would proceed with
    the offer immediately after it receives SEC approval.
        "I'd put it off as long as they conceivably could," said
    Lawrence Cohn, analyst with Merrill Lynch, Pierce, Fenner and
    Smith.
        Cohn said the longer BankAmerica waits, the longer they
    have to show the market an improved financial outlook.
        Although BankAmerica has yet to specify the types of
    equities it would offer, most analysts believed a convertible
    preferred stock would encompass at least part of it.
        Such an offering at a depressed stock price would mean a
    lower conversion price and more dilution to BankAmerica stock
    holders, noted Daniel Williams, analyst with Sutro Group.
        Several analysts said that while they believe the Brazilian
    debt problem will continue to hang over the banking industry
    through the quarter, the initial shock reaction is likely to
    ease over the coming weeks.
        Nevertheless, BankAmerica, which holds about 2.70 billion
    dlrs in Brazilian loans, stands to lose 15-20 mln dlrs if the
    interest rate is reduced on the debt, and as much as 200 mln
    dlrs if Brazil pays no interest for a year, said Joseph
    Arsenio, analyst with Birr, Wilson and Co.
        He noted, however, that any potential losses would not show
    up in the current quarter.
        With other major banks standing to lose even more than
    BankAmerica if Brazil fails to service its debt, the analysts
    said they expect the debt will be restructured, similar to way
    Mexico's debt was, minimizing losses to the creditor banks.
    """
    keyphrases = extractKeyphrases(text)
    summary = extractSentences(text)
    print keyphrases

    print summary