"""
file: ask.py
author: Group Neizetze
python: 2.7.10

desc: the main file. takes in an article file name and a number of questions
and outputs that many questions about the article.
"""

import sys
sys.path.append('/var/nlp/spring16/teams/Nietzsche/nlp-final-project/Libraries/')

import en
from inc.ArticleParser import *
from inc.Questions import *

# Generates numQuestions questions about the article in fileName
def main(fileName, numQuestions):

    # parse the file
    article = simpleAugment(simpleIngest(fileName))

    # generate the questions
    questions = questionGen(article, numQuestions)

    # Print the best questions
    for question in questions:
        print question

# Run main()
if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))

