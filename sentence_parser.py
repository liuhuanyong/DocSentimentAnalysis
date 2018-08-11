#!/usr/bin/env python3
# coding: utf-8
# File: sentence_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-10

import jieba
from pyltp import Postagger, Parser
import os

class LtpParser():
    def __init__(self):
        CUR_DIR = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        LTP_DIR = os.path.join(CUR_DIR, "ltp_data")
        self.postagger = Postagger()
        self.postagger.load(os.path.join(LTP_DIR, "pos.model"))
        self.parser = Parser()
        self.parser.load(os.path.join(LTP_DIR, "parser.model"))

    '''ltp基本操作'''
    def get_postag(self, words):
        return list(self.postagger.postag(words))

    '''依存关系格式化'''
    def syntax_parser(self, words, postags):
        arcs = self.parser.parse(words, postags)
        words = ['Root'] + words
        postags = ['w'] + postags
        dep_tuples = list()
        for index in range(len(words)-1):
            arc_index = arcs[index].head
            arc_relation = arcs[index].relation
            dep_tuples.append([index+1, words[index+1], postags[index+1], words[arc_index], postags[arc_index], arc_index, arc_relation])
        return dep_tuples

    '''为句子中的每个词语维护一个保存句法依存儿子节点的字典'''
    def parser_dict_old(self, words, postags, tuples):
        child_dict_list = list()
        for index, word in enumerate(words):
            child_dict = dict()
            for arc in tuples:
                if arc[3] == word:
                    if arc[-1] in child_dict:
                        child_dict[arc[-1]].append(arc)
                    else:
                        child_dict[arc[-1]] = []
                        child_dict[arc[-1]].append(arc)
            child_dict_list.append([word, postags[index], index, child_dict])
        return child_dict_list


    '''为句子中的每个词语维护一个保存句法依存儿子节点的字典'''
    def parser_dict(self, words, postags, tuples):
        child_dict_list = list()
        for index, word in enumerate(words):
            child_dict = dict()
            for arc in tuples:
                if arc[3] == word:
                    rel = arc[-1]
                    if rel in child_dict:
                        child_dict[rel].append(arc)
                    else:
                        child_dict[rel] = []
                        child_dict[rel].append(arc)
                if arc[1] == word:
                    rel = 'B_' + arc[-1]
                    arc = [arc[-2], arc[-4], arc[-3], arc[1], arc[2], arc[0], rel]
                    if rel in child_dict:
                        child_dict[rel].append(arc)
                    else:
                        child_dict[rel] = []
                        child_dict[rel].append(arc)
            child_dict_list.append([word, postags[index], index, child_dict])
        return child_dict_list

