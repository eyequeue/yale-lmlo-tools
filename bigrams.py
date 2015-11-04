#! /usr/bin/python

from lmlo import *
import pprint
import csv
import sys
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
pd.set_option('display.width', pd.util.terminal.get_terminal_size()[0])   # use width of terminal in use for wide displays



theCorpus = lmloCorpus("/Users/iq2/research/corpus/chant/yale-lmlo-tools/data/v2-CHNT.txt")
theCorpus.ignoreDuplicateChants()
n = 2



if n < 1: sys.exit('n must be >= 1')

theCorpus.selectMode('protus')

allNgrams = defaultdict(Counter)
stemGamut = Counter()
leafGamut = Counter()

for theChant in theCorpus.chants:
    if theChant.ignore(): continue
    for ngram in ngrams(theChant.flatLetter, n):
        if n == 1:
            stem = tuple(' ')
        else:
            stem = ngram[0:n-1]
        leaf = ngram[n-1]
        allNgrams[stem][leaf] += 1
        leafGamut[leaf] += 1
        stemGamut[stem] += 1
        
# normalize

for stem in allNgrams:
    for leaf in allNgrams[stem]:
        allNgrams[stem][leaf] /= float(stemGamut[stem])

# output csv

outfile = open('ngrams.csv', 'wb')
outputCSV = csv.writer(outfile)

# header

row = list()
row.append('stem')
row.append('count')
for leaf in sorted(leafGamut, key=sortMagicString):
    row.append("'"+leaf+"'")
outputCSV.writerow(row)

# body of table

for stem in sorted(allNgrams, key=sortMagic):
    row = list()
    row.append(stem)
    row.append(stemGamut[stem])
    for leaf in sorted(leafGamut, key=sortMagicString):
        row.append(round(allNgrams[stem][leaf], 3))
    outputCSV.writerow(row)