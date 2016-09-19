def find_binary_question_answer(question, target_sentence):
	#question to sentence: 1 to 1 ratio.
	if 'not' in target_sentence:
		return 'No'
	else:
		return 'Yes'

if __name__ == '__main__':
	pass