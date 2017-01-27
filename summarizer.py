import sys
import nltk

def is_similar_to(str1, str2):
	avg_len = (len(str1) + len(str2)) / 2
	return nltk.edit_distance(str1, str2) <= avg_len / 5

def compute_scores(similarity_map, key, total_douts):
	info_list = similarity_map[key]
	appearances = len(info_list)
	appearance_score = appearances / total_douts

	all_zeroes = True
	score_sum = 0.0
	ranked_total = 0

	for dout_info in info_list:
		rank = dout_info["rank"]
		total = dout_info["total"]
		if rank != 0:
			all_zeroes = False
			ranked_total += 1
			score_sum += (total - rank) / total
	ranking_score = 0.5
	if not all_zeroes:
		ranking_score = score_sum / ranked_total

	total_score = (appearance_score + ranking_score) / 2

	return (appearance_score, ranking_score, total_score)


file_list_name = sys.argv[1]
summary_name = sys.argv[2]
with open(summary_name, "w") as summary_out:
	with open(file_list_name) as file_list:
		dout_lines = []
		total_douts = 0
		for file_name in file_list:
			file_name = file_name.strip()
			with open(file_name) as dout:
				i = 0
				for dout_line in dout:
					dout_line = dout_line.strip()
					if dout_line != "":
						pieces = dout_line.split('\t')
						rank = int(dout_line.split("##")[0].strip().split()[0])
						name = dout_line.split("##")[0].strip().split(maxsplit=1)[1]
						category = dout_line.split("##")[1].split("%%")[0].strip()
						descriptions = [x.strip() for x in dout_line.split("%%")[1].strip().split(";")]
						i+=1
						dout_lines.append({"dout": file_name[:-4], "name": name, "rank": rank, "category": category, "descriptions": descriptions})
				total_douts += 1
				for j in range(i):
					dout_lines[len(dout_lines)-1-j]["total"] = i
		similarity_map = {}
		for dout_info in dout_lines:
			added_to_map = False
			for key in similarity_map:
				if is_similar_to(key, dout_info["name"]):
					similarity_map[key].append(dout_info)
					added_to_map = True
					break
			if not added_to_map:
				similarity_map[dout_info["name"]] = [dout_info]

		score_map = {}
		for key in similarity_map:
			#scores: (appearancescore, rankingscore, totalscore)
			scores = compute_scores(similarity_map, key, total_douts)
			if scores[2] not in score_map:
				score_map[scores[2]] = ([])
			score_map[scores[2]].append((scores, key))

		prev_score = 1.1
		cur_ranking = 1
		i = 1
		for score in sorted(score_map, reverse=True):
			if score != prev_score:
				cur_ranking = i
			for scores, key in score_map[score]:
				summary_out.write((str(cur_ranking) + "\t" + key + "\t{:0.2f}\t{:0.2f}\t{:0.2f}\n").format(scores[0], scores[1], scores[2]))
				for dout_info in similarity_map[key]:
					summary_out.write("%"+ dout_info["dout"].split("/")[-1] +" " + str(dout_info["rank"]) + "/" + str(dout_info["total"]))
					summary_out.write("\t" + dout_info["name"] + "\t##" + dout_info["category"] + "\t%%")
					for j in range(len(dout_info["descriptions"])-1):
						summary_out.write(dout_info["descriptions"][j] + "; ")
					if len(dout_info["descriptions"]) > 0:
						summary_out.write(dout_info["descriptions"][-1] + "\n")
				summary_out.write("\n")
				i+=1