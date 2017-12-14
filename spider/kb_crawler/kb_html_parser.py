#-*- coding: UTF-8 -*-  


# kb的内容从basic_info_box里面抽取
# url的内容从电影的演员表（同时添加kb信息）和演员的参演电影里面抽取

# 电影：（名称，外文名，出品时间/上映时间/首播时间，导演，编剧，类型，演员）
#   导演，编剧，类型和演员都可能存在一对多
#   需要进行括号，逗号等处理
#   前6个都来自basic_info，最后一个来自drama_actor（演职员表）
# 演员：（名称，参演电影）
#   参演电影是一对多
#   名称来自basic_info，最后一个来自参演电影(starMovieandTVplay)，需要筛电影和电视
#
# parser抽取basic_info的全部内容和演职员表和参演电影表的全部内容保存
# url从演职员表和参演电影获取新url保存
# json写文件保存（不然放不下，然后再抽取做进一步处理）


from bs4 import BeautifulSoup  
import re  
import urlparse

from HTMLParser import HTMLParser

PREFIX = "https://baike.baidu.com"


class MovieParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

        self.state = 'none'
        self.first_href = False
        self.content = {
            "url": "",
            "basic_info": [],
            "actors": []
        }
        self.url_list = []

    def handle_starttag(self, tag, attrs):
        if tag == "div" and ('class', 'basic-info cmn-clearfix') in attrs:
            self.state = "basic"
        elif tag == "dt" and self.state == "basic":
            self.content["basic_info"].append(['', ''])
            self.state = "basic-dt"
        elif tag == "dd" and self.state == "basic":
            self.state = "basic-dd"
        elif tag == "a" and self.state == "basic-dd":
            self.state = "basic-dd-a"

        elif tag == "div" and ('class', 'drama-actor') in attrs:
            self.state = "in-actorlist"
        elif tag == "li" and ('class', 'listItem') in attrs and self.state == "in-actorlist":
            self.state = "in-actor"
        elif tag == "dl" and ('class', 'info') in attrs and self.state == "in-actor":
            self.state = "in-actorinfo"
        elif tag == "dt" and self.state == "in-actorinfo":
            self.state = "detail-info"
            self.content["actors"].append("")
            self.first_href = False
        elif tag == "a" and self.state == "detail-info":
            self.state = "detail-info-a"
            if self.first_href is False:
                new_url = ''
                for attr in attrs:
                    if attr[0] == 'href':
                        new_url = attr[1]
                if new_url != '':
                    self.url_list.append(PREFIX + new_url)
                self.first_href = True

    def handle_endtag(self, tag):
        if tag == "dt" and self.state == "basic-dt":
            self.state = "basic"
        elif tag == "a" and self.state == "basic-dd-a":
            self.state = "basic-dd"
        elif tag == "dd" and self.state == "basic-dd":
            self.state = "basic"
        elif tag == "div" and self.state == "basic":
            self.state = "none"

        elif tag == "a" and self.state == "detail-info-a":
            self.state = "detail-info"
        elif tag == "dt" and self.state == "detail-info":
            self.state = "in-actorinfo"
        elif tag == "dl" and self.state == "in-actorinfo":
            self.state = "in-actor"
        elif tag == "li" and self.state == "in-actor":
            self.state = "in-actorlist"
        elif tag == "div" and self.state == "in-actorlist":
            self.state = "none"

    def handle_data(self, data):
        data = data.strip()
        if self.state == "basic-dt":
            self.content["basic_info"][-1][0] += data
        elif self.state == "basic-dd":
            self.content["basic_info"][-1][1] += data
        elif self.state == "basic-dd-a":
            self.content["basic_info"][-1][1] += data

        elif self.state == "detail-info":
            self.content["actors"][-1] += data + ", "
        elif self.state == "detail-info-a":
            self.content["actors"][-1] += data + ", "

    def refresh(self):
        self.__init__()


class ActorParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

        self.state = 'none'
        self.first_movie = False
        self.first_href = False
        self.content = {
            "url": "",
            "basic_info": [],
            "movies": []
        }
        self.url_list = []

    def handle_starttag(self, tag, attrs):
        # print "TEST IN HANDLE STARTTAG", self.state
        if tag == "div" and ('class', 'basic-info cmn-clearfix') in attrs:
            self.state = "basic"
        elif tag == "dt" and self.state == "basic":
            self.content["basic_info"].append(['', ''])
            self.state = "basic-dt"
        elif tag == "dd" and self.state == "basic":
            self.state = "basic-dd"
        elif tag == "a" and self.state == "basic-dd":
            self.state = "basic-dd-a"

        elif tag == "div" and ('class', 'starMovieAndTvplay') in attrs and self.first_movie is False:
            self.state = "in-movielist"
            self.first_movie = True
        elif tag == "li" and ('class', 'listItem') in attrs and self.state == "in-movielist":
            self.state = "in-movie"
            self.content["movies"].append("")
        elif tag == "b" and ('class', 'title') in attrs and self.state == "in-movie":
            self.state = "in-movie-name"
        elif tag == "a" and self.state == "in-movie-name":
            self.state = "in-movie-name-a"
            new_url = ''
            for attr in attrs:
                if attr[0] == 'href':
                    new_url = attr[1]
            if new_url != '':
                self.url_list.append(PREFIX + new_url)

    def handle_endtag(self, tag):
        # print "TEST IN HANDLE ENDTAG", self.state
        if tag == "dt" and self.state == "basic-dt":
            self.state = "basic"
        elif tag == "a" and self.state == "basic-dd-a":
            self.state = "basic-dd"
        elif tag == "dd" and self.state == "basic-dd":
            self.state = "basic"
        elif tag == "div" and self.state == "basic":
            self.state = "none"

        elif tag == "a" and self.state == "in-movie-name-a":
            self.state = "in-movie-name"
        elif tag == "b" and self.state == "in-movie-name":
            self.state = "in-movie"
        elif tag == "li" and self.state == "in-movie":
            self.state = "in-movielist"
        elif tag == "div" and self.state == "in-movielist":
            self.state = "none"

    def handle_data(self, data):
        data = data.strip()
        if self.state == "basic-dt":
            self.content["basic_info"][-1][0] += data
        elif self.state == "basic-dd":
            self.content["basic_info"][-1][1] += data
        elif self.state == "basic-dd-a":
            self.content["basic_info"][-1][1] += data

        elif self.state == "in-movie-name-a":
            self.content["movies"][-1] += data

    def handle_comment(self, data):
        pass

    def refresh(self):
        self.__init__()