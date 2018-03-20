#!/usr/bin/env python3
# coding: utf-8
# File: sentiment_objector.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-11
from sentence_parser import *
from senti_settings import *
import jieba
from math import *

class SentimentObjector():

    def __init__(self):
        pass

    '''content分句处理'''
    def process_content(self, content):
        return [sentence for sentence in SentenceSplitter.split(content) if sentence]

    '''利用情感词过滤情感句'''
    def check_senti(self, sentence):
        flag = 0
        for end_index in SenTree.iter(' '.join(list(jieba.cut(sentence)))):
            flag = 1
        return flag

    '''情感句过滤'''
    def filter_sentence(self, sentences):
        senti_sentences = list()
        for index, sentence in enumerate(sentences):
            if self.check_senti(sentence):
                senti_sentences.append([index, sentence])
        return senti_sentences

    '''情感对象抽取'''
    def object_extract(self, sentence):
        parse = LtpParser()
        words, postags, name_entity_dist, tuples, child_dict_list, roles_dict = parse.parser_main(sentence, JIEBA=True)
        sent_results = list()
        for tuple in tuples:
            if tuple[1] in SenDict.keys() and tuple[2] in ['a', 'n', 'd', 'v', 'i', 'z']:
                senti_index = tuple[0]
                senti_word = tuple[1]
                '''如果情感词为谓词,则采用规则1'''
                result1 = self.ruler1(senti_index, senti_word, words, roles_dict)
                result2 = self.ruler2(tuple, senti_word, words, roles_dict)
                result3 = self.ruler3(tuple, senti_word, child_dict_list)
                result4 = self.ruler4(tuple, senti_word)
                result5 = self.ruler5(tuple, senti_word)
                '''执行顺序:1->4->5->2->3'''
                if result1:
                    sent_results.append(result1)
                elif result4:
                    sent_results.append(result4)
                elif result5:
                    sent_results.append(result5)
                elif result2:
                    sent_results.append(result2)
                elif result3:
                    sent_results.append(result3)

        return sent_results

    '''规则1, 若语义角色标注中的谓词是情感词,则直接抽取情感词对应的A0'''
    def ruler1(self, word_index, word_word, words, roles_dict):
        pairs = []
        if word_index in roles_dict.keys():
            role_info = roles_dict[word_index]
            pairs = [[''.join(words[role[1]:role[2] + 1]), word_word] for role in role_info if role[0] in ['A0']]
        return pairs

    '''规则2,若情感词不是谓词,是谓词的状语,宾语等,则通过cmp,adv,vob关系找到谓语,然后再进行查找'''
    def ruler2(self, tuple, senti_word, words, roles_dict):
        pairs = []
        if tuple[-1] in ['VOB', 'ADV', 'CMP']:
            verb_word = tuple[3]
            verb_index = tuple[5]
            if verb_index in roles_dict.keys():
                for pre_pair in self.ruler1(verb_index, verb_word, words, roles_dict):
                    pairs.append([''.join(pre_pair), senti_word])
        return pairs

    '''规则3,若情感词为主谓结构,则通过SBV关系找到对应的主语'''
    def ruler3(self, tuple, senti_word, child_dict_list):
        pairs = []
        if tuple[-1] == 'VOB':
            verb_index = tuple[-2]
            for child_dict in child_dict_list:
                if child_dict[2] == verb_index and 'SBV' in child_dict[3].keys():
                    pairs = [[subj[1], senti_word] for subj in child_dict[3]['SBV'] if subj[-2] == verb_index]
        return pairs

    '''规则4,若情感词为SBV的核心词,情感对象为SBV的修饰词'''
    def ruler4(self, tuple, senti_word):
        pairs = []
        if tuple[-1] == 'SBV':
            pair = [senti_word, tuple[3]]
            pairs.append(pair)
        return pairs

    '''规则5,若情感词为定语,评价对象就是定语的修饰对象,即ATT的核心词'''
    def ruler5(self, tuple, senti_word):
        pairs = []
        if tuple[-1] == 'ATT':
            pair = [tuple[3], senti_word]
            pairs.append(pair)
        return pairs

    '''情感对象抽取主控函数'''
    def object_main(self,sentence):
        sentences = self.process_content(sentence)
        senti_sentences = self.filter_sentence(sentences)
        senti_tuples = list()
        set_results = set()
        for sent in senti_sentences:
            senti_tuples += self.object_extract(sent[1])
        for result in senti_tuples:
            pair = '->'.join(result[0]).replace('Root','')
            if pair.split('->')[0]:
                set_results.add(pair)
        datas = list()
        for item in set_results:
            if item.split('->')[1] in SenDict.keys():
                data = {}
                data['senti_object'] = item.split('->')[0]
                data['senti_desc'] = item.split('->')[1]
                data['senti_ploar'] = SenDict[item.split('->')[1]]
                datas.append(data)
        return datas

def test():
    content1 = """太差劲了，还不如很多四星，房间不隔音，楼上下洗手间声音太大，电视机是闪烁的，说信号不好，毛巾是破损的，这是在北京住的最差的五星酒店!这几天我的心情非常的好, 因为你不知道为什么苹果手机的质量这么靠谱!最近股价上涨的很快!音质有点出乎意料好，亚马逊配送小哥也很好，美中不足的是封塑明显松动，有后封嫌疑，鉴于其他无问题也就懒得问客服💁"""
    content2 = """硅原料供应问题得到有效解决"""
    content3 = """新华保险上涨的弹性最大"""
    content4 = """1季度延续去年年底的市场低迷状况"""
    content5 = """公司的重要优势是廉价的电和劳动力"""
    content6 = """同业资产规模大幅下降, 较二季度减少33.89%"""
    content7 = """手续费收入稳定增长, 拨备力度加大"""
    content8 = """#设施老旧# 但服务很好，位置很好。还是值得的"""
    content9 = """不错的一次网购，物流也快，赶在节前收到货了。包装比较差，快递速度墁。还可以，就是书的封面没有书名。另外，印书用的纸张质量也一般。"""
    sentimentor = SentimentObjector()
    datas = sentimentor.object_main(content1)
    for data in datas:
        print(data)
test()
