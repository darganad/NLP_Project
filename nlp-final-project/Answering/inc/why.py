import os
import nltk 
import difflib
import re
import itertools
import copy
from nltk.parse.stanford import *
from nltk.tag import StanfordNERTagger, StanfordPOSTagger
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk

StanfordNERTagger_pathA = 'english.all.3class.distsim.crf.ser.gz'
StanfordNERTagger_pathB = 'stanford-ner.jar'
Stanford_model = 'stanford-parser-3.5.2-models.jar' 
Nert_3_partA = "edu/stanford/nlp/models/ner/english.all.3class.distsim.crf.ser.gz"
#'english.all.3class.distsim.crf.ser.gz'
Nert_7_partA = "edu/stanford/nlp/models/ner/english.all.3class.distsim.crf.ser.gz"
#'english.muc.7class.distsim.crf.ser.gz'

#TEMP HACKY BULLSHIT
StanfordPOSTagger_pathA = '/var/nlp/spring16/teams/Nietzsche/nlp-final-project/Libraries/stanford-postagger-2015-04-20/models/english-bidirectional-distsim.tagger'
StanfordPOSTagger_pathB = '/var/nlp/spring16/teams/Nietzsche/nlp-final-project/Libraries/stanford-postagger-2015-04-20/stanford-postagger-3.5.2.jar'

'''
StanfordPOSTagger_pathA = "edu/stanford/nlp/models/pos-tagger/english-left3words/english-left3words-distsim.tagger"
#'edu/stanford/nlp/models/english-bidirectional-distsim.tagger'
StanfordPOSTagger_pathB = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0.jar"
#'stanford-postagger-3.5.2.jar'
'''

StanfordParser_path = 'englishPCFG.ser.gz'
StanfordDependencyParser_path = 'englishPCFG.ser.gz'

os.environ["STANFORD_MODELS"] = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0-models.jar"

NERT_3= StanfordNERTagger(Nert_3_partA, os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0.jar")
NERT_7= StanfordNERTagger(Nert_7_partA, os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0.jar")
#pos = StanfordPOSTagger(StanfordPOSTagger_pathA, os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0.jar")
pos = StanfordPOSTagger(StanfordPOSTagger_pathA,StanfordPOSTagger_pathB)
#parser = StanfordParser(model_path=StanfordParser_path)
#dep_parser=StanfordDependencyParser(model_path=StanfordDependencyParser_path)

parser=StanfordParser(path_to_jar = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0.jar", path_to_models_jar = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0-models.jar", model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
dep_parser=StanfordDependencyParser(path_to_jar = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0.jar", path_to_models_jar = os.environ["CORENLP_3_6_0_PATH"] + "/stanford-corenlp-3.6.0-models.jar", model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")



pattern_uppercase = re.compile('[A-Z]{2,}[$]*')
pattern_parens = re.compile('[()]')


pattern_uppercase_v2 = re.compile('[(][A-Z]{1,}[$]*\s')
pattern_parens_v2 = re.compile('[)]')

wordnet_lemmatizer = WordNetLemmatizer()


auxillary_words = ["be","am","are","is","was","were","being","been","can","could","dare","do","does","did","have","has","had","having","may","might","must","need","ought","shall","should","will","would"]
verb_tags = ["VBZ","VB","VBG","VBD","VBN","VBP"]
noun_tags = ["NN",'NNS','NNP','NNPS']






'''
Takes as input the str of an element of a list produced by collect_ADJP_phrases
and collect_NP_phrases and strips out unecessary symbols/ parentheses/ spaces

'''


def extract_string(string):
	string = re.sub('[(], ,[)]',',',string) 
	string = re.sub('[(]-LRB- -LRB-[)]','',string)
	string = re.sub('[(]-RRB- -RRB-[)]','',string)
	string = pattern_uppercase_v2.sub('',string)
	string = pattern_parens_v2.sub('',string)
	string = re.sub('\s+', ' ',string).strip()
	string = re.sub(r'(.*) [,] (.*)',r'\1,\2',string)
	return string

'''

Attempt to find all "ADJP" phrases in the parse tree

'''


def collect_ADJP_phrases(raw_parse):
	if(raw_parse.label()=="ADJP"):
		return [raw_parse]
	else:
		try:
			a = collect_ADJP_phrases(raw_parse[0])
		except:
			a = []
		try:
			b = collect_ADJP_phrases(raw_parse[1])
		except:
			b = []
		try:
			c = collect_ADJP_phrases(raw_parse[2])
		except:
			c= []
		try:
			d= collect_ADJP_phrases(raw_parse[3])
		except:
			d= []	
		return a+b+c+d

'''

Attempt to find all "NP" phrases in the parse tree

'''


def collect_NP_phrases(raw_parse):
	if(raw_parse.label()=="NP"):
		return [raw_parse]
	else:
		try:
			a = collect_NP_phrases(raw_parse[0])
		except:
			a = []
		try:
			b = collect_NP_phrases(raw_parse[1])
		except:
			b = []
		try:
			c = collect_NP_phrases(raw_parse[2])
		except:
			c= []
		try:
			d= collect_NP_phrases(raw_parse[3])
		except:
			d= []	
		return a+b+c+d

'''

Finds the closest "phrase" that occurs after the "target word" passed in. 

I.e if the sentence is  "Aditya like reading books" and the target word passed in "reading" and
the list of phrases contains "books", then "books will be returned"

'''

def closest_phrase(string, target_word, list_of_phrases):
	target_index = string.index(target_word)
	min_diff = 10000
	closest_phrase = ''
	for phrase in list_of_phrases:
		temp_diff = string.index(phrase) - target_index
		if(temp_diff > 0 and temp_diff < min_diff):
			min_diff = temp_diff
			closest_phrase = phrase
	return closest_phrase

def closest_phrase_absolute(string,target_word,list_of_phrases):
	target_index = string.index(target_word)
	min_diff = 10000
	closest_phrase = ''
	for phrase in list_of_phrases:
		temp_diff = (string.index(phrase) - target_index)**2
		if(temp_diff < min_diff):
			min_diff = temp_diff
			closest_phrase = phrase
	return closest_phrase


'''
Attempts to answer "Why" questions based on question string and the sentence determined to most likely contain
the answer.

'''

def answerWhyQuestion(question_string,likely_sentence_string):
    try:
    	ans = likely_sentence_string.split("because")[1]
    	return ans
    except:
		likely_sentence_string_parse = (list(parser.raw(likely_sentence_string)))[0]
		adjp_in_likely_sentence_raw = collect_ADJP_phrases(likely_sentence_string_parse)
		adjp_in_likely_sentence = [extract_string(str(e)) for e in adjp_in_likely_sentence_raw]
		if(len(adjp_in_likely_sentence)>0):
			return adjp_in_likely_sentence[0]
		np_in_likely_sentence_raw = collect_NP_phrases(likely_sentence_string_parse)
		np_in_likely_sentence = [extract_string(str(e)) for e in np_in_likely_sentence_raw]
		if(len(np_in_likely_sentence)>0):
			return np_in_likely_sentence[len(np_in_likely_sentence)-1]
