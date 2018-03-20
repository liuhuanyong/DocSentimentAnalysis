#!/usr/bin/env python3
# coding: utf-8
# File: sentence_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-10

from global_settings import *
import jieba

class LtpParser():
    def __init__(self):
        pass
    '''ltp基本操作'''
    def basic_parser(self, words):
        postags = list(postagger.postag(words))
        netags = recognizer.recognize(words, postags)
        return postags, netags

    '''基于实体识别结果,整理输出实体列表'''
    def format_entity(self, words, netags, postags):
        '''
        O：这个词不是NE
        S：这个词单独构成一个NE
        B：这个词为一个NE的开始
        I：这个词为一个NE的中间
        E：这个词位一个NE的结尾
        Nh：人名
        Ni：机构名
        Ns：地名
        '''
        name_entity_dist = {}
        name_entity_list = []
        place_entity_list = []
        organization_entity_list = []
        ntag_E_Nh = ""
        ntag_E_Ni = ""
        ntag_E_Ns = ""
        index = 0
        for item in zip(words, netags):
            word = item[0]
            ntag = item[1]
            if ntag[0] != "O":
                if ntag[0] == "S":
                    if ntag[-2:] == "Nh":
                        name_entity_list.append(word+'_%s ' % index)
                    elif ntag[-2:] == "Ni":
                        organization_entity_list.append(word+'_%s ' % index)
                    else:
                        place_entity_list.append(word + '_%s ' % index)
                elif ntag[0] == "B":
                    if ntag[-2:] == "Nh":
                        ntag_E_Nh = ntag_E_Nh + word + '_%s ' % index
                    elif ntag[-2:] == "Ni":
                        ntag_E_Ni = ntag_E_Ni + word + '_%s ' % index
                    else:
                        ntag_E_Ns = ntag_E_Ns + word + '_%s ' % index
                elif ntag[0] == "I":
                    if ntag[-2:] == "Nh":
                        ntag_E_Nh = ntag_E_Nh + word + '_%s ' % index
                    elif ntag[-2:] == "Ni":
                        ntag_E_Ni = ntag_E_Ni + word + '_%s ' % index
                    else:
                        ntag_E_Ns = ntag_E_Ns + word + '_%s ' % index
                else:
                    if ntag[-2:] == "Nh":
                        ntag_E_Nh = ntag_E_Nh + word + '_%s ' % index
                        name_entity_list.append(ntag_E_Nh)
                        ntag_E_Nh = ""
                    elif ntag[-2:] == "Ni":
                        ntag_E_Ni = ntag_E_Ni + word + '_%s ' % index
                        organization_entity_list.append(ntag_E_Ni)
                        ntag_E_Ni = ""
                    else:
                        ntag_E_Ns = ntag_E_Ns + word + '_%s ' % index
                        place_entity_list.append(ntag_E_Ns)
                        ntag_E_Ns = ""
            index += 1
        name_entity_dist['nhs'] = self.modify_entity(name_entity_list, words, postags, 'nh')
        name_entity_dist['nis'] = self.modify_entity(organization_entity_list, words, postags, 'ni')
        name_entity_dist['nss'] = self.modify_entity(place_entity_list,words, postags, 'ns')
        return name_entity_dist

    '''entity修正,为rebuild_wordspostags做准备'''
    def modify_entity(self, entity_list, words, postags, tag):
        entity_modify = []
        if entity_list:
            for entity in entity_list:
                entity_dict = {}
                subs = entity.split(' ')[:-1]
                start_index = subs[0].split('_')[1]
                end_index = subs[-1].split('_')[1]
                entity_dict['stat_index'] = start_index
                entity_dict['end_index'] = end_index
                if start_index == entity_dict['end_index']:
                    consist = [words[int(start_index)] + '/' + postags[int(start_index)]]
                else:
                    consist = [words[index] + '/' + postags[index] for index in range(int(start_index), int(end_index)+1)]
                entity_dict['consist'] = consist
                entity_dict['name'] = ''.join(tmp.split('_')[0] for tmp in subs) + '/' + tag
                entity_modify.append(entity_dict)
        return entity_modify

    '''基于命名实体识别,修正words,postags'''
    def rebuild_wordspostags(self, name_entity_dist, words, postags):
        pre = ' '.join([item[0] + '/' + item[1] for item in zip(words, postags)])
        post = pre
        for et, infos in name_entity_dist.items():
            if infos:
                for info in infos:
                    post = post.replace(' '.join(info['consist']), info['name'])
        post = [word for word in post.split(' ') if len(word.split('/')) == 2 and word.split('/')[0]]
        words = [tmp.split('/')[0] for tmp in post]
        postags = [tmp.split('/')[1] for tmp in post]

        return words, postags

    '''依存关系格式化'''
    def syntax_parser(self, words, postags):
        '''
        主谓关系	SBV	subject-verb	我送她一束花 (我 <– 送)
        动宾关系	VOB	直接宾语，verb-object	我送她一束花 (送 –> 花)
        间宾关系	IOB	间接宾语，indirect-object	我送她一束花 (送 –> 她)
        前置宾语	FOB	前置宾语，fronting-object	他什么书都读 (书 <– 读)
        兼语	DBL	double	他请我吃饭 (请 –> 我)
        定中关系	ATT	attribute	红苹果 (红 <– 苹果)
        状中结构	ADV	adverbial	非常美丽 (非常 <– 美丽)
        动补结构	CMP	complement	做完了作业 (做 –> 完)
        并列关系	COO	coordinate	大山和大海 (大山 –> 大海)
        介宾关系	POB	preposition-object	在贸易区内 (在 –> 内)
        左附加关系	LAD	left adjunct	大山和大海 (和 <– 大海)
        右附加关系	RAD	right adjunct	孩子们 (孩子 –> 们)
        独立结构	IS	independent structure	两个单句在结构上彼此独立
        核心关系	HED	head	指整个句子的核心

        [1, '北京语言大学', 'ni', '是', 'v', 2, 'SBV']
        [2, '是', 'v', 'Root', 'w', 0, 'HED']
        [3, '中国', 'ns', '首都', 'n', 4, 'ATT']
        [4, '首都', 'n', '北京', 'ns', 5, 'ATT']
        [5, '北京', 'ns', '大学', 'n', 11, 'ATT']
        [6, '的', 'u', '北京', 'ns', 5, 'RAD']
        [7, '一', 'm', '所', 'q', 8, 'ATT']
        [8, '所', 'q', '大学', 'n', 11, 'ATT']
        [9, '语言', 'n', '类', 'n', 10, 'ATT']
        [10, '类', 'n', '大学', 'n', 11, 'ATT']
        [11, '大学', 'n', '是', 'v', 2, 'VOB']
        '''
        arcs = parser.parse(words, postags)
        words = ['Root'] + words
        postags = ['w'] + postags
        tuples = list()
        for index in range(len(words)-1):
            arc_index = arcs[index].head
            arc_relation = arcs[index].relation
            tuples.append([index+1, words[index+1], postags[index+1], words[arc_index], postags[arc_index], arc_index, arc_relation])

        return words, postags, tuples

    '''为句子中的每个词语维护一个保存句法依存儿子节点的字典'''
    def build_parse_child_dict(self, words, postags, tuples):
        """
        :param words:words
        :param tuples:tuples
        :return:
        ['Root', 0, {'HED': [[2, '点头', 'v', 'Root', 'w', 0, 'HED']]}]
        ['点头', 2, {'SBV': [[1, '他', 'r', '点头', 'v', 2, 'SBV']], 'COO': [[3, '表示', 'v', '点头', 'v', 2, 'COO']]}]
        ['表示', 3, {'VOB': [[4, '同意', 'v', '表示', 'v', 3, 'VOB']]}]
        ['同意', 4, {'VOB': [[7, '意见', 'n', '同意', 'v', 4, 'VOB']]}]
        ['我', 5, {'RAD': [[6, '的', 'u', '我', 'r', 5, 'RAD']]}]
        ['意见', 7, {'ATT': [[5, '我', 'r', '意见', 'n', 7, 'ATT']]}]
        """
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

    '''语义角色标注'''
    def format_labelrole(self, words, postags):
        '''
        ADV	adverbial, default tag ( 附加的，默认标记 )
        BNE	beneﬁciary ( 受益人 )
        CND	condition ( 条件 )
        DIR	direction ( 方向 )
        DGR	degree ( 程度 )
        EXT	extent ( 扩展 )
        FRQ	frequency ( 频率 )
        LOC	locative ( 地点 )
        MNR	manner ( 方式 )
        PRP	purpose or reason ( 目的或原因 )
        TMP	temporal ( 时间 )
        TPC	topic ( 主题 )
        CRD	coordinated arguments ( 并列参数 )
        PRD	predicate ( 谓语动词 )
        PSR	possessor ( 持有者 )
        PSE	possessee ( 被持有 )
        '''
        arcs = parser.parse(words, postags)
        roles = labeller.label(words, postags, arcs)
        roles_dict = {}
        for role in roles:
            #roles_dict[role.index] = [[arg.name,arg.range.start, arg.range.end] for arg in role.arguments]
            roles_dict[role.index] = {arg.name:[arg.name,arg.range.start, arg.range.end] for arg in role.arguments}
        return roles_dict


    '''parser主函数'''
    def parser_main(self, sentence, JIEBA=False):
        if JIEBA:
            words = list(jieba.cut(sentence))
        else:
            words = list(segmentor.segment(sentence))
        postags, netags = self.basic_parser(words)
        name_entity_dist = self.format_entity(words, netags, postags)
        words, postags = self.rebuild_wordspostags(name_entity_dist, words, postags)
        words, postags, tuples = self.syntax_parser(words, postags)
        child_dict_list = self.build_parse_child_dict(words, postags, tuples)
        roles_dict = self.format_labelrole(words, postags)

        return words, postags, name_entity_dist, tuples, child_dict_list, roles_dict



parse = LtpParser()
sentence = '李克强总理今天来我家了,我感到非常荣幸'
parse.parser_main(sentence, JIEBA=True)
