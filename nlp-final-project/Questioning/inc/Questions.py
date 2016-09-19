"""
file: Questions.py
author: Group Neizetze
python: 2.7.10

desc:
"""


import sys

import nltk, en

from Grammaticality import scoreQuestion
from SentenceAdjustment import editVerb
from WhQuestion import *
from YesNoRules import *

# stanford parser stuff
dir = os.path.dirname(__file__)
inputFileLocation = os.path.join(dir, 'RulesWorkspace/WhSentences.txt')
conOutputFileLocation = os.path.join(dir, "RulesWorkspace/constituencyParses.txt")
depOutputFileLocation = os.path.join(dir, "RulesWorkspace/dependencyParses.txt")

parserLocation = 'nlp-final-project/Libraries/stanford-parser-full-2015-04-20'
conParseCommand = "java -classpath %s/stanford-parser.jar -mx1000m edu.stanford.nlp.parser.lexparser.LexicalizedParser %s/stanford-parser-3.5.2-models/englishPCFG.ser.gz %s >> %s 2> /dev/null" % (parserLocation, parserLocation, inputFileLocation, conOutputFileLocation)
depParseCommand = "java -classpath %s/stanford-parser.jar -mx1000m edu.stanford.nlp.parser.lexparser.LexicalizedParser -outputFormat conll2007 %s/stanford-parser-3.5.2-models/englishPCFG.ser.gz %s >> %s 2> /dev/null" % (parserLocation, parserLocation, inputFileLocation, depOutputFileLocation)

""" DEPRECATED
# Takes in a dict of {heading : paragraph} and returns a list of questions.
def articleToQuestion(article):
    questions = []
    for heading in article.keys() :
        paragraph = article[heading]
        for sentence in paragraph:
            new_question = rules.who_rule(sentence)
            if not (new_question == ""):
                questions.append(new_question)
            new_question = rules.has_rule(sentence)
            if not (new_question == ""):
                questions.append(new_question)
            new_question = rules.can_rule(sentence)
            if not (new_question == ""):
                questions.append(new_question)
    return questions
"""

def questionGen(article, num):
    candidates = simpleQuestionGen(article)
    #return candidates;
    return bestQuestionsOf(candidates, num)

# Returns the top num questions in questions.
def bestQuestionsOf(questions, num):
    #filter the questions asap
    pronouns = ['he', 'she', 'her', 'him', 'it', 'they', 'them', 'their']
    negations = ['not', 'never', 'no']
    def blacklist(wordList, sentence):
        for word in wordList:
            if word in sentence.lower().split(' '):
                return False
        return True
    questions = filter(lambda t: len(t.split(" ")) > 6, questions)
    questions = filter(lambda t: blacklist(pronouns, t), questions)
    #questions = filter(lambda t: blacklist(negations, t), questions)
    #http://stackoverflow.com/questions/9001509/how-can-i-sort-a-dictionary-by-key
    import collections
    d = {question:scoreQuestion(question) for question in questions}
    sortedScores = collections.OrderedDict(sorted(d.items(), key=lambda t: t[1]))
    best = []
    i = 0
    for k, v in sortedScores.iteritems():
        i += 1
        best.append(k)
        if i == num:
            break
    return best

# Generates a list of questions from a list of sentences.
def simpleQuestionGen(article):

    #deleting the contents of the workspace files
    with open(inputFileLocation, 'w'): pass
    with open(conOutputFileLocation, 'w'): pass
    with open(depOutputFileLocation, 'w'): pass

    #writing the article to a file for the shell scripts to use
    f=open(inputFileLocation, 'w')
    for sentence in article:
        phrases = sentence.split("CC");
        for phrase in phrases:
            f.writelines(phrase)
            f.writelines("\n")
    f.close()


    #splitting things into phrases based on CC


    #Generating the dependency parse once
    subprocess.call(depParseCommand, shell=True)
    depParses = dict()
    currentParse = ""
    i = 0;
    f = open(depOutputFileLocation)
    for line in f :
        if line.decode('ascii', 'ignore').rstrip() == "" :
            if(currentParse != ""):
                #make sure that the sentence is actually machine readable
                try:
                    article[i] = article[i].decode('utf8')
                    currentParse = currentParse.decode('utf8')
                except:
                    i+=1;
                    currentParse = ""
                    continue;
                depParse = DependencyGraph(currentParse, top_relation_label='root')
                try:
                    newArticle = editVerb(article[i], depParse)
                except KeyError, e:
                    newArticle = article[i]
                article[i] = newArticle

                depParses[article[i]] = depParse;
                i+=1;
            currentParse = ""
        else:
            currentParse += line
    f.close();

    #Generating the constituency parse once
    subprocess.call(conParseCommand, shell=True)
    conParseTrees = dict()
    currentTree = ""
    i = 0;
    f = open(conOutputFileLocation)
    for line in f :
        line = line.decode('ascii', 'ignore').rstrip()
        if line == "" :
            if(currentTree != ""):
                #make sure that the sentence is actually machine readable
                try:
                    article[i] = article[i].decode('utf8')
                    currentTree = currentTree.decode('utf8')
                except:
                    i+=1;
                    currentTree = ""
                    continue;
		#generating the dependency parse
		conParseTrees[article[i]] = nltk.ParentedTree.fromstring(currentTree)		
                i+=1;
            currentTree = ""
        else:
            currentTree += line
    f.close();


    questions = []
    for question in WhGeneration(conParseTrees, depParses):
        questions.append(question)
    for question in YesNoGeneration(conParseTrees):
        questions.append(question)
        
    ''' DEBUGGING
    for sentence in conParseTrees.keys():
        print sentence
        conTree = conParseTrees[sentence];
        #depTree = depParseTrees[sentence];
        print conTree.pretty_print();
        print depTree.pretty_print();
    '''
    
    return questions

