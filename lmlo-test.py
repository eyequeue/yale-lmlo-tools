from lmlo import *

corpus = lmloCorpus("/Users/iq2/research/corpus/chant/yale-lmlo-tools/data/v2-CHNT.txt")

# CLASS HIERARCHY in bottom-up order...
#
# class lmloNote:
#         self.sd = sd
#         self.letter = letter
# 
# class lmloSyllable:
#         self.notes = list of lmloNote instances
# 
# class lmloWord:
#         self.text = text of word
#         self.syllables = list of lmloSyllable instances
# 
# class lmloChant:
#         self.words = list of lmloWord objects (nested representation of chant)
#         self.flatLetter = list of 2-char letter names (flat representation of chant)
#         self.flatSD = list of 2-char SD names (flat representation of chant)
#         self.fulltext() = string containing all words (text) in the chant
#         self.mode = two-char mode encoding [taken directly from LMLO header]
#         self.maneria = 'protus', 'deuterus', etc. [calculated from mode number]
#         self.ambitus = 'plagal' or 'authentic' [calculated from mode number]
#         self.index = index number (assigned by this module, not by LMLO)
#         self.service = service code from LMLO header
#         self.genre = genre code from LMLO header
#         self.lmloEncoding = original encoding from LMLO (second of the four encodings)
#         self.lmloHeader = encoding of chant header from lmlo (first line of the block)
# 
# class lmloCorpus:
#         self.chants = list of lmloChant instances

for c in corpus.chants:
    print c.fulltext()