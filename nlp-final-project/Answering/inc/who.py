import os
from nltk.tag import StanfordNERTagger, StanfordPOSTagger
def find_who_question_answer(question, target_sentence):
	#question to sentence: 1 to 1 ratio.
    java_path = "C:/Program Files/Java/jdk1.8.0_65/bin/java.exe"
    StanfordNERTagger_pathA = 'C:/Users/Barry/Desktop/CMU/2. Second Semester/11611 NLP/project/stanford-ner-2015-04-20/classifiers/english.all.3class.distsim.crf.ser.gz'
    StanfordNERTagger_pathB = 'C:/Users/Barry/Desktop/CMU/2. Second Semester/11611 NLP/project/stanford-ner-2015-04-20/stanford-ner.jar'

    os.environ['JAVAHOME'] = java_path
    st = StanfordNERTagger(StanfordNERTagger_pathA, StanfordNERTagger_pathB)                   
    r = st.tag(target_sentence.split())

    person = ''
    for i in range(0, len(r)):
        if person != '':
            break
        if r[i][1] == 'PERSON':
            person += r[i][0] + ' '
            while (i + 1 < len(r) and r[i+1][1] == 'PERSON'):
                i += 1
                person += r[i][0] + ' '
    if person == '':
    	return "Mr.Alan Black III"

    return person

if __name__ == '__main__':
	pass