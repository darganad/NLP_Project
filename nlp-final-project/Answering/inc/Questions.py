"""
file: Questions.py
author: Group Neizetze
python: 2.7.10

desc:
dependencies: pyStatParser
wget https://github.com/emilmont/pyStatParser.git
sudo python setup.py install
"""


import sys

import nltk
#from YesNoRules import *
#from WhQuestion import *

#import en
#from SentenceAdjustment import editVerb

# Takes in a dict of {heading : paragraph} and returns a list of questions.
def articleToQuestion(article):
    questions = [];

    for heading in article.keys() :
        paragraph = article[heading];

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

# Returns the top num questions in questions.
def determineBestQuestions(questions, num):
    # NYI
    return []

"""
********************************************************************************
"""

# Generates a list of questions from a list of sentences.
def simpleQuestionGen(article):
    WhQuestions = WhGeneration(article)

    print "THIS IS WH QUESTIONS"
    for question in WhQuestions:
        print editVerb(question)

        
    print "THIS IS Y/N QUESTIONS"        
    YesNoQuestions = YesNoGeneration(article)
    for question in YesNoQuestions:
        print editVerb(question)
    #print YesNoQuestions
    return []

