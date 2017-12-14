#coding:utf-8

import os
import random
import sys
import time

sys.path.append("..")
DIR = os.path.abspath(os.path.dirname(__file__))

import json
import random
import sys
import time
import urllib

import url_manager
import html_downloader
import sqa_url_parser
import html_saver


PREFIX = "https://zhidao.baidu.com/search?word="           # 后加搜索名gbk转码
SUFFIX = "&ie=gbk&site=-1&sites=0&date=0&pn="              # 后加页数0/10/20

KEY_WORDS = [
    "电影",
    "上映", "放映", "哪年", "哪一年", "时间", "时候", "地方",
    "导演", "编导", "拍的",
    "类型",
    "演员", "演过", "拍过", "演的", "主演", "拍", "演",
    "身高", "高", "出生", "生日", '出生日期'
]
KEY_WORDS = [word.decode('utf-8') for word in KEY_WORDS]


# manager 启动，整体调控
# url_manager 记录扩展过的url和待扩展的url（包括断点恢复和存储）
# html_downloader 网页下载，模拟多个浏览器
# html_parser 网页解析器
# html_saver 存储网页内容


class Spider(object):
    def __init__(self, argvs):
        # self.url_manager = url_manager.UrlManager("./new_urls.txt", "./old_urls.txt", "./bad_urls.txt")
        self.html_downloader = html_downloader.HtmlDownloader()
        self.qa_list_parser = sqa_url_parser.QAListParser()
        self.qa_parser = sqa_url_parser.QAParser()
        # self.qa_list_saver = html_saver.HtmlSaver("./test.txt")
        self.qa_saver = html_saver.HtmlSaver("./actor_qa.txt-" + str(argvs[3]))

    def main(self, file_name, argvs):
        entity_file = open(file_name)

        count = [0, 0, 0, 0]
        warning_list = [0 for _ in range(7)]

        for line in entity_file:
            count[0] += 1
            if count[0] <= int(argvs[1]) or count[0] > int(argvs[2]):
                continue
            time.sleep(random.randint(3, 5))

            try:
                sys.stdout.flush()
                print "ENTITY ============================================", count[0], time.ctime()
                entity = json.loads(line[:-1])["basic_info"][0][1]
                print entity.encode('utf-8')
                entity = urllib.quote(entity.encode('gbk'))
                print entity, time.ctime()
            except:
                print "001-WARNING!!! TRY PREPROCESS FAILED!"
                warning_list[0] += 1
                continue

            # level1
            for i in range(0, 12):

                # level1: safe craw
                craw_count = 0
                html_cont = ""
                temp_urls = []
                while craw_count < 3:
                    try:
                        new_url_level1 = PREFIX + entity + SUFFIX + str(i * 10)
                        html_cont = self.html_downloader.download(new_url_level1)
                        if "</html>" not in html_cont:
                            raise
                        break
                    except:
                        craw_count += 1
                if craw_count >= 3:
                    print "002-WARNING!!! TRY CRAW HTML LEVEL1 FAILED!"
                    print new_url_level1
                    warning_list[1] += 1
                    continue

                # level1: parse
                try:
                    self.qa_list_parser.refresh()
                    self.qa_list_parser.feed(html_cont)
                    # self.qa_list_saver.write_file(self.qa_list_parser.url_list)
                    temp_urls = self.qa_list_parser.url_list
                except:
                    print "003-WARNING!!! TRY PARSE CONT LEVEL1 FAILED!"
                    print new_url_level1
                    warning_list[2] += 1
                    continue
                count[1] += 1

                # level2
                for new_url_level2 in temp_urls:
                    # level2: safe craw
                    count[2] += 1
                    craw_count = 0
                    html_cont = ""
                    while craw_count < 3:
                        try:
                            html_cont = self.html_downloader.download_by_request(new_url_level2)
                            if "</html>" not in html_cont:
                                raise
                            break
                        except:
                            craw_count += 1
                    if craw_count >= 3:
                        print "004-WARNING!!! TRY CRAW HTML LEVEL2 FAILED!"
                        print new_url_level2
                        warning_list[3] += 1
                        continue

                    # level2: parse
                    try:
                        self.qa_parser.refresh()
                        self.qa_parser.feed(html_cont.decode('gbk'))
                        if self.qa_parser.content["question"] == "" or self.qa_parser.content["answer"] == "":
                            print "006-WARNING!!! TRY GET QA LEVEL2 FAILED!"
                            warning_list[5] += 1
                            continue
                        satisfy = False
                        for word in KEY_WORDS:
                            if word in self.qa_parser.content["question"] or \
                                            word in self.qa_parser.content["question_detail"]:
                                satisfy = True
                                break
                        if not satisfy:
                            print "007-WARNING!!! TRY GET SATISFIED QUESTION LEVEL2 FAILED!"
                            warning_list[6] += 1
                            print self.qa_parser.content["question"].encode('utf-8')
                            continue
                        print "008-SUCCESS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", count[2], time.ctime()
                        print "question", self.qa_parser.content["question"].encode('utf-8')
                        print "q_detail", self.qa_parser.content["question_detail"].encode('utf-8')
                        print "answer", self.qa_parser.content["answer"]
                        self.qa_saver.write_file(self.qa_parser.content)
                    except:
                        print "005-WARNING!!! TRY PARSE CONT LEVEL2 FAILED!"
                        print new_url_level2
                        warning_list[4] += 1
                        continue
                    count[3] += 1

        print "CRAWLER DONE, INFO: "
        print "count(try1/handle1/try2/handle2):", count
        print "warning(name/craw1/parse1/craw2/parse2/empty/bad): ", warning_list


    def main_qa_list(self, file_name):
        entity_file = open(file_name)

        count = [0, 0]
        warning_list = [0, 0]
        for line in entity_file:
            count[0] += 1
            if count[0] <= 0 or count[0] > 5000:
                continue
            time.sleep(random.randint(1, 2))

            try:
                sys.stdout.flush()
                print "========================", count[0]
                entity = json.loads(line[:-1])["basic_info"][0][1]
                print entity.encode('utf-8')
                entity = urllib.quote(entity.encode('gbk'))
                print entity, time.ctime()
            except:
                print "001-WARNING!!! TRY PREPROCESS FAILED!"
                continue

            for i in range(0, 12):
                # safe download
                craw_count = 0
                html_cont = ""
                while craw_count < 3:
                    try:
                        new_url = PREFIX + entity + SUFFIX + str(i * 10)
                        html_cont = self.html_downloader.download(new_url)
                        if "</html>" not in html_cont:
                            raise
                        break
                    except:
                        craw_count += 1
                if craw_count >= 3:
                    print "002-WARNING!!! TRY CRAW HTML FAILED!"
                    print new_url
                    warning_list[0] += 1
                    continue

                # parse
                try:
                    self.qa_list_parser.feed(html_cont)
                    self.qa_list_saver.write_file(self.qa_list_parser.url_list)
                    self.qa_list_parser.refresh()
                except:
                    print "003-WARNING!!! TRY PARSE CONT FAILED!"
                    print new_url
                    warning_list[1] += 1
                    continue

                count[1] += 1

        print "CRAWLER DONE, INFO: "
        print "count(lists/urls):", count
        print "warning(craw/parse): ", warning_list

    def main_qa(self, file_name):

        url_file = open(file_name)

        count = [0, 0]
        warning_list = [0, 0, 0, 0]
        for line in url_file:
            count[0] += 1
            if count[0] <= 0 or count[0] > 5:
                continue
            if count[0] % 2 == 0:
                time.sleep(random.randint(1, 2))

            new_urls = json.loads(line[:-1])
            # new_urls = ["http://zhidao.baidu.com/question/481981492.html?fr=iks&word=%B9%A6%B7%F2&ie=gbk"]
            # new_urls = ["http://zhidao.baidu.com/question/481981492.html?&word=%B9%A6%B7%F2&ie=gbk"]
            for new_url in new_urls:
                # safe download
                craw_count = 0

                html_cont = ""
                while craw_count < 3:
                    try:
                        html_cont = self.html_downloader.download_by_request(new_url)
                        if "</html>" not in html_cont:
                            raise
                        break
                    except:
                        craw_count += 1
                if craw_count >= 3:
                    print "001-WARNING!!! TRY CRAW HTML FAILED!"
                    print new_url
                    warning_list[0] += 1
                    continue

                # parse
                try:
                    # print "TEST0", html_cont.decode('gbk')
                    self.qa_parser.feed(html_cont.decode('gbk'))
                    print "=====================================================================", time.ctime()
                    print "TEST url", count[1], new_url
                    print "TEST question", self.qa_parser.content["question"].encode('utf-8')
                    # print "TEST q_detail", self.qa_parser.content["question_detail"]
                    # print "TEST answer", self.qa_parser.content["answer"]
                    if self.qa_parser.content["question"] == "":
                        print "003-WARNING!!! TRY GET QUESTION FAILED!"
                        warning_list[2] += 1
                    if self.qa_parser.content["answer"] == "":
                        print "004-WARNING!!! TRY GET ANSWER FAILED!"
                        warning_list[3] += 1
                    self.qa_saver.write_file(self.qa_parser.content)
                    self.qa_parser.refresh()
                except:
                    print "002-WARNING!!! TRY PARSE CONT FAILED!"
                    print new_url
                    warning_list[1] += 1
                    continue

                count[1] += 1

        print "CRAWLER DONE, INFO: "
        print "count(lists/urls):", count
        print "warning(craw/parse): ", warning_list


if __name__ == '__main__':

    if sys.getdefaultencoding() != 'gbk':
        reload(sys)
        sys.setdefaultencoding('gbk')
    default_encoding = sys.getdefaultencoding()

    # sys.argv = ['', 500, 502, 1]
    obj_spider = Spider(sys.argv)
    obj_spider.main("./../../preprocessor/kb_processor/actor_content.temp1", sys.argv)

    # obj_spider.main_qa_list("./../../preprocessor/kb_processor/movie_content.temp1")
    # obj_spider.main_qa_list("./../../preprocessor/kb_processor/actor_content.temp1")
    # obj_spider.main_qa("./movie_qa_lists1.txt")
