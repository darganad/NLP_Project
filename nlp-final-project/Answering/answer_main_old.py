"""
file: answer_main.py
author: Group Neizetze
python: 2.7.10

desc:
"""

import sys
import re

from fuzzywuzzy import fuzz
import inc.binary
import inc.what
import inc.who
import inc.where
import reconcile
from nltk import tokenize

def find_the_answer(array_of_questions, array_of_target_sentences):
    # |array_of_questions| <= |array_of_target_sentences|
    # Classify the questions ---. what, where, who, how, why, binary
    binary_question_keywords = ["be","am","are","is","was","were","being","been","can","could",
    "dare","do","does","did","have","has","had","having","may","might","must","need","ought","shall","should","will","would"]
    # wh_question_keywords = ['who','where','what','when','how','why','which']
    wh_question_keywords = ['who','where','what']

    # As long as the question contains a wh word, it is classified as a WH-question
    
    array_of_answers = []
    for i in range(0, len(array_of_questions)):
        question =  array_of_questions[i]
        target_sentence = array_of_target_sentences[i]

        answer = ''
        for wh_word in wh_question_keywords:
            if wh_word in question:
                if wh_word == 'what':
                    answer = inc.what.answerWhatQuestion(question, target_sentence)
                    array_of_answers.append(answer)
                    break

                elif wh_word == 'who':
                    answer = inc.who.find_who_question_answer(question, target_sentence)
                    array_of_answers.append(answer)
                    break

                elif wh_word == 'where':
                    answer = inc.where.find_where_question_answer(question, target_sentence)
                    array_of_answers.append(answer)
                    pass

                #elif wh_word == 'when':
                    ###
                #elif wh_word == 'why':
                    ###
                #elif wh_word == 'which':
                    
        
        # It is a binary question
        #answer = inc.binary.find_binary_question_answer(question, target_sentence)
        #array_of_answers.append(answer)
    #answer = inc.where.find_where_question_answer(question, target_sentence)
    #answer = inc.what.answerWhatQuestion(question, target_sentence)
    #print answer
    #answer = inc.what.answerWhatQuestion(question, target_sentence)
    #print answer

    print "HERE ARE THE FINAL ANSWERS"
    for answer in array_of_answers:
        print answer
    
    


def main(fileName, numQuestions):
    f_fileName = open(fileName,'r')
    # Filter out some characters that cannot be printed in the console
    f_fileName_read = f_fileName.read()
    
    raw_file = f_fileName_read.lower().decode('ascii','ignore')
    raw_file2 =f_fileName_read.decode('ascii','ignore')
    #raw_file = (f_fileName.read()).lower().decode('ascii', 'ignore')
    
    f_numQuestions = open(numQuestions, 'r')
    raw_question = (f_numQuestions.read()).lower().decode('ascii', 'ignore').split('\n')
    
    # Store all the questions in the txt file into a list
    array_of_questions = []
    for item in raw_question:
        array_of_questions.append(item)
    
    content = tokenize.sent_tokenize(raw_file)
    for i,s in enumerate(content):
        content[i] = re.sub(r'([A-Za-z0-9 ]+\s{2,})','',s)
       # content[i] = re.sub(r'\s+',' ',s)

    #for sentence in content:
       # print sentence
       # sentence = re.sub(r'([A-Za-z0-9 ]+ \s{2,})','',sentence)
       # sentence = re.sub(r'\s+',' ',sentence)
       # print sentence
    #content = reconcile.doCoref(tokenize.sent_tokenize(raw_file2))
    
    # We assume that target sentence contaisn the answer we're looking for
    # Find the target sentences and store them into a list
    array_of_target_sentences = []
    for question in array_of_questions:
        fuzz_ratio = 0
        target_sentence = ''
        for item in content:
            tmp_fuzz_ratio = fuzz.partial_ratio(question,item)
            if (tmp_fuzz_ratio > fuzz_ratio):
                fuzz_ratio = tmp_fuzz_ratio
                target_sentence = item
        array_of_target_sentences.append(target_sentence)        

    '''
    There is a better way to implement this part:
    create a dictionary and map a question to multiple target sentences.

    ''' 

    array_of_answers = []
    array_of_answers = find_the_answer(array_of_questions, array_of_target_sentences)

# Run main() when it is directly run by the terminal
if __name__ == '__main__':
    fileName = sys.argv[1]
    numQuestions = sys.argv[2]
    main(fileName, numQuestions)

