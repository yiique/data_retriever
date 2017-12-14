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

import mdia_html_parser

from utils import html_downloader
from utils import html_saver
from utils import url_manager


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
        # self.article_list_parser = mdia_html_parser.ArticleListParser()
        # self.article_parser = mdia_html_parser.ArticleParser()
        # self.article_list_saver = html_saver.HtmlSaver("./article_list.txt")
        self.article_saver = html_saver.HtmlSaver("./article.raw-" + str(argvs[3]))

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

        count = [0, 0]
        warning_list = [0]
        for line in open(file_name):

            count[0] += 1
            if count[0] <= int(argvs[1]) or count[0] > int(argvs[2]):
                continue
            new_urls = json.loads(line[:-1])
            for new_url in new_urls:

                count[1] += 1
                time.sleep(5.5)

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
                        time.sleep(5.5)
                        craw_count += 1
                if craw_count >= 3:
                    print "WARNING!!! TRY CRAW HTML FAILED!"
                    print new_url
                    self.url_manager.add_bad_url(new_url)
                    warning_list[0] += 1
                    continue

                self.article_saver.write_file({
                    "url": new_url,
                    "content": html_cont
                })

                count[1] += 1
                print new_url

        print "CRAWLER DONE, INFO: "
        print "count(try/success):", count
        print "warning(craw): ", warning_list


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
    obj_spider = Spider(sys.argv)
    # obj_spider.main_article_list()
    obj_spider.main_article("./article_list.txt.all", sys.argv)
