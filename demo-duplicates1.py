from lmlo import *

corpus = lmloCorpus("/Users/iq2/research/corpus/chant/yale-lmlo-tools/data/v2-CHNT.txt")

# show the results of ignoring duplicate chants, then stripping duplicate pitches, then ignoring duplicate chants again

corpus.selectMode('1d')

# the selectMode() function will also accept a list of modes, a maneria, or an ambitus
# examples:

# corpus.selectMode(['1d','2d'])
# corpus.selectMode('protus')
# corpus.selectMode('plagal')

print "{} chants, {} notes".format(corpus.countChants(), corpus.countNotes())

corpus.ignoreDuplicateChants() # here duplicate chants are chants with the same pitch sequence
print "{} chants, {} notes".format(corpus.countChants(), corpus.countNotes())

corpus.stripDuplicatePitches()
print "{} chants, {} notes".format(corpus.countChants(), corpus.countNotes())

corpus.ignoreDuplicateChants() # this will ignore a few more chants because we've stripped duplicate pitches
print "{} chants, {} notes".format(corpus.countChants(), corpus.countNotes())
