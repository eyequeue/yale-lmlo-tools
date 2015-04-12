from lmlo import *

corpus = lmloCorpus("/Users/iq2/research/corpus/chant/yale-lmlo-tools/data/v2-CHNT.txt")

corpus.stripDuplicatePitches()
corpus.ignoreDuplicateChants()

# this shows you that selectMode works with a variety of different arguments

for m in ['authentic','protus','plagal','1d','2d',['1d','2d']]:
    corpus.selectMode(m)
    print "selected {}: {} chants, {} notes".format(m, corpus.countChants(), corpus.countNotes())
 
