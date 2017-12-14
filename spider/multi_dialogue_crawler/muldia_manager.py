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
import mdia_html_parser
import html_saver


GROUP_PERFIX = [
    # ["https://www.douban.com/group/EmirKusturica/discussion?start=", 682],
    # ["https://www.douban.com/group/EpisodeFilm/discussion?start=", 26],
    # ["https://www.douban.com/group/ustv/discussion?start=", 1036],
    # ["https://www.douban.com/group/dorama/discussion?start=", 680],
    # ["https://www.douban.com/group/ka-tvb/discussion?start=", 927],
    # ["https://www.douban.com/group/lonelylife/discussion?start=", 560],
    # ["https://www.douban.com/group/movie_view/discussion?start=", 512],
    # ["https://www.douban.com/group/199108/discussion?start=", 100],
    # ["https://www.douban.com/group/movie/discussion?start=", 2756],
    # ["https://www.douban.com/group/596333/discussion?start=", 1441],
    # ["https://www.douban.com/group/Cult_Movie/discussion?start=", 174],
    # ["https://www.douban.com/group/horrormovies/discussion?start=", 246],
    # ["https://www.douban.com/group/558979/discussion?start=", 73],
    # ["https://www.douban.com/group/frenchmovie/discussion?start=", 54],
    # ["https://www.douban.com/group/brit/discussion?start=", 59],
    # ["https://www.douban.com/group/tw/discussion?start=", 97],
    # ["https://www.douban.com/group/wuyechang/discussion?start=", 98],
    # ["https://www.douban.com/group/kr/discussion?start=", 97],
    # ["https://www.douban.com/group/hkmovies/discussion?start=", 68],
    # ["https://www.douban.com/group/NoDirection/discussion?start=", 162],
]


# manager 启动，整体调控
# url_manager 记录扩展过的url和待扩展的url（包括断点恢复和存储）
# html_downloader 网页下载，模拟多个浏览器
# html_parser 网页解析器
# html_saver 存储网页内容


class Spider(object):
    def __init__(self, argvs):
        self.url_manager = url_manager.UrlManager(
            "./new_urls.txt-" + str(argvs[3]),
            "./old_urls.txt-" + str(argvs[3]),
            "./bad_urls1.txt-" + str(argvs[3]))
        self.html_downloader = html_downloader.HtmlDownloader()
        self.article_list_parser = mdia_html_parser.ArticleListParser()
        self.article_parser = mdia_html_parser.ArticleParser()
        # self.article_list_saver = html_saver.HtmlSaver("./article_list.txt")
        self.article_saver = html_saver.HtmlSaver("./article.txt-" + str(argvs[3]))

    def main_article_list(self):

        count = [0, 0]
        warning_list = [0, 0]
        for perfix_pair in GROUP_PERFIX:
            perfix = perfix_pair[0]
            for page in range(0, perfix_pair[1]):

                count[0] += 1
                # if count[0] > 2:
                #     exit()
                if count[0] % 10 == 0:
                    time.sleep(random.randint(1, 2))

                # safe download
                craw_count = 0
                html_cont = ""
                while craw_count < 3:
                    try:
                        new_url = perfix + str(page * 25)
                        html_cont = self.html_downloader.download_by_request(new_url)
                        if "</html>" not in html_cont:
                            raise
                        break
                    except:
                        craw_count += 1
                if craw_count >= 3:
                    print "001-WARNING!!! TRY CRAW HTML FAILED!"
                    # print new_url
                    warning_list[0] += 1
                    continue

                # parse
                try:
                    self.article_list_parser.feed(html_cont)
                    self.article_list_saver.write_file(self.article_list_parser.url_list)
                    print "====================", page
                    print new_url
                    # print html_cont
                    print self.article_list_parser.url_list
                    self.article_list_parser.refresh()
                except:
                    print "002-WARNING!!! TRY PARSE CONT FAILED!"
                    print new_url
                    warning_list[1] += 1
                    continue

                count[1] += 1

        print "CRAWLER DONE, INFO: "
        print "count(try/success):", count
        print "warning(craw/parse): ", warning_list

    def main_article(self, file_name, argvs):

        count = [0, 0, 0, 0, 0]
        warning_list = [0, 0, 0]
        for line in open(file_name):

            count[0] += 1
            if count[0] <= int(argvs[1]) or count[0] > int(argvs[2]):
                continue
            new_urls = json.loads(line[:-1])
            for new_url in new_urls:

                count[1] += 1
                time.sleep(6)

                # safe download
                craw_count = 0
                html_cont = ""
                while craw_count < 3:
                    try:
                        html_cont = self.html_downloader.download(new_url)
                        if "</html>" not in html_cont:
                            raise
                        break
                    except:
                        craw_count += 1
                if craw_count >= 3:
                    print "001-WARNING!!! TRY CRAW HTML FAILED!"
                    print new_url
                    self.url_manager.add_bad_url(new_url)
                    warning_list[0] += 1
                    continue

                # parse
                try:
                    print "====================", "page: ", count[0], "url: ", count[1], \
                        "succ: ", count[3], time.ctime()
                    print new_url
                    self.article_parser.feed(html_cont.decode('utf-8'))
                    print "topic", self.article_parser.content["topic"].strip().encode('utf-8')
                    print "author", self.article_parser.content["author"].strip().encode('utf-8')
                    # print "t-content", self.article_parser.content["topic_content"].replace("\r", "\n").strip()
                    '''print "dialogue"
                    for dialog in self.article_parser.content["multi_dialogues"]:
                        if len(dialog) >= 2 and (dialog[0][0] == self.article_parser.content["author"] or
                                                         dialog[1][0] == self.article_parser.content["author"]):
                            print self.article_parser.content["author"], self.article_parser.content["topic_content"]
                            for pair in dialog:
                                print pair[0], pair[1]
                            count[3] += 1
                            print "----------------"
                        elif len(dialog) > 2:
                            for pair in dialog:
                                print pair[0], pair[1]
                            count[3] += 1
                            print "----------------"'''
                    if self.article_parser.content["topic"] != "" and self.article_parser.content["author"] != "" \
                        and len(self.article_parser.content["multi_dialogues"]) != 0:
                        self.article_saver.write_file(self.article_parser.content)
                        count[4] += len(self.article_parser.content["multi_dialogues"])
                        count[3] += 1
                        print "SUCCESS!"
                    self.article_parser.refresh()
                except:
                    print "002-WARNING!!! TRY PARSE CONT FAILED!"
                    print new_url
                    warning_list[1] += 1
                    continue

                count[2] += 1

        print "CRAWLER DONE, INFO: "
        print "count(page/try/success/dialogue):", count
        print "warning(craw/parse): ", warning_list


if __name__ == '__main__':

    '''
    if sys.getdefaultencoding() != 'gbk':
        reload(sys)
        sys.setdefaultencoding('gbk')
    default_encoding = sys.getdefaultencoding()

    sys.argv = [0, 6000, 7000, 7]
    obj_spider = Spider(sys.argv)
    # obj_spider.main_article_list()
    obj_spider.main_article("./article_list.txt.all", sys.argv)
    '''

    test_url = "https://www.douban.com/group/topic/52346190/"
    html_cont = html_downloader.HtmlDownloader().download(test_url)
    print html_cont
