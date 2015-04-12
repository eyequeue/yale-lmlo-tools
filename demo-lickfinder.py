from lmlo import *

corpus = lmloCorpus("/Users/iq2/research/corpus/chant/yale-lmlo-tools/data/v2-CHNT.txt")

corpus.selectMode('deuterus')

# findLicks() builds prefix and suffix trees. There are four parameters you can use. The first
# three are self-explanatory, and the fourth can be 'sd' or 'letter'.  If you set no parameters,
# the defaults are treeDepth = 20, countThreshold = 10, probThreshold = .9, representation = 'sd'
corpus.findLicks(treeDepth = 8, countThreshold = 10, probThreshold = .8, representation = 'sd')

# printFullSuffixTree and printFullPrefixTree dumps out the trees in the format you're used to.
# You can no longer print only rows with stars, but I'm working on a more sophisticated interface
# to the prefix/suffix trees. In the meantime, you have access to corpus.prefixTree and
# corpus.suffixTree, which have the same structure as they did in the earlier version of
# the lickfinder code.
corpus.printFullSuffixTree()