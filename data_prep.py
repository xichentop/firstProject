# -*- coding: UTF-8 -*-
#!/usr/bin/python
'''
Created on Dec 7, 2016
this program prepares the input data for MALLET
@author: xichentop
@version: Dec 8, 2016

'''
#===============================================================================
# imported libraries
#===============================================================================
from __future__ import print_function
import codecs
import sys
import re
import argparse
from IPython.utils.io import stderr


def prep_train_file(train_file):
    with codecs.open(train_file, 'rb', encoding='utf-8',errors='ignore') as f:
        flag = False
        for line in f:
            # irrelevant text
            if '#' not in line and not flag:
                continue
            # section break
            elif '###' in line: 
                flag = False
                print()
            # section text    
            elif flag:
                print(line.strip().encode('utf-8'), end = ' ')
            # beginning of section
            else:
                m = re.search('\d+\s*([^#%]+)##([^#%]+)%%', line)
#                 n = re.search('\d+\s*([^%]+)%%', line) #test segmentation data without cat
                if m:
                    attr_name='_'.join(m.group(1).split())
                    cat='_'.join(m.group(2).split())
                    print('{} {}'.format(attr_name.encode('utf-8'), cat.encode('utf-8')), end =' ')
                    flag = True
#                 elif n:#test data without category
#                     attrac_name = '_'.join(n.group(1).split())
#                     print('{}'.format(attrac_name.encode('utf-8'), end=' '))
#                     flag = True
                        
def prep_test_file(test_file):
    with codecs.open(test_file, 'rb', encoding='utf-8', errors='ignore') as f:
        flag = False
        for line in f:
            # irrelevant text
            if '%%' not in line and not flag:
                continue
            # section break
            elif '###' in line: 
                flag = False
                print()
            # section text    
            elif flag:
                print(line.strip().encode('utf-8'), end = ' ')
            # beginning of section
            else:
                m = re.search('^\d+([^%]+)%%', line)                
                if m:
                    attrac_name = '_'.join(m.group(1).split())
                    print('{}'.format(attrac_name.encode('utf-8')), end=' ')
                    flag = True  
#             if flag:
#                 print(line.strip().encode('utf-8'), end=' ')
#             if '###' in line:
#                 print()
#                 flag = False
        
    

if __name__=='__main__':
    parser = argparse.ArgumentParser("data_prep")
    parser.add_argument("input_file", help = "the segmented input file") 
    parser.add_argument("mode", help = 'train or test')
    args = parser.parse_args()
    if args.mode == 'train':
        prep_train_file(args.input_file)
    elif args.mode == 'test':
        prep_test_file(args.input_file)
    else:
        stderr.write("input mode can be either 'train' or 'test'")
        
#     prep_test_file(r'C:\Users\xichentop\Documents\ling570\project\segmentation.txt')
#     prep_train_file(r'C:\Users\xichentop\Documents\ling570\project\segmentation.txt')
