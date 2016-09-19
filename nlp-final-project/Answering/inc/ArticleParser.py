"""
file: ArticleParser.py
author: Group Neizetze
python: 2.7.10

desc: Parses the article to create a python representation to manipulate.
dependencies: tokenizers/punkt/english.pickle
              download nltk, then run nltk.download() -> d -> punkt
"""

import sys
import nltk

# Returns a dictionary of {heading : paragraph} where a paragraph is a list of
# sentences in fileName.
def ingest(fileName):
    articleFile = open(fileName)

    article = dict();
    currentHeading = "";
    previousSentence = "";

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    for paragraph in articleFile :
        paragraph = paragraph.decode('utf8').rstrip()
        sentences = tokenizer.tokenize(paragraph);

        if(len(sentences) == 1 and not(paragraph == "") and previousSentence == ""):
            currentHeading = paragraph
            article[currentHeading] = [];
        elif(not(currentHeading == "")):
            for sentence in sentences:
                if(not (sentence == "")):
                    article[currentHeading].append(sentence)

        previousSentence = paragraph;

    articleFile.close()
    return article

def augment(paragraph):
    # spooky. augment the sentences of the paragraph.
    return paragraph

"""
********************************************************************************
"""

# JUST FOR TESTING. return a list of the sentneces
def simpleIngest(fileName):
    articleFile = open(fileName)
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = []
    for paragraph in articleFile:
        news = tokenizer.tokenize(paragraph.decode('utf8').rstrip())
        if len(news) == 0 or news[0][-1:] != '.':
            continue
        sentences += news
    return sentences
