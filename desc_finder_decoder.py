import sys
import pickle
import codecs

inp_file_name = sys.argv[1]
classifier_file_name = sys.argv[2]
out_file_name = sys.argv[3]
#log_file_name = sys.argv[4]

#log = open(log_file_name, "w")

def read_segments(file_name):
    with codecs.open(file_name, "r", encoding="utf-8", errors="ignore") as f:
        x = 0
        text_segment = ""
        ret_dict = {}
        ret = []
        desc_set = set()
        next_is_out_line = True
        out_line = ""
        for line in f:
        	if "-annot" in line:
        		ret_dict[line.strip()] = []
        	else:
        		if line.strip() == "#####":
        			#print("END")
        			ret.append((text_segment, out_line))
        			text_segment = ""
        			next_is_out_line = True
        		else:
        			#print("REGULAR")
        			if next_is_out_line:
        				out_line = line.strip()
        				next_is_out_line = False
        			else:
        				text_segment += " " + line.strip()

    # return format: {file: [(text_of_segment, out_line)]}
    return ret

def label_sequence(text, classifier):
	ret = []
	display = []
	indexa = 0
	for sentence in text.split("."):
		#print("\t" + str(indexa) + "/" + str(len(text.split("."))))
		#print("\t\t" + str(len(sentence.split())) + "\n")
		tokens = sentence.split()
		for i in range(len(tokens)):
			feature_dict = {}
			if i < 2:
				feature_dict["i-2"] = "<s>"
				feature_dict["i-2_tag"] = "<s>"
				if i == 0:
					feature_dict["i-1"] = "<s>"
					feature_dict["i-1_tag"] = "<s>"
				else:
					feature_dict["i-1"] = tokens[i-1]
					feature_dict["i-1_tag"] = ret[-1]
			else:
				feature_dict["i-2"] = tokens[i-2]
				feature_dict["i-2_tag"] = ret[-2]
			feature_dict["word"] = tokens[i]
			feature_dict["location"] = i

			label = classifier.classify(feature_dict)
			ret.append(label)
			display.append (tokens[i] + "/" + label)
		indexa += 1
	#log.write(str(display) + "\n\n")
	return ret

def extract_descriptions(text, tags):
	ret = set()
	i = 0
	for sentence in text.split("."):
		#print(sentence)
		phrase_str = ""
		last_label = None
		for token in sentence.split():
			if last_label == "I" or last_label == "B":
				if tags[i] != "I":
					ret.add(phrase_str)
					phrase_str = ""
			if tags[i] == "I":
				phrase_str += " " + token
			if tags[i] == "B":
				phrase_str = token
			last_label = tags[i]
			i += 1
	return ret

with open(classifier_file_name, "rb") as classifier_file:
	with open(out_file_name, "w") as out:

		classifier = pickle.load(classifier_file)
		data = read_segments(inp_file_name)
		#print(data)
		#out.write(annot + "\n")
		#log.write(annot + "\n")
		#sys.stderr.write(annot + "\n")
		index = 0
		for segment in data:
			#log.write(str(index) + "/" + str(len(data[annot])) + "\n")
			text, out_line = segment
			#print(text + "\n\n\n2@@@@@@@@@@@@@@@@@@@@@\n\n\n")
			out.write(out_line.strip() + " %%")
			#print("a")
			tags = label_sequence(text, classifier)
			#print("b")
			desc_phrases = extract_descriptions(text, tags)
			#print("c")
			for phrase in desc_phrases:
				out.write(phrase + "; ")
			#print("d")
			out.write("\n")
			out.write(text.strip() + "\n")
			out.write("#####\n")
			index += 1
