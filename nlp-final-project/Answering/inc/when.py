import os
import nltk
from nltk.tag import StanfordNERTagger, StanfordPOSTagger
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn

def supersense(sentence, word):
    cur = lesk(sentence, word, 'n')
    if cur is None:
        return  None
    else:
        return cur.lexname()

def find_when_question_answer(question, target_sentence):
	
    time = ''
    words = target_sentence.split(' ')
    for word in words:
        #print word
        tmp = str(supersense(target_sentence, word)).split('.')

        if len(tmp) > 1:
            tag = tmp[1]
            if tag == 'time':
                time += word + ' '
    
    return time

if __name__ == '__main__':
	pass
