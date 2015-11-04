import argparse
from lmlo import *

parser = argparse.ArgumentParser()
parser.add_argument("mode")
parser.add_argument("depth", type=int)
parser.add_argument("countthresh", type=int)
parser.add_argument("probthresh", type=float)
parser.add_argument("representation")
args = parser.parse_args()



corpus = lmloCorpus("/Users/iq2/research/corpus/chant/yale-lmlo-tools/data/v2-CHNT.txt")
corpus.ignoreDuplicateChants()
corpus.stripDuplicatePitches()
corpus.selectMode(args.mode)

# findLicks() builds prefix and suffix trees. There are four parameters you can use. The first
# three are self-explanatory, and the fourth can be 'sd' or 'letter'.  If you set no parameters,
# the defaults are treeDepth = 20, countThreshold = 10, probThreshold = .9, representation = 'sd'

corpus.findLicks(treeDepth = args.depth, 
                 countThreshold = args.countthresh, 
                 probThreshold = args.probthresh, 
                 representation = args.representation)

# printFullSuffixTree and printFullPrefixTree dumps out the trees in the format you're used to.
# You can no longer print only rows with stars, but I'm working on a more sophisticated interface
# to the prefix/suffix trees. In the meantime, you have access to corpus.prefixTree and
# corpus.suffixTree, which have the same structure as they did in the earlier version of
# the lickfinder code.
corpus.printFullSuffixTree()