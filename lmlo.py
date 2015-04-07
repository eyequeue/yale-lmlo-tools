# provides lmlo module

import re       # module for pattern matching with Regular Expressions
import csv      # module for writing CSV files (can be read in excel)
import random   # module for generating random numbers
import math
import sys
import pprint
import string


########################################################
# CHANGE THIS TO POINT TO THE LMLO DATA ON YOUR SYSTEM #
########################################################

lmloFile = "/Users/iq2/research/corpus/chant/lmlo/data/v2-CHNT.txt"

#########################################
# options for setting search parameters #
#########################################


def sortMagic(theTuple):
    t = theTuple[0]
    t = t.replace('-','1')
    t = t.replace(' ','2')
    t = t.replace('+','3')
    return t

lmloGamut = '%*-0123456789>'
sdGamut = '1234567'
letterGamut = 'abcdefg'
octaveGamut = '-=+^'

def lmlo2sd (lmloChar):
    i = string.find(lmloGamut, lmloChar)
    if i == -1:
        raise NameError("Can't translate lmloChar: "+lmloChar)
    sd = sdGamut[(i-4) % 7]
    octave = octaveGamut[(i+3)/7]
    return octave+sd

def sd2pc (sd, final):
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

for f in ['c','d','e','f','g']:
    for sd in lmloGamut:
        print f, lmlo2sd(sd), sd2pc(lmlo2sd(sd), f)
    
sys.exit()

# dict of dicts for translating SDs to PCs
sd2pc = { 
    'c': {
            '-4' : '-f',
            '-5' : '-g',
            '-6' : '=a',
            '-7' : '=b',
            ' 1' : '=c',
            ' 2' : '=d',
            ' 3' : '=e',
            ' 4' : '=f',
            ' 5' : '=g',
            ' 6' : '+a',
            ' 7' : '+b',
            '+1' : '+c',
            '+2' : '+d',
            '+3' : '+e'
        },
    'd': {
            '-4' : '-g',
            '-5' : '=a',
            '-6' : '=b',
            '-7' : '=c',
            ' 1' : '=d',
            ' 2' : '=e',
            ' 3' : '=f',
            ' 4' : '=g',
            ' 5' : '+a',
            ' 6' : '+b',
            ' 7' : '+c',
            '+1' : '+d',
            '+2' : '+e',
            '+3' : '+f'
        },
    'e': {
            '-4' : ' a',
            '-5' : ' b',
            '-6' : ' c',
            '-7' : ' d',
            ' 1' : ' e',
            ' 2' : ' f',
            ' 3' : ' g',
            ' 4' : '+a',
            ' 5' : '+b',
            ' 6' : '+c',
            ' 7' : '+d',
            '+1' : '+e',
            '+2' : '+f',
            '+3' : '+g'
        },
    'f': {
            '-4' : ' b',
            '-5' : ' c',
            '-6' : ' d',
            '-7' : ' e',
            ' 1' : ' f',
            ' 2' : ' g',
            ' 3' : '+a',
            ' 4' : '+b',
            ' 5' : '+c',
            ' 6' : '+d',
            ' 7' : '+e',
            '+1' : '+f',
            '+2' : '+g',
            '+3' : '++a'
        },
    'g': {
            '-4' : ' c',
            '-5' : ' d',
            '-6' : ' e',
            '-7' : ' f',
            ' 1' : ' g',
            ' 2' : '+a',
            ' 3' : '+b',
            ' 4' : '+c',
            ' 5' : '+d',
            ' 6' : '+e',
            ' 7' : '+f',
            '+1' : '+g',
            '+2' : '++a',
            '+3' : '++b'
        }}


# translate from letter names to numbers
pc2int = {       
    'd' : 0,
    'e' : 1,
    'f' : 2,
    'g' : 3,
    'a' : 4,
    'b' : 5,
    'c' : 6
}

# the reverse of pc2int
int2pc = ['d', 'e','f', 'g', 'a', 'b', 'c']  

# any chant in a mode other than the ones on this list is thrown out
basicmodes = ['1d', '2d', '3e', '4e', '5f', '6f', '7g', '8g']
    
# translate mode number to maneria
maneria = {
    '1' : 'protus',
    '2' : 'protus',
    '3' : 'deuterus',
    '4' : 'deuterus',
    '5' : 'tritus',
    '6' : 'tritus',
    '7' : 'tetrardus',
    '8' : 'tetrardus'
}    

# translate mode number to ambitus
ambitus = {
    '1' : 'authentic',
    '2' : 'plagal',
    '3' : 'authentic',
    '4' : 'plagal',
    '5' : 'authentic',
    '6' : 'plagal',
    '7' : 'authentic',
    '8' : 'plagal'
}    


######################
# open all the files #
######################



f = open(lmloFile, "r")

LMLO = list()
for line in f:
    LMLO.append(line.rstrip())   # strip off trailing newline/CR

#######################################################
# first pass through the LMLO data:                   #
# * find all header lines and the chant lines we want #
# * extract metadata from headers                     #
# * clean up chant lines a bit                        #
# * populate the chantLines data structure            #
#######################################################

chantLines = list()
theHeader = ""
theMode = ""


for i in range(len(LMLO)):

    # a line with '|gNN =SGN.mf' starts a new chant and includes mode information
    # see the documentation for the re module if you want to understand how this works

    matchHeaderLine = re.search('\\|g(.*?) \\=(.*?)\\.(..)',LMLO[i]) # parens in the regex aren't part of the 
                                                                # pattern to be matched but indicate parts
                                                                # of the pattern we'll want to refer to later

    # if it's a header extract the metadata

    if matchHeaderLine:                         
        theHeader = matchHeaderLine.group(0)      # group(0) = the whole regex (matched pattern)
        theMode = matchHeaderLine.group(3)        # group(3) = the third paren group in the regex
        theService = matchHeaderLine.group(2)[0]  # = first character of the second paren group in the regex
        theGenre = matchHeaderLine.group(2)[1]    # = second character of the second paren group in the regex
        continue                             # and now we can skip to the next line; we got what we wanted
    
    # if the most recent header sets a mode that isn't in basicmodes, skip this line
    # (effectively, keep skipping until the next header that changes modes to a basicmode)

    if theMode not in searchModes: continue   
    
    # line with '\ ' is [usually] a line of chant
    # this is [usually] the second of Hughes's four representations of each chant
    # so we've got all the words and syllables and stuff
    # (this is a change from what I've been saying in class)
    
    matchChantLine = re.search('\\\\ ',LMLO[i])
    if not matchChantLine: continue   # skip lines that don't start with '\ '
    
    # some chant index lines are broken up over two lines in the file, so
    # if the line doesn't contain '\()' [optionally with stuff inside the parens] 
    # then it's continued on the next line according to LMLO conventions
    
    while not re.search('\\\\\\(.*?\\)',LMLO[i]):  # while makes this iterative; we keep gluing lines
                                                   # together until we match '\()' or '\(*stuff*)'
       LMLO[i] = LMLO[i] + LMLO.pop(i+1)    # glue this line together with the next one, which is deleted;
       LMLO.append("")                      # add a blank line at the end so the length of LMLO doesn't change;
                                            # if we don't add blanks the big loop we're in will freak out since i
                                            # was set to iterate over the original length of LMLO;
                                            # those empty lines will be ignored b/c they aren't headers or chantlines
        
    # get rid of footnotes, which by LMLO convention have the form '(!*stuff*)'

    re.sub("\\(!.*?\\)","",LMLO[i]) # what this really does is replace a footnote with an empty string
    
    # populate chantLines, a list of dicts that hold data and metadata for each chant
    
    thisChant = dict()
    thisChant['header'] = theHeader
    thisChant['mode'] = theMode
    thisChant['service'] = theService
    thisChant['genre'] = theGenre
    thisChant['data'] = LMLO[i]
    thisChant['i'] = i
    thisChant['random'] = random.random()
    
    chantLines.append(thisChant)




########################
########################
####second iteration:###
########################
########################

#get ngrams


dupes = 0           #running counter of duplicate chants

suffixTree = dict()
prefixTree = dict()
for n in range(1,treeDepth+1):
    suffixTree[n] = dict()
    suffixTree[n]['total'] = 0
    prefixTree[n] = dict()
    prefixTree[n]['total'] = 0


allChants = []  # this will be a duplicate-free list of chants

for chant in chantLines:
    mList = [] # will contain letter names of notes

#begin borrowed chunk
    i = chant['i']
    chantWords = LMLO[i].split()[1:-1]     # split() turns a string into a list of words
    theMode = chant['mode']

    theGenre = chant['genre']
    for theCW in chantWords:
        prevSD = ''
        syllables = theCW.split('.')   # split the chantword on periods (which separate syllables in the encoding)
        word = syllables[0]                   # everything before the first . in a chantword is the word
        for j in range(len(syllables)-1):
            theSyll = syllables[j+1]    # now look at subsequent parts of the chantword, which are notes by syllable
            for c in range(len(theSyll)):   # and now we go character by character through the syllable
                if theSyll[c] == '=' and prevSD != '':
                    sd = prevSD       # if we see a '=' we repeat the previous pitch
                else:
                    try:
                        sd = lmlo2sd[theSyll[c]]  # this throws an error if we see anything but a pitch character
                    except:
                        continue   # in which case we simply ignore and skip to the next character
                
                # if we're still here then the current character is a scale degree
                
                #add the current pc to mList (as a letter name)
                if useLetterNamesInsteadOfSDs:
                    mList.append(sd2pc[theMode[-1]][sd])
                else:
                    mList.append(sd)


    i = 0

    # prune duplicate pitches

    while i < len(mList)-1:
        while i < len(mList)-1 and mList[i] == mList[i+1]:
            mList.pop(i)
        i += 1
    
    # add start and end tokens

    mList.insert(0, '>S')
    mList.append('>E')

    # print the whole chant

#     s = ""
#     for c in mList:
#         s += c
#     print theMode, theGenre, s

    #check to see if this is a duplicate chant. If it is, increase the total tally of duplicates and move on to the next. otherwise, add it to the total list of all chants
    if mList in allChants:
        dupes += 1
        continue
    else:
        allChants.append(mList)
#         if chant['random'] < 0.8:
#             trainingChants.append(mList)
#         else:
#             testChants.append(mList)
#             continue

matchSequence = [' d', ' f', ' d', ' c', ' f', ' g', '+a']
for mList in allChants:
    n = len(matchSequence)
    for nn in range(n-1,n+2):
        for pos in range(len(mList)-nn):
            ngram = mList[pos:pos+nn+1] 
            print fuzz.ratio(matchSequence, ngram), ngram
