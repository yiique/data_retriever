#-*- coding: UTF-8 -*-


# 一级页面：获取讨论帖url（超过0回复才行）
#   list-inner->dl
# 二级页面：（标题，题目描述，下方多轮对话）
#


from HTMLParser import HTMLParser


class ArticleListParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

        self.state = 'none'
        self.url_list = []

    def handle_starttag(self, tag, attrs):
        if tag == "div" and ('class', 'article') in attrs:
            self.state = "article-list"
        elif tag == "tr" and self.state == 'article-list':
            self.state = "article"
        elif tag == "td" and ('class', 'title') in attrs and self.state == 'article':
            self.state = "article-title"
        elif tag == "a" and self.state == "article-title":
            new_url = ''
            for attr in attrs:
                if attr[0] == 'href':
                    new_url = attr[1]
            if new_url != '':
                self.url_list.append(new_url)

    def handle_endtag(self, tag):
        if tag == "td" and self.state == "article-title":
            self.state = "article"
        elif tag == "tr" and self.state == "article":
            self.state = "article-list"
        # elif tag == "div" and self.state == "article-list":
        #     self.state = "none"

    def handle_data(self, data):
        pass

    def refresh(self):
        self.__init__()


class ArticleParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

        self.state = 'none'
        self.temp_pair = {
            "s1": '',
            "c1": '',
            "s2": '',
            "c2": ''
        }
        self.content = {
            "url": '',
            "topic": '',
            "topic_content": '',
            "author": '',
            "multi_dialogues": []
        }

    def handle_starttag(self, tag, attrs):
        if tag == "div" and ('id', 'content') in attrs:
            self.state = "content"

        elif tag == "h1" and self.state == "content":
            self.state = "topic"
        elif tag == "div" and ('class', 'topic-content') in attrs and self.state == "content":
            self.state = "topic-content"
        elif tag == "div" and ('class', 'topic-content clearfix') in attrs and self.state == "content":
            self.state = "topic-content"
        elif tag == "span" and ('class', 'from') in attrs and self.state == "topic-content":
            self.state = "topic-author"
        elif tag == "a" and self.state == "topic-author":
            self.state = "author"
        elif tag == "p" and self.state == "topic-content":
            self.state = "topic-content-p"

        elif tag == "ul" and ('class', 'topic-reply') in attrs:
            self.state = "reply-content"
        elif tag == "div" and ('class', 'reply-doc content') in attrs and self.state == "reply-content":
            self.state = "reply"
        elif tag == "div" and ('class', 'bg-img-green') in attrs and self.state == "reply":
            self.state = "reply-bg"
        elif tag == "a" and self.state == "reply-bg":
            self.state = "reply-s2"
        elif tag == "div" and ('class', 'reply-quote') in attrs and self.state == "reply":
            self.state = "reply-quote"
        elif tag == "span" and ('class', 'all') in attrs and self.state == "reply-quote":
            self.state = "reply-c1"
        elif tag == "span" and ('class', 'pubdate') in attrs and self.state == "reply-quote":
            self.state = "reply-pubdate"
        elif tag == "a" and self.state == "reply-pubdate":
            self.state = "reply-s1"
        elif tag == "p" and self.state == "reply":
            self.state = "reply-c2"

    def handle_endtag(self, tag):
        if tag == "h1" and self.state == "topic":
            self.state = "content"
        elif tag == "a" and self.state == "author":
            self.state = "topic-author"
        elif tag == "span" and self.state == "topic-author":
            self.state = "topic-content"
        elif tag == "p" and self.state == "topic-content-p":
            self.state = "topic-content"

        elif tag == "a" and self.state == "reply-s2":
            self.state = "reply-bg"
        elif tag == "div" and self.state == "reply-bg":
            self.state = "reply"
        elif tag == "span" and self.state == "reply-c1":
            self.state = "reply-quote"
        elif tag == "a" and self.state == "reply-s1":
            self.state = "reply-pubdate"
        elif tag == "span" and self.state == "reply-pubdate":
            self.state = "reply-quote"
        elif tag == "div" and self.state == "reply-quote":
            self.state = "reply"
        elif tag == "p" and self.state == "reply-c2":
            self.state = "reply"
        elif tag == "div" and self.state == "reply":
            self.state = "reply-content"

    def handle_data(self, data):
        if self.state == "topic":
            self.content["topic"] = data
        elif self.state == "author":
            self.content["author"] = data
        elif self.state == "topic-content-p":
            self.content["topic_content"] += data

        elif self.state == "reply-s2":
            self.temp_pair["s2"] += data
        elif self.state == "reply-c1":
            self.temp_pair["c1"] += data
        elif self.state == "reply-s1":
            self.temp_pair["s1"] += data
        elif self.state == "reply-c2":
            self.temp_pair["c2"] += data
            if self.temp_pair["s1"] != "" and self.temp_pair["c1"] != "":
                contin = False
                for dialog in self.content["multi_dialogues"]:
                    if dialog[-1] == (self.temp_pair["s1"], self.temp_pair["c1"]):
                        dialog.append((self.temp_pair["s2"], self.temp_pair["c2"]))
                        contin = True
                        break
                if not contin:
                    self.content["multi_dialogues"].append([(self.temp_pair["s1"], self.temp_pair["c1"]),
                                                            (self.temp_pair["s2"], self.temp_pair["c2"])])
            self.temp_pair = {"s1": '', "c1": '', "s2": '', "c2": ''}

    def refresh(self):
        self.__init__()
