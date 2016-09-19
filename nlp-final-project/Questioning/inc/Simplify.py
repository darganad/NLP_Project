"""
file: Simplify.py
author: Group Neizetze
python: 2.7.10

desc:
"""

import sys,os,re,subprocess
from collections import namedtuple

inputFile = os.path.join(os.path.dirname(__file__), "RulesWorkspace/depExtraParses.txt")
outputfile = os.path.join(os.path.dirname(__file__), "RulesWorkspace/results.txt")
depExtraParse = re.compile(r'(.*)\((.*)-(.*), (.*)-(.*)\)')

Dependency = namedtuple("Dependency", "relation first second")

# takes in a sentence and output a list of simpler sentences.
def simplifySentence(article): 

    #deleting the contents of the workspace files
    with open(inputFile, 'w'): pass
    with open(outputfile, 'w'): pass

    f=open(inputFile, 'w')
    for sentence in article:
        phrases = sentence.split("CC");
        for phrase in phrases:
            f.writelines(phrase)
            f.writelines("\n")
    f.close()
    
    #http://stackoverflow.com/questions/9595983/tools-for-text-simplification-java

    curDeps = []
    sentences = []
    
    def flush():
        words = set()
        def flushHelper(cur):
            words.add(cur)
            for dep in curDeps:
                if dep.first == cur:
                    if dep.second not in words:
                        flushHelper(dep.second)
        for dep in curDeps:
            if 'nsubj' in dep.relation:
                cur = dep.first
                words.add(dep.second)
                flushHelper(cur)
                import operator
                sentence = [word[0] for word in sorted(list(words), key=lambda x: x[1])]
                sentence = " ".join(sentence)
                sentence = sentence + "."
                sentences.append(sentence)
                words = set()

    depExtraParseCommand = "java -classpath nlp-final-project/Libraries/stanford-parser-full-2015-04-20/stanford-parser.jar -mx1000m edu.stanford.nlp.parser.lexparser.LexicalizedParser -outputFormat typedDependencies nlp-final-project/Libraries/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models/englishPCFG.ser.gz %s > %s 2> /dev/null" % (inputFile, outputfile)
    subprocess.call(depExtraParseCommand, shell=True)
    f = open(outputfile)
    for line in f:
        if line.rstrip() == "":
            flush()
            curDeps = []
        else:
            matches = depExtraParse.match(line)
            def toVal(string):
                total = 0.0
                while string[-1] == '\'':
                    total *= 0.1
                    total += 0.1
                    string = string[:-1]
                total += int(string)
            curDeps.append(Dependency(relation = matches.group(1),
                                      first = (matches.group(2), toVal(matches.group(3))),
                                      second = (matches.group(4), toVal(matches.group(5))))
                          )
    # return the two longest ones
    sentences = sorted(sentences, key=lambda t: -len(t))
    return sentences[:2]

""" DEBUGGING
simplifySentence("test.txt")
simplifySentence("testChinese.txt")
"""

