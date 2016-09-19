"""
file: SentenceAdjustment.py
author: Group Neizetze
python: 2.7.10

desc:
"""

import os, en

# Load these exactly once.
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
from nltk.parse.stanford import *

parser=StanfordParser(path_to_jar = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0.jar", path_to_models_jar = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0-models.jar", model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
dep_parser=StanfordDependencyParser(path_to_jar = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0.jar", path_to_models_jar = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0-models.jar", model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

# Change the verb to a synonym of it.
def editVerb(statement, statementParse):
    # find the verb
    head = statementParse.tree()._label

    synset = lesk(statement, head, 'v')
    if synset is None:
        return statement
    syns = synset.lemma_names()
    for syn in syns:
        syn = matchTense(syn, head)
        try:
            synbase = en.verb.present(syn.lower())
        except KeyError, e:
            break;
        try:
            headbase = en.verb.present(head.lower())
        except KeyError, e:
            break;
        if syn not in head and synbase is not headbase:
            statement = statement.replace(head, syn)
            break
    return statement

#returns a version of verb1 whose tense matches verb2
def matchTense(verb1, verb2):
    desiredTense = en.verb.tense(verb2)

    newVerb = ""
    if desiredTense == "1st singular present":    
        newVerb = en.verb.present(verb1, person = "1")
    elif desiredTense == "2nd singular present":    
        newVerb = en.verb.present(verb1, person = "2")
    elif desiredTense == "3rd signular present":
        newVerb = en.verb.present(verb1, person = "3")
    elif desiredTense == "present plural":    
        newVerb = en.verb.present(verb1, person = "*")
    elif desiredTense == "present participle":
        newVerb = en.verb.present_participle(verb1)
    elif desiredTense == "past":
        newVerb = en.verb.past(verb1)
    elif desiredTense == "1st singular past":
        newVerb = en.verb.past(verb1, person = "1")
    elif desiredTense == "2nd singular past":
        newVerb = en.verb.past(verb1, person = "2")
    elif desiredTense == "3rd signular past":
        newVerb = en.verb.past(verb1, person = "3")
    elif desiredTense == "past plural":
        newVerb = en.verb.past(verb1, person = "*")
    elif desiredTense == "past participle":
        newVerb = en.verb.past_participle(verb1)
    elif desiredTense == "infinitive":    
        newVerb = en.verb.infinitive(verb1)
    return newVerb;

