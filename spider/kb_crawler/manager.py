#coding:utf-8

import os
import random
import sys
import time
import traceback

sys.path.append("..")
DIR = os.path.abspath(os.path.dirname(__file__))

import url_manager
import html_downloader
import kb_html_parser
import html_saver


# manager 启动，整体调控
# url_manager 记录扩展过的url和待扩展的url（包括断点恢复和存储）
# html_downloader 网页下载，模拟多个浏览器
# html_parser 网页解析器
# html_saver 存储网页内容

MOVIE_CONTENT = ["剧情简介", "演职员表", "角色介绍", "音乐原声", "幕后", "花絮",
                 "出品时间", "出品公司", "发行公司", "制片地区", "制片成本", "拍摄地点", "拍摄日期", "制片人",
                 "主演", "片长", "上映时间", "票房", "对白语言", "播放平台"]
ACTOR_CONTENT = [""]


class Spider(object):
    def __init__(self):
        self.url_manager = url_manager.UrlManager("./new_urls.txt", "./old_urls.txt", "./bad_urls.txt")
        self.html_downloader = html_downloader.HtmlDownloader()
        self.movie_parser = kb_html_parser.MovieParser()
        self.actor_parser = kb_html_parser.ActorParser()
        self.movie_saver = html_saver.HtmlSaver("./movie_content.txt")
        self.actor_saver = html_saver.HtmlSaver("./actor_content.txt")

    def main(self, movie_url, actor_url):

        warning_list = [0, 0, 0, 0]

        self.url_manager.add_url(movie_url)
        while (self.url_manager.total_count < 300 and self.url_manager.has_url()):

            # safe download
            craw_count = 0
            html_cont = ""
            while craw_count < 3:
                try:
                    new_url = self.url_manager.get_url()
                    html_cont = self.html_downloader.download(new_url)
                    if "</html>" not in html_cont:
                        raise
                    break
                except:
                    print "001-WARNING!!! TRY CRAW HTML FAILED!"
                    craw_count += 1
            if craw_count >= 3:
                print self.url_manager.temp_url
                warning_list[0] += 1
                self.url_manager.add_bad_url(self.url_manager.temp_url)
                continue

            # type
            try:
                index_begin = html_cont.index('<div class="lemma-catalog">')
                index_end = html_cont.index('</div>', index_begin)
                print index_begin, index_end
                if "演职员表" in html_cont[index_begin:index_end] or "剧情简介" in html_cont[index_begin:index_end]:
                    type = "movie"
                    parser = self.movie_parser
                    saver = self.movie_saver
                    print "movie: ===================="
                elif "参演电影" in html_cont[index_begin:index_end] or "演艺经历" in html_cont[index_begin:index_end]:
                    type = "actor"
                    parser = self.actor_parser
                    saver = self.actor_saver
                    print "actor: --------------------"
                else:
                    type = "unknown"
            except:
                type = "unknown"
            if type == "unknown":
                print "002-WARNING!!! TRY PREPROCESS FAILED!"
                print self.url_manager.temp_url
                warning_list[1] += 1
                self.url_manager.add_bad_url(self.url_manager.temp_url)
                continue

            # parse
            try:
                parser.feed(html_cont)
                parser.close()
                new_urls = parser.url_list
                new_content = parser.content
                new_content["url"] = self.url_manager.temp_url
                saver.write_file(new_content)
                self.url_manager.add_urls(new_urls)
            except:
                print "003-WARNING!!! TRY PARSE CONT FAILED!"
                print self.url_manager.temp_url
                warning_list[2] += 1
                self.url_manager.add_bad_url(self.url_manager.temp_url)
                continue

            # postprocess
            try:
                print self.url_manager.total_count, self.url_manager.temp_url
                for i in range(0, len(new_content["basic_info"])):
                    if i >= 5:
                        break
                    info = new_content["basic_info"][i]
                    print info[0], info[1]

                parser.refresh()
                self.url_manager.complete_url()

                if self.url_manager.total_count % 20 == 0:
                    time.sleep(random.randint(3, 6))
            except:
                print "004-WARNING!! TRY POSTPROCESS FAILED!"
                print self.url_manager.temp_url
                self.url_manager.add_bad_url(self.url_manager.temp_url)
                warning_list[3] += 1

        print "CRAWLER DONE, INFO: "
        print "warning: ", warning_list
        print "total: ", self.url_manager.total_count
        print "new: ", len(self.url_manager.new_urls)
        print "old: ", len(self.url_manager.old_urls)
        print "bad: ", len(self.url_manager.bad_urls)


if __name__ == '__main__':
    if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')
    default_encoding = sys.getdefaultencoding()

    # movie_url = "https://baike.baidu.com/item/%E8%8E%AB%E6%96%87%E8%94%9A/207736"
    movie_url = "https://baike.baidu.com/item/%E5%8A%9F%E5%A4%AB/5607641"
    # movie_url = "https://baike.baidu.com/item/%E5%A4%A7%E8%AF%9D%E8%A5%BF%E6%B8%B8/9640#2_1"        # 大话西游
    actor_url = "https://baike.baidu.com/item/%E6%9C%B1%E8%8C%B5/10617#3_1"                         # 朱茵
    obj_spider = Spider()
    obj_spider.main(movie_url, actor_url)
