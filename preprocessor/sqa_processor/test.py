import json

import os
import random
import sys
import time

sys.path.append("../../spider")
DIR = os.path.abspath(os.path.dirname(__file__))

import json
import random
import sys
import time
import urllib

import url_manager
import html_downloader
import html_saver
from spider.single_qa_crawler.sqa_url_parser import QAParser

replace = "https://zhidao.baidu.com/api/getdecpic?"
replace_dict = {

}

'''
f = open("./sqa_raw/movie_qa.txt-1")

count = 0
re_count = 0
for line in f:
    count += 1
    info = json.loads(line[:-1])
    if count % 10000 == 0:

        print "======================================="
        print count
        print info["url"]
        print info["question"]
        print info["question_detail"]
        print info["answer"].replace("\r", "")
        print [info["answer"]]
    if replace in info["answer"]:
        re_count += 1
print count, re_count'''


succ = False
content = ""
answer = ""
for i in range(100):
    time.sleep(1)
    print "count", i
    test_url = "https://zhidao.baidu.com/question/2116111864068948667.html"
    content = html_downloader.HtmlDownloader().download_by_request(test_url)#.decode('gbk')
    parser = QAParser()
    parser.feed(content)
    # print content
    # print parser.content["answer"]
    if replace not in parser.content["answer"]:
        succ = True
        answer = parser.content["answer"]
        break
    parser.refresh()

if succ:
    print content
    print answer
else:
    print "NOT SUCCESS!"
