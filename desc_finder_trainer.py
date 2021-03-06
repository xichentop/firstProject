import sys
import nltk
import codecs
import pickle

file_name = sys.argv[1]
classifier_file_name = sys.argv[2]
with open(classifier_file_name, 'wb') as out:
	def read_segments(file_name):
	    with codecs.open(file_name, "r", encoding="utf-8", errors="ignore") as f:
	        x = 0
	        text_segment = ""
	        ret = []
	        desc_set = set()
	        next_is_out_line = True
	        for line in f:
	        	if "-annot" not in line:
	        		if line.strip() == "#####":
	        			ret.append((text_segment, desc_set))
	        			text_segment = ""
	        			desc_set = set()
	        			next_is_out_line = True
	        		else:
	        			if next_is_out_line:
	        				desc_str = line.split("%%")[1].strip()
	        				desc_set = {x.strip() for x in desc_str.split(";")}
	        				next_is_out_line = False
	        			else:
	        				text_segment += line.strip() + " "

	    # return format: [(text_of_segment, set_of_description_strings)]
	    return ret

	def concat(tokens):
		string = ""
		for item in tokens:
			string += item + " "
		return string.strip()

	def find_sublist(a, suba):
		ilst = []
		for i in range(len(a)-len(suba)):
			atI = True
			for j in range(len(suba)):
				if a[i+j] != suba[j]:
					atI = False
			if atI:
				ilst.append(i)
		return ilst


	data = read_segments(file_name)

	feature_vectors = []
	desc_vocab = set()
	ind = 1
	for datum in data:
		text, desc_set = datum
		for sentence in text.split("."):
			tokens = sentence.split()
			labels = [None] * len(tokens)
			for desc in desc_set:
				desc_tokens = desc.split()
				ilst = find_sublist(tokens, desc_tokens)
				for i in ilst:
					labels[i] = "B"
					for j in range(1, len(desc_tokens)):
						labels[i + j] = "I"
			for i in range(len(labels)):
				if labels[i] == None:
					labels[i] = "O"
				feature_dict = {}
				if i < 2:
					feature_dict["i-2"] = "<s>"
					feature_dict["i-2_tag"] = "<s>"
					if i == 0:
						feature_dict["i-1"] = "<s>"
						feature_dict["i-1_tag"] = "<s>"
					else:
						feature_dict["i-1"] = tokens[i-1]
						feature_dict["i-1_tag"] = labels[i-1]
				else:
					feature_dict["i-2"] = tokens[i-2]
					feature_dict["i-2_tag"] = labels[i-2]
				feature_dict["word"] = tokens[i]
				feature_dict["location"] = i
				feature_vectors.append((feature_dict, labels[i]))
		ind += 1




















	classifier = nltk.NaiveBayesClassifier.train(feature_vectors)
	pickle.dump(classifier, out)
