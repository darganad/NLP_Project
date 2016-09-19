import re
import subprocess
import os.path
import time
import nltk

id_tracker = 0
id_to_noun = dict()
ids = []

def dashrepl(matchobj):
	global id_tracker,id_to_noun
	index = id_tracker
	id_tracker = id_tracker+1
	return ">"+id_to_noun[ids[index]]+"</NP>"


def doCoref(list_of_sentences):
	global ids
	
	fd= open("reconcile.txt","w")
	for sentence in list_of_sentences:
		fd.write(sentence+"\n")
	fd.close()
	process= subprocess.Popen(['java','-jar','reconcile-1.0.jar',"reconcile.txt"], stdout=subprocess.PIPE)
	stdout, stderr = process.communicate()
	with open('reconcile.txt.coref', 'r') as myfile:
		data = myfile.read().replace('\n', '')
	nouns = re.findall('>([^>]+)</NP>', data)
	ids = re.findall('CorefID="([0-9]+)"',data)
	ids = [int(e) for e in ids]
	tuples = zip(nouns,ids)
	for tuple in tuples:
		if tuple[1] not in id_to_noun.keys():
			id_to_noun[tuple[1]] = tuple[0]
	data= re.sub('>([^>]+)</NP>',dashrepl,data)
	data= re.sub('</NP>','',data)
	data= re.sub('<NP NO="([0-9]+)" CorefID="([0-9]+)">','',data)
	data = re.sub( r'([,.!])([a-zA-Z])', r'\1 \2',data)
	return nltk.sent_tokenize(data)
	
	
#doCoref(['Aditya is a wonderful man.','He likes to party alot.',"Bob is cool as fuck."])
#print nltk.sent_tokenize("Aditya is a wonderful manself. Aditya likes to party alot")

