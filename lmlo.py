# provides lmlo module

import re       # module for pattern matching with Regular Expressions
import string
import os.path
import cPickle
import sys
import time
import math
import collections


'''
TO DO:
flag and/or delete duplicate chants
flag and/or delete duplicate pitches in chants
figure out what the capital letters are: beginnings/ends of units?
'''


# from http://stackoverflow.com/questions/3012421/python-lazy-property-decorator
# used for lazy evaluation of flatLetter and flatSD

class lazy_property(object):
    '''
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    '''

    def __init__(self,fget):
        self.fget = fget
        self.func_name = fget.__name__


    def __get__(self,obj,cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj,self.func_name,value)
        return value



def ngrams( inputList, n ):
    return zip(*[inputList[i:] for i in range(n)])

################################################################################################
# utilities for translating between LMLO scaledegrees, numeric scale degrees, and letter names #
################################################################################################

# basic gamuts

lmloGamut = '%*-0123456789>' # definitely don't change this!
sdGamut = '1234567' # probably don't change
letterGamut = 'abcdefg' # probably don't change
octaveGamut = '-=+^' # can be changed/customized
basicModes = ['1d','2d','3e','4e','5f','6f','7g','8g']
expBasicModes = ['1d','2d','3e','4e','5f','6f','6c','7g','8g']

def sortMagic(theTuple):
    t = theTuple[0]
    for i in range(len(octaveGamut)):
        t = t.replace(octaveGamut[i],str(i))
    return t

def sortMagicString(t):
    for i in range(len(octaveGamut)):
        t = t.replace(octaveGamut[i],str(i))
    return t

# turns an LMLO scaledegree character into a two-char octave+sd code

def lmlo2sd (lmloChar):
    i = string.find(lmloGamut, lmloChar)
    if i == -1:
        raise NameError("Can't translate lmloChar: "+lmloChar)
    sd = sdGamut[(i-4) % 7]
    octave = octaveGamut[(i+3)/7]
    return octave+sd

# turns a two-char octave+sd code into a two-char octave+letter name given a final
# (assumes that scale degree '=1' is in the '=' octave of letter names)

def sd2letter (sd, mode):
    final = string.lower(mode[1])
    if final not in letterGamut:
        raise NameError("Can't translate final: " + final)
    if len(sd) != 2 and sd[0] not in octaveGamut and sd[1] not in sdGamut:
        raise NameError("Can't translate sd: " + sd)
    i = string.find(octaveGamut, sd[0]) * 7 + \
        string.find(sdGamut, sd[1]) + \
        string.find(letterGamut, final)
    letter = letterGamut[i%7]
    octave = octaveGamut[i/7]
    return octave+letter

# NEED TO WRITE letter2sd !!!!!

def letter2number (letter):
    return letterGamut.index(letter[1]) + 7 * octaveGamut.index(letter[0])
    
l2v = dict()
l2v['-d'] = 'D'
l2v['-e'] = 'E'
l2v['-f'] = '8'
l2v['-g'] = '9'
l2v['=a'] = 'a'
l2v['=b'] = 'b'
l2v['=c'] = 'c'
l2v['=d'] = 'd'
l2v['=e'] = 'e'
l2v['=f'] = 'f'
l2v['=g'] = 'g'
l2v['+a'] = 'h'
l2v['+b'] = 'j'
l2v['+c'] = 'k'
l2v['+d'] = 'l'
l2v['+e'] = 'm'
l2v['+f'] = 'n'
l2v['+g'] = 'o'
l2v['^a'] = 'p'
l2v['^b'] = 'q'
l2v['>E'] = '5'
l2v['>S'] = '1'

v2small = dict()
v2small['-'] = '-'
v2small['D'] = 'Q'
v2small['E'] = 'R'
v2small['8'] = '('
v2small['9'] = ')'
v2small['a'] = 'A'
v2small['b'] = 'B'
v2small['c'] = 'C'
v2small['d'] = 'D'
v2small['e'] = 'E'
v2small['f'] = 'F'
v2small['g'] = 'G'
v2small['h'] = 'H'
v2small['j'] = 'J'
v2small['k'] = 'K'
v2small['l'] = 'L'
v2small['m'] = 'M'
v2small['n'] = 'N'
v2small['o'] = 'O'
v2small['p'] = 'P'
v2small['q'] = 'Q'
   
fullGenre = dict()
fullGenre['$'] = 'suffrage (usually an antiphon)'
fullGenre['A'] = 'antiphon or Agnus'
fullGenre['D'] = 'dialogue (versicle and response)'
fullGenre['E'] = 'antiphon for gospel (or monastic) canticles'
fullGenre['H'] = 'hymn'
fullGenre['I'] = 'invitatory'
fullGenre['J'] = 'alleluia at Mass'
fullGenre['K'] = 'canticle text or Kyrie'
fullGenre['Q'] = 'sequence'
fullGenre['R'] = 'responsory or gradual'
fullGenre['U'] = 'alleluia verse'
fullGenre['V'] = 'verse of responsory or gradual'
fullGenre['W'] = 'verse (not responsory or alleluia)'
fullGenre['X'] = 'doxology'
fullGenre['Z'] = 'Benedicamus Domino'
fullGenre['a'] = 'antiphon or Agnus [incipit]'
fullGenre['i'] = 'invitatory [incipit]'
fullGenre['l'] = 'lesson [incipit]'
fullGenre['r'] = 'responsory or gradual [incipit]'
fullGenre['v'] = 'verse of responsory or gradual [incipit]'

fullService = dict()
fullService['$'] = 'Memorial service or suffrage'
fullService['C'] = 'Compline'
fullService['H'] = 'Little hours'
fullService['L'] = 'Lauds'
fullService['M'] = 'Matins'
fullService['N'] = 'Nones'
fullService['P'] = 'Prime'
fullService['Q'] = 'Unknown or unidentified service'
fullService['R'] = 'Procession'
fullService['S'] = 'Sext'
fullService['T'] = 'Terce'
fullService['U'] = '[not explained by Hughes]'
fullService['V'] = 'First Vespers'
fullService['W'] = 'Second Vespers'


#####################################################################################
# hierarchy of classes: lmloCorpus > lmloChant > lmloWord > lmloSyllable > lmloNote #
#####################################################################################

class lmloNote:
    def __init__(self, sd, letter):
        self.sd = sd
        self.letter = letter

class lmloSyllable:
    def __init__(self):
        self.notes = list() # list of lmloNote instances

class lmloWord:
    def __init__(self, text = ''):
        self.text = text
        self.syllables = list() # list of lmloSyllable instances

class lmloChant:
    def __init__(self, mode):
        if len(mode) != 2 or mode[0] not in '12345678' or mode[1] not in 'abcdefgABCDEFG':
            raise NameError("Unparseable mode: " + mode)
        if mode[0] not in '12345678':
            raise NameError("Unknown mode number: " + mode[0])
        self.mode = mode
        self.words = list()
        self.ignoreMode = False
        self.ignoreDupe = False
        
    @lazy_property
    def volpiano(self):
        volpiano = '1---'
        for w in self.words:
            for s in w.syllables:
                for n in s.notes:
                    volpiano += l2v[n.letter]
                volpiano += '-'
            volpiano += '-'
        volpiano += '5'
        return volpiano


    @lazy_property
    def flatSD(self):
        print "calculating flatSD"
        flat = ['>S']
        for w in self.words:
            for s in w.syllables:
                for n in s.notes:
                    flat.append(n.sd)
        flat.append('>E')
        return flat
        
    @lazy_property
    def flatLetter(self):
        flat = ['>S']
        for w in self.words:
            for s in w.syllables:
                for n in s.notes:
                    flat.append(n.letter)
        flat.append('>E')
        return flat
        
        
        
    def ignore(self):
        return self.ignoreMode or self.ignoreDupe
        
    @lazy_property
    def fulltext(self):
        ws = ''
        for w in self.words:
            ws += w.text + ' '
        return ws[0:-1]

class lmloCorpus:
    def __init__(self, lmloFilename):

        pickleFilename = 'LMLOdata.pickle'
        if os.path.isfile(pickleFilename):
            sys.stderr.write("getting data from pickle... ")
            start = time.clock()
            self.chants = cPickle.load(open(pickleFilename, 'r'))
            sys.stderr.write(str(time.clock()-start) + ' secs\n')
        else:

            sys.stderr.write("data pickle not found, recalculating... ")
            start = time.clock()

            #######################################################
            # first pass through the LMLO data:                   #
            # * find all header lines and the chant lines we want #
            # * extract metadata from headers                     #
            # * clean up chant lines a bit                        #
            # * populate the self.chants data structure            #
            #######################################################

            f = open(lmloFilename, "r")

            lmloDataLines = list()
            for line in f:
                lmloDataLines.append(line.rstrip())   # strip off trailing newline/CR

            self.chants = list()
            theHeader = ""
            theMode = ""


            for i in range(len(lmloDataLines)):
            
                # look for new office header
                # see the documentation for the re module if you want to understand how this works
            
                matchOfficeLine = re.search('\\(X (.*?)\\)', lmloDataLines[i])
                if matchOfficeLine:
                    theOffice = matchOfficeLine.group(1)
                    continue

                # a line with '|gNN =SGN.mf' starts a new chant and includes mode information
                # see the documentation for the re module if you want to understand how this works

                matchHeaderLine = re.search('\\|g(.*?) \\=(.*?)\\.(..)',lmloDataLines[i]) # parens in the regex aren't part of the 
                                                                            # pattern to be matched but indicate parts
                                                                            # of the pattern we'll want to refer to later

                # if it's a header extract the metadata

                if matchHeaderLine:                         
                    theHeader = matchHeaderLine.group(0)      # group(0) = the whole regex (matched pattern)
                    theMode = matchHeaderLine.group(3)        # group(3) = the third paren group in the regex
                    theService = matchHeaderLine.group(2)[0]  # = first character of the second paren group in the regex
                    theGenre = matchHeaderLine.group(2)[1]    # = second character of the second paren group in the regex
                    continue                             # and now we can skip to the next line; we got what we wanted
    
                # line with '\ ' is [usually] a line of chant
                # this is [usually] the second of Hughes's four representations of each chant
                # so we've got all the words and syllables and stuff
    
                matchChantLine = re.search('^\\\\ ',lmloDataLines[i])
                if not matchChantLine: continue   # skip lines that don't start with '\ '
            
                # some chant index lines are broken up over two lines in the file, so
                # if the line doesn't contain '\()' [optionally with stuff inside the parens] 
                # then it's continued on the next line according to LMLO conventions
    
                while not re.search('\\\\\\(.*?\\)',lmloDataLines[i]):  # while makes this iterative; we keep gluing lines
                                                               # together until we match '\()' or '\(*stuff*)'
                   lmloDataLines[i] = lmloDataLines[i] + lmloDataLines.pop(i+1)    # glue this line together with the next one, which is deleted;
                   lmloDataLines.append("")                      # add a blank line at the end so the length of lmloDataLines doesn't change;
                                                        # if we don't add blanks the big loop we're in will freak out since i
                                                        # was set to iterate over the original length of lmloDataLines;
                                                        # those empty lines will be ignored b/c they aren't headers or chantlines
        
                # get rid of footnotes, which by LMLO convention have the form '(!*stuff*)'

                re.sub("\\(!.*?\\)","",lmloDataLines[i]) # what this really does is replace a footnote with an empty string
    
                # populate self.chants, a list of dicts that hold data and metadata for each chant

                try:
                    thisChant = lmloChant(theMode)
                except:
                    continue
                if theMode[0] in '1357':
                    thisChant.ambitus = 'authentic'
                elif theMode[0] in '2468':
                    thisChant.ambitus = 'plagal'
                if theMode[0] in '12':
                    thisChant.maneria = 'protus'
                elif theMode[0] in '34':
                    thisChant.maneria = 'deuterus'
                elif theMode[0] in '56':
                    thisChant.maneria = 'tritus'
                elif theMode[0] in '78':
                    thisChant.maneria = 'tetrardus'
            
                thisChant.office = theOffice
                thisChant.service = theService
                thisChant.genre = theGenre
                thisChant.index = i
                thisChant.lmloEncoding = lmloDataLines[i]
    
                self.chants.append(thisChant)

            ####################################################################
            # second pass: process each chant into words, notes, and syllables #
            ####################################################################

            for i, theChant in enumerate(self.chants):
        
            #begin borrowed chunk
                chantWords = theChant.lmloEncoding.split()[1:-1]     # each chantWordord has the form illustret.14.43454.21
                del theChant.lmloEncoding
            
                for theCWtext in chantWords:
                            
                    prevSD = ''
                    syllables = theCWtext.split('.')   # split the chantword on periods (which separate syllables in the encoding)
                    if len(syllables) == 1: continue
                    theWord = lmloWord(syllables[0])   # everything before the first . in a chantword is the text word
                
                    # now look at subsequent parts of the chantword, which are notes by syllable
                
                    for j in range(len(syllables)-1):
                
                        theSyllData = syllables[j+1]    
                        if len(theSyllData) == 0: continue

                        theSyllable = lmloSyllable()
                    
                        for c in range(len(theSyllData)):   # and now we go character by character through the syllable
                            if theSyllData[c] == '=' and prevSD != '':
                                sd = prevSD       # if we see a '=' we repeat the previous pitch
                            else:
                                try:
                                    sd = lmlo2sd(theSyllData[c])  # this throws an error if we see anything but a pitch character
                                except:
                                    #print 'possible typo in LMLO data: ' +theSyllData[c]#+' in '+ theSyllData + ' in ' + theChant.lmloMetadata['lmlo-encoding']
                                    continue   # in which case we simply ignore and skip to the next character
                            # if we're still here then sd (the current character) is a scale degree
                            theNote = lmloNote(sd, sd2letter(sd, theChant.mode)) 
                            theSyllable.notes.append(theNote) 
                        
                        theWord.syllables.append(theSyllable)
                    theChant.words.append(theWord)
                    
                # add start tokens where appropriate
                
                firstSyllable = lmloSyllable()
                firstSyllable.notes.append('>S')
                firstWord = lmloWord('>S')
                firstWord.syllables.append(firstSyllable)
                
                lastSyllable = lmloSyllable()
                lastSyllable.notes.append('>E')
                lastWord = lmloWord('>E')
                lastWord.syllables.append(lastSyllable)

            cPickle.dump(self.chants, open(pickleFilename,'w'), protocol=cPickle.HIGHEST_PROTOCOL)
            sys.stderr.write(str(time.clock()-start) + ' secs\n')

    def ignoreDuplicateChants( self, verbose = False ):
        ignored = 0
        for i, c1 in enumerate(self.chants):
            origPrinted = False
            for c2 in self.chants[i+1:]:
                if c1.flatLetter == c2.flatLetter:
                    ignored += 1
                    c2.ignoreDupe = True
        return ignored
        
    def selectMode(self, modes):
    
        self.ignored = 0
        self.retained = 0
        self.modeFilter = set()

        def filter(attr):
            for c in self.chants:
                if modes != ['all'] and getattr(c, attr) not in modes:
                    c.ignoreMode = True
                    self.ignored += 1
                else:
                    self.modeFilter.add(c.mode)
                    c.ignoreMode = False
                    if not c.ignoreDupe:     # modify this line if other ignore types are added
                        self.retained += 1
    
        if isinstance(modes, str):
            modes = [modes]
        if modes in [['protus'],['deuterus'],['tritus'],['tetrardus']]:
            filter('maneria')
        elif modes in [['authentic'],['plagal']]:
            filter('ambitus')
        else:
            filter('mode')
        print 'filter = {}, {} chants ({} ignored)'.format(modes, self.retained, self.ignored)

    def selected( self ):
    
        l = list()
        for c in self.chants:
            if not c.ignoreMode and not c.ignoreDupe:
                l.append(c)
        return l

    def stripDuplicatePitches( self ):
    
    # IS IT NECESSARY TO REMOVE PITCHES FROM WORD-BY-WORD REPRESENTATION?
    
        for c in self.chants:
            i = 0
            while i < len(c.flatLetter)-1:
                while c.flatLetter[i] == c.flatLetter[i+1]:
                    c.flatLetter.pop(i+1)
                    c.flatSD.pop(i+1)
                i += 1

    def countNotes(self): # count notes in non-ignored chants
        total = 0
        for c in self.chants:
            if c.ignore():
                continue
            for n in c.flatLetter[1:-1]:
                total += 1
        return total
        
    def countChants(self): # count non-ignored chants
        total = 0
        for c in self.chants:
            if c.ignore():
                continue
            total += 1
        return total
        

    def findLicks( self, representation, treeDepth = 20, countThreshold = 10, entropyThreshold = .9):
        
        self.suffixTree = dict()
        self.prefixTree = dict()
        self.treeDepth = treeDepth
        self.countThreshold = countThreshold
        self.entropyThreshold = entropyThreshold
        for n in range(1,self.treeDepth+1):
            self.suffixTree[n] = dict()
            self.suffixTree[n]['total'] = 0
            self.prefixTree[n] = dict()
            self.prefixTree[n]['total'] = 0

        if string.lower(representation) not in ['sd','letter']:
            raise NameError('unknown representation: ' + representation)

        self.lickModeDist = collections.defaultdict(collections.Counter)
        

        for theChant in self.chants:
        
            if theChant.ignore(): continue

            if string.lower(representation) == 'sd':
                mList = theChant.flatSD
            else:
                mList = theChant.flatLetter
            
            # Build suffix and prefix trees

            for n in range(1, self.treeDepth+1):
    
                # suffix tree
    
                for loc in range(len(mList)):
                    if loc >= (len(mList) - n + 1): break
                    ngram = tuple(mList[loc:loc+n])
                    prefix = tuple(ngram[0:-1])
                    suffix = tuple([ngram[-1]])
                    if prefix not in self.suffixTree[n]:
                        self.suffixTree[n][prefix] = dict()
                        self.suffixTree[n][prefix]['total'] = 0
                    if suffix in self.suffixTree[n][prefix]:
                        self.suffixTree[n][prefix][suffix] += 1
                    else:
                        self.suffixTree[n][prefix][suffix] = 1
                    self.suffixTree[n][prefix]['total'] += 1
            
                    self.suffixTree[n]['total'] += 1
        
                    # tally modal distribution of lick
                    
                    self.lickModeDist[ngram][theChant.mode] += 1

            
                # prefix tree

#                 for loc in range(len(mList)):
#                     if loc >= (len(mList) - n + 1): break
#                     ngram = tuple(mList[loc:loc+n])
#                     prefix = tuple([ngram[0]])
#                     suffix = tuple(ngram[1:])
#                     if suffix not in self.prefixTree[n]:
#                         self.prefixTree[n][suffix] = dict()
#                         self.prefixTree[n][suffix]['total'] = 0
#                     if prefix in self.prefixTree[n][suffix]:
#                         self.prefixTree[n][suffix][prefix] += 1
#                     else:
#                         self.prefixTree[n][suffix][prefix] = 1
#                     self.prefixTree[n][suffix]['total'] += 1
#             
#                     self.prefixTree[n]['total'] += 1
                    
                
                

    def traverseSuffixTree ( self, lick, chainLength, outputList ):

        def suffixProb ( lick ):
            n = len(lick)
            branch = self.suffixTree[n][lick[0:-1]]
#             print lick, lick[-1], branch
            return branch[(lick[-1],)] * 1. / branch['total']
        
        def suffixEntropy ( lick ):
            n = len(lick) + 1
            H = 9.99
            if n <= self.treeDepth and lick[-1] != '>E':
                H = 0.
                branch = self.suffixTree[n][lick]
                for leaf in branch:
                    if leaf == 'total': continue
                    P = branch[leaf] * 1. / branch['total']
                    H -= P * math.log(P, 2)
#                print '{:3f} {:45}  {:10}  {}'.format(H, lick[0:-1], leaf, branch)
            return H

        n = len(lick)
        theSuffixEntropy = suffixEntropy(lick)
        
        sortString = ''
        for i in reversed(lick):
            sortString += l2v[i]
            
        hashes = ''
        
        output = list()
        output.append(self.suffixTree[n][lick[0:-1]][lick[-1:]])
        for i in range(n,self.treeDepth): output.append('')
        for c in lick: output.append(c)
        output.append(theSuffixEntropy)
        if suffixProb(lick) < .5: chainLength = 0
        if theSuffixEntropy < self.entropyThreshold: 
            chainLength += 1
        if chainLength != 0 and theSuffixEntropy >= self.entropyThreshold:
            if theSuffixEntropy >= self.entropyThreshold: 
                for i in range(chainLength):
                    hashes += '#'
            chainLength = 0
        output.append(hashes)
            
        if hashes != '': 
            output.append('_'+sortString)
            
            # calculate entropy of this lick's distribution over selected modes

            # NOTE: this currently ignores any transposed or "capitalized" mode
                        
            modeEntropy = 0
            total = 0
            for m in self.modeFilter:      
                total += self.lickModeDist[lick][m]
            for m in self.modeFilter:
                p = self.lickModeDist[lick][m] * 1. / total
                if p != 0: modeEntropy -= p * math.log(p)
            output.append(modeEntropy)
            output.append(str(self.lickModeDist[lick]))
            
            outputList.append(output)
        if lick[-1] == '>E' or n+1 == self.treeDepth: return
        for suffix in sorted(self.suffixTree[n+1][lick], key=sortMagic):
            if suffix == 'total': continue
            if self.suffixTree[n+1][lick][suffix] >= self.countThreshold:
                    self.traverseSuffixTree ( lick + suffix, chainLength, outputList )

    
#     def printPartialPrefixTree ( self, lick ):
# 
#         def prefixProb ( lick ):
#             n = len(lick)
#             return self.prefixTree[n][lick[1:]][lick[0:1]] * 1. / self.prefixTree[n][lick[1:]]['total']
# 
#         n = len(lick)
#         thePrefixProb = prefixProb(lick)
#         output = ''
#         output += '{:>6d}'.format(self.prefixTree[n][lick[1:]][lick[0:1]])
#         for i in range(n,self.treeDepth+1): output += '    '
#         for c in lick: output += '{:>4}'.format(c)
#         output += '    '
#         output += '{:.2f}'.format(thePrefixProb)
#         if thePrefixProb > self.probThreshold: 
#             output += " *"
#         if output[-1]=='*': print output
#         if lick[0] == '>S' or n == self.treeDepth: return
#         for prefix in sorted(self.prefixTree[n+1][lick], key=sortMagic):
#             if prefix == 'total': continue
#             if self.prefixTree[n+1][lick][prefix] >= self.countThreshold:
#                     self.printPartialPrefixTree ( prefix + lick )
# 
#     def printFullPrefixTree (self):
#         for note in sorted(self.prefixTree[2], key=sortMagic):
#             if note == 'total': continue
#             self.printPartialPrefixTree(note)

    def listLicks (self):
        outputList = list()
        for note in sorted(self.suffixTree[2], key=sortMagic):
            if note == 'total': continue
            self.traverseSuffixTree(note, 0, outputList)
        return outputList
