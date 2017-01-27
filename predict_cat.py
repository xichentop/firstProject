'''
Created on Dec 13, 2016
predicts cat using both result from training and from regex detection
outputs d.out
@author: xichentop
'''
#===============================================================================
# imported libraries
#===============================================================================
from __future__ import print_function
import argparse
import nltk
import codecs
import re
from nltk import word_tokenize
from nltk import pos_tag


def process_cat_list(cat_file):
    cat_list =[]
    syn_dict={}
    feature_tags = ['NN','NNS','JJ']
    with codecs.open(cat_file, 'r', encoding='utf-8', errors='ignore') as cf:
        for line in cf:
            line = line.strip().lower()
            if line:
                cat = line
                idx = line.find(':')
                if idx !=-1:
                    cat = line[0:idx]
                    tokens = word_tokenize(line[idx+1:])
                    descr = pos_tag(tokens)
                    negation = False
                    for token,tag in descr:
                        if token == 'not' or token == 'than':
                            negation = True
                        elif token == '.' or token == ',':
                            negation = False
                        elif token == cat or re.search('\W', token):
                            continue
                        elif tag in feature_tags and not negation:
                            syn_dict[token]=cat 
                    
                cat_list.append(cat)
                
                
                    
    return cat_list, syn_dict

# calc the top result from training
def ml_result(result):
    with codecs.open(result, 'rb', encoding='utf-8', errors='ignore') as f:
        ml_result = {}
        for line in f:
            tokens = line.strip().split()
            max_prob= 0
            max_idx = -1
            for i in xrange(2, len(tokens), 2):
#                 print(tokens[i])
                temp= float(tokens[i])
                if temp > max_prob:
                    max_idx = i
                    max_prob = temp
            t = re.sub('_',' ', tokens[0])
            ml_result[t]=tokens[max_idx-1]
    return ml_result  
      
# detect cat in attraction name
def regex_result(attractions, cat_list, syn_dict):
    regex_result = {}
    for name in attractions:
        n = name.lower()
        for c in sorted(cat_list, key=len, reverse=True):
            if name not in regex_result:                
                if c in n:
                    regex_result[name]=c
                else:
                    for syn in syn_dict:
                        if syn in n:
                            regex_result[name]=syn_dict[syn] 
#             else:
#                 if name.endswith(c) and c not in regex_result[name]:
#                     regex_result[name]=c
    return regex_result

#resolve differences between machine learning and regex detection;
def resolve_diff(ml_result, regex_result):
    result = {}
    overlap = set(ml_result.keys()).intersection(regex_result.keys())
    for key in ml_result:
        if key not in overlap:
            result[key]=ml_result[key]
        else:
            result[key]=regex_result[key]
    return result
# prep d*.out file    
def print_d_files(result, test_file):

    #to be implemented
    with codecs.open(test_file, 'rb', encoding='utf-8', errors='ignore') as f:
#	out = codecs.open(test_file+'.out','wb',encoding='utf-8',errors='ignore')
        for line in f:
            m = re.search('^\d+([^%]+)%%', line)
            if m:
                key = m.group(1).strip()
#                 print(key)
                idx = line.index('%')
                print('{} ##{} {}'.format(line[0:idx].encode('utf-8'), result[key].encode('utf-8'), line[idx:-1].encode('utf-8')))
# 	out.close()   
if __name__=='__main__':
    parser = argparse.ArgumentParser("predict_cat")
    parser.add_argument("result", help = "the result from machine learning") 
    parser.add_argument("cat_file", help = 'the cat file used in annotation')
    parser.add_argument("test_file", help = 'the segmented test data')
    args = parser.parse_args()
    ml_result = ml_result(args.result)
    attractions = ml_result.keys()
    cat_list, syn_dict = process_cat_list(args.cat_file)
    regex_result = regex_result(attractions, cat_list, syn_dict)
    result = resolve_diff(ml_result, regex_result)
    print_d_files(result, args.test_file)
#     cat_list = process_cat_list(args.cat_file)
#     regex_result = regex_result(attractions, cat_list)
#     ml_result = ml_result(r'C:\Users\xichentop\Documents\ling570\project\ml.result')
#     attractions = ml_result.keys()
#     for entry in ml_result:
#         print('{} {}'.format(entry, ml_result[entry]))
#     cat_list, syn_dict = process_cat_list(r'C:\Users\xichentop\Documents\ling570\project\category-list')
#     regex_result = regex_result(attractions, cat_list, syn_dict)
#     result = resolve_diff(ml_result, regex_result)
#     print_d_files(result, r'C:\Users\xichentop\Documents\ling570\project\dev_file.txt')
