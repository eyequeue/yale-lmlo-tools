# provides lmlo module

import re       # module for pattern matching with Regular Expressions
import string
import os.path
import cPickle
import sys
import time

'''
TO DO:
flag and/or delete duplicate chants
flag and/or delete duplicate pitches in chants
'''

################################################################################################
# utilities for translating between LMLO scaledegrees, numeric scale degrees, and letter names #
################################################################################################

# basic gamuts

lmloGamut = '%*-0123456789>' # definitely don't change this!
sdGamut = '1234567' # probably don't change
letterGamut = 'abcdefg' # probably don't change
octaveGamut = '-=+^' # can be changed/customized

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

def sd2pc (sd, mode):
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
        self.flatSD = list()
        self.flatLetter = list()
        
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
            
                thisChant.lmloHeader = theHeader
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
                            theNote = lmloNote(sd, sd2pc(sd, theChant.mode)) 
                            theSyllable.notes.append(theNote) 
                            theChant.flatLetter.append(theNote.letter)
                            theChant.flatSD.append(theNote.sd)
                        
                        theWord.syllables.append(theSyllable)
                    theChant.words.append(theWord)
            cPickle.dump(self.chants, open(pickleFilename,'w'))
            sys.stderr.write(str(time.clock()-start) + ' secs\n')
