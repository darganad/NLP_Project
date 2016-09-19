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
1) "What does Aditya like to read?" (sentence ends with a verb) -> find NP in answer sentence closest to verb in sentence

'''

def caseA(question_string_pos_tagged,noun_phrases_in_question,likely_sentence_string,likely_sentence_string_pos_tagged,noun_phrases_in_likely_sentence):
	if(question_string_pos_tagged[len(question_string_pos_tagged)-2][1] in verb_tags):
		question_has_verb_at_end = True
	else:
		question_has_verb_at_end = False
	if question_has_verb_at_end:
		verb_at_end_of_question = question_string_pos_tagged[len(question_string_pos_tagged)-2][0]
		verbs_in_likely_sentence = [elem[0] for elem in likely_sentence_string_pos_tagged if elem[1] in verb_tags]
		target_verb = ''
		for verb in verbs_in_likely_sentence:
			if(wordnet_lemmatizer.lemmatize(verb,'v') == wordnet_lemmatizer.lemmatize(verb_at_end_of_question,'v')):
				target_verb = verb
		if(target_verb==''):
			return noun_phrases_in_likely_sentence[0]
		answer = closest_phrase(likely_sentence_string,target_verb, noun_phrases_in_likely_sentence)
		return answer
	else:
		return None

'''
2) "What is the language of Singapore"? (auxillary verb is second word and question has one NP) -> match NP in answer sentence and try to find ADJP next to
	matched NP. if no ADJP present then return closest NP in answer sentence

'''


def caseB(question_string_tokenized,noun_phrases_in_question,noun_phrases_in_likely_sentence,likely_sentence_string):
	if(question_string_tokenized[1] in auxillary_words and len(noun_phrases_in_question)==1):
		np_found_in_likely_sentence_index = -1
		for x in xrange(len(noun_phrases_in_likely_sentence)):
			if(noun_phrases_in_likely_sentence[x].lower()==noun_phrases_in_question[0].lower()):
				np_found_in_likely_sentence_index = x
		if(np_found_in_likely_sentence_index==-1):
			return None
		get_ADJP_phrases_in_likely_sentence = collect_ADJP_phrases((list(parser.raw_parse(likely_sentence_string)))[0])
		ADJP_phrases_in_likely_sentence = [extract_string(str(e)) for e in get_ADJP_phrases_in_likely_sentence]
		if(len(ADJP_phrases_in_likely_sentence)>0):
			answer = closest_phrase(likely_sentence_string,noun_phrases_in_likely_sentence[np_found_in_likely_sentence_index],ADJP_phrases_in_likely_sentence)
		else:
			target_phrase = noun_phrases_in_likely_sentence[np_found_in_likely_sentence_index]
			noun_phrases_in_likely_sentence.remove(noun_phrases_in_likely_sentence[np_found_in_likely_sentence_index])
			answer = closest_phrase(likely_sentence_string,target_phrase,noun_phrases_in_likely_sentence)
		return answer
	else:
		return None 
'''
3) "What NOUN ....?" Tag second word using super sense (if its a noun) Find same super sense in likely sentence. If more than one match return the super sense
closest to the first NP in likely sentence

'''

def caseC(question_string,question_string_pos_tagged,noun_phrases_in_question,likely_sentence_string,likely_sentence_string_tokenized,noun_phrases_in_likely_sentence):
	second_word_in_question_tag = question_string_pos_tagged[1][1]
	if(second_word_in_question_tag in noun_tags):
		second_word_in_question_supersense = lesk(question_string,question_string_pos_tagged[1][0],'n')
		second_word_in_question_supersense = second_word_in_question_supersense.lexname()
		super_sense_matches_in_likely_sentence = []
		for word in likely_sentence_string_tokenized:
			temp_supersense = lesk(likely_sentence_string,word,'n')
			if(temp_supersense is None):
				continue 
			temp_supersense = temp_supersense.lexname()
			if(temp_supersense==second_word_in_question_supersense):
				super_sense_matches_in_likely_sentence.append(word)
		if(len(super_sense_matches_in_likely_sentence)==1):
			return super_sense_matches_in_likely_sentence[0]
		if(len(super_sense_matches_in_likely_sentence)>1):
			first_np_in_likely_sentence = noun_phrases_in_likely_sentence[0]
			answer = closest_phrase_absolute(likely_sentence_string,first_np_in_likely_sentence,super_sense_matches_in_likely_sentence)
			return answer
		return None	
	else:
		return None
'''
4) "What VERB ....?" (second word is a verb) -> find NP in answer sentence closest to this verb

'''
def caseD(question_string_pos_tagged,noun_phrases_in_question,likely_sentence_string,likely_sentence_string_pos_tagged,noun_phrases_in_likely_sentence):
	if(question_string_pos_tagged[1][1] in verb_tags):
		question_second_word_is_verb = True
	else:
		question_second_word_is_verb= False
	if(question_second_word_is_verb):
		second_verb_question = question_string_pos_tagged[1][0]
		verbs_in_likely_sentence = [elem[0] for elem in likely_sentence_string_pos_tagged if elem[1] in verb_tags]
		target_verb = ''
		for verb in verbs_in_likely_sentence:
			if(wordnet_lemmatizer.lemmatize(verb,'v') == wordnet_lemmatizer.lemmatize(second_verb_question,'v')):
				target_verb = verb
		if(target_verb==''):
			return noun_phrases_in_likely_sentence[0]
		answer = closest_phrase(likely_sentence_string,target_verb, noun_phrases_in_likely_sentence)
		return answer
	else:
		return None






'''
Attempts to answer "What" questions based on question string and the sentence determined to most likely contain
the answer.

'''

def answerWhatQuestion(question_string,likely_sentence_string):
	question_string_tokenized = nltk.word_tokenize(question_string)
	likely_sentence_string_tokenized = nltk.word_tokenize(likely_sentence_string)

	question_string_pos_tagged =  pos.tag(question_string_tokenized)
	get_noun_phrases_in_question_raw = collect_NP_phrases((list(parser.raw_parse(question_string)))[0])
	noun_phrases_in_question = [extract_string(str(e)) for e in get_noun_phrases_in_question_raw]

	likely_sentence_string_pos_tagged = pos.tag(likely_sentence_string_tokenized)
	get_noun_phrases_in_likely_sentence_raw = collect_NP_phrases((list(parser.raw_parse(likely_sentence_string)))[0])
	noun_phrases_in_likely_sentence = [extract_string(str(e)) for e in get_noun_phrases_in_likely_sentence_raw]


	answer = None
	answer = caseA(question_string_pos_tagged,noun_phrases_in_question,likely_sentence_string,likely_sentence_string_pos_tagged,noun_phrases_in_likely_sentence)
	if(answer):
		return answer
	answer = caseB(question_string_tokenized,noun_phrases_in_question,copy.deepcopy(noun_phrases_in_likely_sentence),likely_sentence_string)
	if(answer):
		return answer
	answer = caseC(question_string,question_string_pos_tagged,noun_phrases_in_question,likely_sentence_string,likely_sentence_string_tokenized,noun_phrases_in_likely_sentence)
	if(answer):
		return answer
	answer = caseD(question_string_pos_tagged,noun_phrases_in_question,likely_sentence_string,likely_sentence_string_pos_tagged,noun_phrases_in_likely_sentence)
	if(answer):
		return answer


	'''
	add 4 more rules

	'''
