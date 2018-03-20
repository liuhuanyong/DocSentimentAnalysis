#!/usr/bin/env python3
# coding: utf-8
# File: senti_settings.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-10

import os
import jieba
import ahocorasick


DICT_DIR = './dict'
DegreePath = os.path.join(DICT_DIR, 'degree.txt')
DenyPath = os.path.join(DICT_DIR, 'deny.txt')
FreqPath = os.path.join(DICT_DIR, 'freq.txt')
NegPath = os.path.join(DICT_DIR, 'neg.txt')
PosPath = os.path.join(DICT_DIR, 'pos.txt')
SenPath = os.path.join(DICT_DIR, 'sensor.txt')

def build_worddict(file, value_flag):
    word_dict = dict()
    with open(file, 'r') as f:
        for line in f:
            record = line.strip().split('\t')
            if len(record) == 2:
                word_dict[record[0]] = value_flag*float(record[-1])
            else:
                word_dict[record[0]] = value_flag*1
    return word_dict

def build_actree(wordlist):
    actree = ahocorasick.Automaton()
    for index, word in enumerate(wordlist):
        actree.add_word(word, (index, word))
    actree.make_automaton()
    return actree

DegreeDict = build_worddict(DegreePath, 1)
DenyDict = build_worddict(DenyPath, -1)
FreqDict = build_worddict(FreqPath, 1)
NegDict = build_worddict(NegPath, -1)
PosDict = build_worddict(PosPath, 1)
SorDict = build_worddict(SenPath, -1)
SenDict = NegDict
SenDict.update(PosDict)
SenDict.update(SorDict)

SenTree = build_actree(list(SenDict.keys()))
UserWords = set(list(DegreeDict.keys()) + list(DenyDict.keys()) + list(FreqDict.keys()) + list(SenDict.keys()))



for word in UserWords:
    jieba.add_word(word)

'''
def collect_fined():
    import jieba.posseg as pseg
    f = open('fined_words.txt', 'w+')
    for word in set(PosDict.keys()):
        tag = [word.flag for word in pseg.cut(word)]
        if 'a' in tag or 'i' in tag:
            f.write(word + '\t' + '1' + '\n')


    for word in set(NegDict.keys()):
        tag = [word.flag for word in pseg.cut(word)]
        if 'a' in tag or 'i' in tag:
            f.write(word + '\t' + '-1' + '\n')
    f.close()

collect_fined()
'''
