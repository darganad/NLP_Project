import nltk

from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser
from nltk.parse.stanford import StanfordNeuralDependencyParser
from nltk.tag.stanford import StanfordPOSTagger, StanfordNERTagger
from nltk.tokenize.stanford import StanfordTokenizer

import os, subprocess, shlex, en

dir = os.path.dirname(__file__)
DoPattern = os.path.join(dir, 'TRegexScripts/YesNoDo.txt')
DidPattern= os.path.join(dir, 'TRegexScripts/YesNoDid.txt')
DoesPattern = os.path.join(dir, 'TRegexScripts/YesNoDoes.txt')
AuxPattern = os.path.join(dir, 'TRegexScripts/YesNoAux.txt')
Patterns = [DoPattern, DidPattern, DoesPattern, AuxPattern];

inputTreeLocation = os.path.join(dir, "RulesWorkspace/results.txt")

# Generates a list of applicable Y/N questions from the list of sentences
def YesNoGeneration(conParseTrees):

    #deleting the contents of the workspace file
    with open(inputTreeLocation, 'w'): pass
    
    f=open(inputTreeLocation, 'w')
    for sentence in conParseTrees.keys():
        f.writelines(str(conParseTrees[sentence]).split('\n'))
        f.writelines("\n")
    f.close()

    Results = dict()
    #applying the yes/no tsurgeon
    for pattern in Patterns:
        proc = subprocess.Popen(['sh','nlp-final-project/Libraries/tregex/tsurgeon.sh','-treeFile', inputTreeLocation, pattern], stdout=subprocess.PIPE)
        tmp = proc.stdout.read()
        Results[pattern] = tmp

    #auxilliary verbs
    auxVerbs = set(['am', 'is', 'are', 'be', 'was', 'were', 'been',
                    'being', 'have', 'has', 'had', 'do', 'does', 'did',
                    'shall', 'will', 'should', 'would', 'might',
                    'must', 'can', 'could'])

    parseTrees = []
    #generating parse tree results after pattern application
    currentTree = ""
    for pattern in Patterns:
        for line in Results[pattern].split('\n') :
            line = line.rstrip()
            if line == "" :
                if(currentTree != ""):
                    parseTrees.append(currentTree)
                currentTree = ""
            else:
                currentTree += line+"\n"


    #filtering it out so we only have the new results
    parseTrees = set(parseTrees)
    parseTrees = map(lambda x: nltk.Tree.fromstring(x), parseTrees)
    parseTrees = map(lambda x: str(x), parseTrees)

    for sentence in conParseTrees.keys():
        tree = conParseTrees[sentence]
        if(str(tree) in parseTrees):
            parseTrees.remove(str(tree))
    parseTrees = map(lambda x: nltk.Tree.fromstring(x), parseTrees)

    import random

    FinalQuestions = [];
    #one more filter to apply "be" word transformations
    for tree in parseTrees:
        t = tree;
        #Applying verb tense change transformation
        for i in t.subtrees(filter=lambda x: x.label() == 'VERBBASE'):
            verb = i[0]
            if(verb.lower() in auxVerbs):
                doLocations = t.subtrees(filter=lambda x: x.label() == 'DO')
                for loc in doLocations:
                    loc[0] = verb;
                    i[0] = ""
            else:
                try:
                    presentVerb = en.verb.present(verb)
                except KeyError, e:
                    presentVerb = verb
                    break;
                i[0] = presentVerb

            i[0] = random.choice(["not ", ""]) + i[0]

        #t.pprint()
        words = t.leaves()
        words[0] = words[0].capitalize()
        words[len(words) - 1] = "?"
        
        question = " ".join(words)
        #have a chance to corrupt a random word
        """ DOESN'T WORK YET
        postags = nltk.pos_tag(nltk.word_tokenize(question))
        ctg = None
        repWord = None
        for word,pos in postags:
            if pos == 'NN':
                ctg = lesk(question, word)
        if ctg is not None:
            hypernyms = ctg.hypernyms()
            if len(hypernyms) > 0:
                hypernym = hypernyms[0]
                hypohypernyms = hypernym.hyponyms()
                if len(hypohypernyms) > 0:
                    replacement = hypohypernyms[0].lemmas()[0].name()
                    print "A REPLACEMENT IS HAPPENING"
                    print question
                    question = question.replace(, replacement)
                    print question
        """
        
        FinalQuestions.append(question)

    return FinalQuestions;
