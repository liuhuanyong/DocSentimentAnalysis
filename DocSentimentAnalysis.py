#!/usr/bin/env python3
# coding: utf-8
# File: DocSentimentAnalysis.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-7-16

from sentence_parser import *
import ahocorasick
import jieba
import re
import math
import os

class Sentimentor():
    def __init__(self):
        CUR_DIR = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        DICT_DIR = os.path.join(CUR_DIR,'dict')
        DescPath = os.path.join(DICT_DIR, 'desc_words.txt')
        SenPath = os.path.join(DICT_DIR, 'sentiment_words.txt')
        self.DescDict = {i.strip().split('\t')[0]:float(i.strip().split('\t')[1]) for i in open(DescPath) if i.strip()}
        self.SenDict = {i.strip().split('\t')[0]:float(i.strip().split('\t')[1]) for i in open(SenPath) if i.strip()}
        self.SenTree = self.build_actree(list(self.SenDict.keys()))
        self.UserWords = list(set(list(self.DescDict.keys()) + list(self.SenDict.keys())))
        jieba.load_userdict(self.UserWords)
        self.senti_parser = LtpParser()

    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            word = ' ' + word + ' '
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''content分句处理'''
    def seg_sentences(self, content):
        return [sentence.replace('\u3000','').replace('\xc2\xa0', '').replace(' ','') for sentence in re.split(r'[!?？！:;。\n\r]',content) if sentence]

    '''利用情感词过滤情感句'''
    def check_senti(self, sentence):
        flag = 0
        word_list = list(jieba.cut(sentence))
        # print(word_list)
        senti_words = []
        for i in self.SenTree.iter(' '.join(word_list + [' '])):
            senti_words.append(i[1][1].replace(' ', ''))
            flag += 1
        return flag, word_list, senti_words

    '''情感句过滤'''
    def filter_sentence(self, sentences):
        senti_sentences = list()
        for index, sentence in enumerate(sentences):
            flag, word_list, senti_words = self.check_senti(sentence)
            if flag:
                senti_sentences.append([index, sentence, word_list, senti_words])
        return senti_sentences

    '''sentence analysis'''
    def get_sentence_score(self, sent_words, senti_words):
        sent_postag = self.senti_parser.get_postag(sent_words)
        sent_tuples = self.senti_parser.syntax_parser(sent_words, sent_postag)
        dep_dict = self.senti_parser.parser_dict(sent_words, sent_postag, sent_tuples)
        sent_score = 0.0
        for dep in dep_dict:
            word = dep[0]
            word_desc = dep[3]
            word_score = self.get_abs_sentiment(word, word_desc, senti_words)
            sent_score += word_score
            # print(dep, word_score)

        return math.tanh(sent_score)

    def get_abs_sentiment(self, word, word_desc, senti_words):
        if word not in senti_words:
            return 0.0
        else:
            word_score = self.SenDict.get(word, 0.6)
            if not word_desc:
                return word_score
            else:
                desc_words = []
                for rel, info in word_desc.items():
                    desc_words += [i[1] for i in info if i[2][0] not in ['w', 'u']]
                for desc_word in desc_words:
                    desc_score = self.DescDict.get(desc_word, 1.0)
                    word_score *= desc_score
            return word_score

    def doc_sentiment_score(self, content):
        sents = self.seg_sentences(content)
        senti_sentences = self.filter_sentence(sents)
        scores = []
        for sent in senti_sentences:
            sent_words = sent[2]
            senti_words = sent[3]
            sent_score = self.get_sentence_score(sent_words, senti_words)
            # print(sent[1], sent_score)
            if sent_score:
                scores.append(sent_score)
        if len(scores) > 0:
            return sum(scores)/len(scores)
        else:
            return 0.0


