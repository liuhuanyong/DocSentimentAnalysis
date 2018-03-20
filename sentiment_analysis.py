#!/usr/bin/env python3
# coding: utf-8
# File: sentiment_analysis.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-10
from sentence_parser import *
from senti_settings import *
import jieba
from math import *

class Sentimentor():

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

    '''基于词性模板的情感得分计算'''
    def compute_sentscore(self, sentence):
        parse = LtpParser()
        score_total = 0.0
        words, postags, name_entity_dist, tuples, child_dict_list, roles_dict = parse.parser_main(sentence, JIEBA=True)
        for child_dict in child_dict_list:
            word = child_dict[0]
            if word in SenDict.keys() and child_dict[3]:
                cw = [word, child_dict[1]]
                for arc in child_dict[3].values():
                    for sub_arc in arc:
                        rel = sub_arc[-1]
                        mw = [sub_arc[1], sub_arc[2]]
                        if rel == 'ATT':
                            score = self.ATT_compute(cw, mw)
                            score_total += score
                        elif rel == 'SBV':
                            score = self.SBV_compute(cw, mw)
                            score_total += score
                        elif rel == 'VOB':
                            score = self.VOB_compute(cw, mw)
                            score_total += score
                        elif rel == 'COO':
                            score = self.COO_compute(cw, mw)
                            score_total += score
                        elif rel == 'ADV':
                            score = self.ADV_compute(cw, mw)
                            score_total += score
                        elif rel == 'CMP':
                            score = self.CMP_compute(cw, mw)
                            score_total += score
        return score_total

    '''ATT定中关系'''
    def ATT_compute(self, cw, mw):
        score = 0.0
        if (mw[1], cw[1]) in [('r', 'n'), ('m', 'n'), ('q','n')]:
            score = SenDict[cw[0]]
        if (mw[1], cw[1]) in [('n', 'n')] and mw[0] in SenDict.keys():
            score = SenDict[cw[0]] + SenDict[mw[0]]
        if (mw[1], cw[1]) in [('v', 'n'), ('a', 'n')] and mw[0] in SenDict.keys():
            score = abs(SenDict[cw[0]])*SenDict[mw[0]]
        #print('att', score, SenDict[cw[0]], cw, mw)
        return score

    '''SBV主谓关系'''
    def SBV_compute(self, cw, mw):
        score = 0.0
        if (mw[1], cw[1]) in [('r', 'n'), ('nh', 'v'), ('ns', 'v')]:
            score = SenDict[cw[0]]
        if (mw[1], cw[1]) in [('v', 'v')] and mw[0] in SenDict.keys():
            score = SenDict[cw[0]] + SenDict[mw[0]]
        if (mw[1], cw[1]) in [('n', 'v'), ('n', 'a')] and mw[0] in SenDict.keys():
            score = SenDict[cw[0]]*0.5 + SenDict[mw[0]]
        #print('sbv', score, SenDict[cw[0]], cw, mw)
        return score

    '''VOB动宾关系'''
    def VOB_compute(self, cw, mw):
        score = 0.0
        if (mw[1], cw[1]) in [('r', 'v'), ('m', 'v'), ('q', 'v')]:
            score = SenDict[cw[0]]
        if (mw[1], cw[1]) in [('v', 'v')] and mw[0] in SenDict.keys():
            score = SenDict[cw[0]] + SenDict[mw[0]]
        if (mw[1], cw[1]) in [('n', 'v'), ('a', 'v')] and mw[0] in SenDict.keys():
            score = SenDict[cw[0]] + SenDict[mw[0]]*0.5
        #print('vob', score, SenDict[cw[0]], cw, mw)
        return score

    '''COO并列关系'''
    def COO_compute(self, cw, mw):
        score = 0.0
        if mw[0] in SenDict.keys():
            score = SenDict[cw[0]] + SenDict[mw[0]]
        #print('coo', score, SenDict[cw[0]], cw, mw)
        return score

    '''CMP动补关系'''
    def CMP_compute(self, cw, mw):
        score = 0.0
        if mw[0] in SenDict.keys():
            score = SenDict[cw[0]] + SenDict[mw[0]]
        #print('cmp', SenDict[cw[0]], cw, mw)
        return score

    '''ADV状中关系'''
    def ADV_compute(self, cw, mw):
        score = 0.0
        if (mw[1], cw[1]) in [('d', 'v'), ('d', 'a')] and mw[0] in DegreeDict.keys():
            score = SenDict[cw[0]]*DegreeDict[mw[0]]
        if (mw[1], cw[1]) in [('d', 'v'), ('d', 'a')] and mw[0] in DenyDict.keys():
            score = SenDict[cw[0]]*-1
        if (mw[1], cw[1]) in [('nt', 'v'), ('p', 'v')]:
            score = SenDict[cw[0]]
        if (mw[1], cw[1]) in [('a', 'v')] and mw[0] in SenDict.keys():
            score = SenDict[mw[0]]*0.5 + SenDict[cw[0]]
        if (mw[1], cw[1]) in [('v', 'v')] and mw[0] in SenDict.keys():
            score = SenDict[cw[0]] + SenDict[mw[0]]
        #print('adv', score, SenDict[cw[0]], cw, mw)
        return score

    '''情感分析主控函数'''
    def sentiment_main(self, content):
        sentences = self.process_content(content)
        senti_sentences = self.filter_sentence(sentences)
        doc_score = 0.0
        for sent in senti_sentences:
            sent_index = sent[0]
            score_total = self.compute_sentscore(sent[1])
            doc_score += score_total
        return doc_score

def test():
    content1 = """
    央视新闻客户端3月9日消息，当地时间3月8日凌晨1时许，中国水电15局位于马里中部距离首都巴马科700公里处的项目工地现场及营地遭遇大约25至30名不明身份武装人员袭击。吊车、皮卡车、发电机等施工设备和物资均被烧毁；中方人员安全无伤亡，但随身手机、电脑等物品全部被抢。该项目组正在封闭工地并开始撤离。中国驻马里大使馆通报各驻马里中资企业定期排查隐患，采取安保措施，制定应急预案，切实加强防范，必要时考虑暂时撤离危险地区。
    """
    content2 = """
    华盛顿时间2018年3月1日，美国总统特朗普宣布，由于进口钢铁和铝产品严重损害了美国内产业，威胁到美国家安全，为重振美国钢铁和铝产业，决定将对所有来源的进口钢铁和铝产品全面征税，税率分别为25%和10%。商务部贸易救济局局长王贺军就此发表谈话。
    王贺军表示，美国进口的钢铁和铝产品大多是民用的中低端产品，并未损害美国国家安全。美国以国家安全为由限制钢铁和铝产品的国际贸易，是对以世贸组织为代表的多边贸易体制的严重破坏，必将对正常的国际贸易秩序造成重大冲击。美方可能出台的措施已经受到欧盟、加拿大、巴西、韩国等国家和地区的反对，美国内多个行业协会也对此表达了不满。
    """
    content3 = """
    最近几天，网上流传着一段高铁吃泡面的视频：一名男子在高铁上吃泡面，被一名女子怒怼。视频中的女子怒吼“整个高铁都知道不能吃泡面”，情绪激动，且言辞激烈。这段视频引起了网友的讨论，有人认为这位女子素质太差，也有人认为高铁上吃泡面，味道确实让人反感。
　　扬子晚报紫牛新闻记者辗转联系上视频中发飙的女子，她称因孩子对泡面过敏，曾跟这名男子沟通过，但对方执意不听，她这才发泄不满。记者无法联系上被怼的吃泡面男子
    """
    sentimentor = Sentimentor()
    sentences = sentimentor.process_content(content3)
    senti_sentences = sentimentor.filter_sentence(sentences)
    doc_score = 0.0
    for sent in senti_sentences:
        score_total = sentimentor.compute_sentscore(sent[1])
        doc_score += score_total
    print('doc score', doc_score)

test()
