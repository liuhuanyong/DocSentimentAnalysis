#!/usr/bin/env python3
# coding: utf-8
# File: sentence_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-10

import os
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SentenceSplitter, SementicRoleLabeller

LTP_DIR = "./ltp_data"

segmentor = Segmentor()
segmentor.load(os.path.join(LTP_DIR, "cws.model"))

postagger = Postagger()
postagger.load(os.path.join(LTP_DIR, "pos.model"))

parser = Parser()
parser.load(os.path.join(LTP_DIR, "parser.model"))

recognizer = NamedEntityRecognizer()
recognizer.load(os.path.join(LTP_DIR, "ner.model"))

labeller = SementicRoleLabeller()
labeller.load(os.path.join(LTP_DIR, 'pisrl.model'))


