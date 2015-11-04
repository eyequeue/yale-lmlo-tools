from lmlo import *

corpus = lmloCorpus("/Users/iq2/research/corpus/chant/yale-lmlo-tools/data/v2-CHNT.txt")

# CLASS HIERARCHY in bottom-up order...
#
# class lmloNote:
#         .sd 			= sd
#         .letter		= letter
# 
# class lmloSyllable:
#         .notes 		= list of lmloNote instances
# 
# class lmloWord:
#         .text 		= text of word
#         .syllables 	= list of lmloSyllable instances
# 
# class lmloChant:
#         .words 		= list of lmloWord objects (nested representation of chant)
#         .flatLetter 	= list of 2-char letter names (flat representation of chant)
#         .flatSD 		= list of 2-char SD names (flat representation of chant)
#         .fulltext()	= string containing all words (text) in the chant
#         .mode			= two-char mode encoding [taken directly from LMLO header]
#         .maneria		= 'protus', 'deuterus', etc. [calculated from mode number]
#         .ambitus		= 'plagal' or 'authentic' [calculated from mode number]
#         .index		= index number (line number within LMLO chant data file)
#         .service		= service code from LMLO header
#         .genre		= genre code from LMLO header
#         .lmloEncoding = original encoding from LMLO (second of the four encodings)
#         .lmloHeader 	= encoding of chant header from lmlo (first line of the block)
# 
# class lmloCorpus:
#         .chants 		= list of lmloChant instances

d = dict()
for c in corpus.chants:
    if c.mode in d: 
        d[c.mode] += 1
    else:
        d[c.mode] = 1
        
         


