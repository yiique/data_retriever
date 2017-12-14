#-*- coding: UTF-8 -*-  


# 一级页面：（获取单个问题url）
#   list-inner->dl
# 二级页面：（问题，问题详细，答案（有最佳取最佳，否则取第一个），赞，踩等）
#
# parser抽取basic_info的全部内容和演职员表和参演电影表的全部内容保存
# url从演职员表和参演电影获取新url保存
# json写文件保存（不然放不下，然后再抽取做进一步处理）


from HTMLParser import HTMLParser

PREFIX1 = "https://zhidao.baidu.com/search?word="           # 后加搜索名gbk转码
SUFFIX1 = "&ie=gbk&site=-1&sites=0&date=0&pn="              # 后加页数0/10/20


class QAListParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

        self.state = 'none'
        # self.first_dt = False
        self.url_list = []

    def handle_starttag(self, tag, attrs):
        if tag == "div" and ('class', 'list-inner') in attrs:
            self.state = "inner"
        elif tag == "dt" and self.state == "inner":
            self.state = "inner-dt"
        elif tag == "a" and self.state == "inner-dt":
            self.state = "inner-dt-a"
            new_url = ''
            for attr in attrs:
                if attr[0] == 'href':
                    new_url = attr[1]
            if new_url != '':
                self.url_list.append(new_url)

    def handle_endtag(self, tag):
        if tag == "a" and self.state == "inner-dt-a":
            self.state = "inner-dt"
        elif tag == "dt" and self.state == "inner-dt":
            self.state = "inner"
        elif tag == "div" and self.state == "inner":
            self.state = "none"

    def handle_data(self, data):
        pass

    def refresh(self):
        self.__init__()


class QAParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

        self.state = 'none'
        self.eva_state = 'none'
        self.content = {
            "url": "",
            "question": "",
            "question_detail": "",
            "answer": "",
            "eva": []
        }

    def handle_starttag(self, tag, attrs):
        if tag == "div" and ('class', 'wgt-ask accuse-response line mod-shadow ') in attrs:
            self.state = "question"
        elif tag == "span" and ('class', 'ask-title ') in attrs and self.state == "question":
            self.state = "question-title"
        elif tag == "span" and ('class', 'con') in attrs and self.state == "question":
            self.state = "question-content"

        # re answer
        elif tag == "div" and ('class', 'wgt-best mod-shadow wgt-recommend ') in attrs:
            self.state = "re-answer"
        elif tag == "div" and ('class', 'wgt-best mod-shadow  ') in attrs:
            self.state = "re-answer"
        elif tag == "pre" and self.state == "re-answer":
            self.state = "re-answer-content"

        # answer
        elif tag == "div" and (('class', 'wgt-answers') in attrs or ('class', 'wgt-answers   ') in attrs):
            self.state = "multi-answer"
        elif tag == "span" and ('class', 'con') in attrs and self.state == "multi-answer":
            self.state = "multi-answer-content"

        # word_replace
        elif tag == "img" and ('class', 'word-replace') in attrs and self.state == 'question-content':
            for attr in attrs:
                if attr[0] == 'src':
                    self.content["question_detail"] += "<replace>" + attr[1] + "</replace>"

        elif tag == "img" and ('class', 'word-replace') in attrs \
                and (self.state == 're-answer-content' or self.state == 'multi-answer-content'):
            for attr in attrs:
                if attr[0] == 'src':
                    self.content["answer"] += "<replace>" + attr[1] + "</replace>"

    def handle_endtag(self, tag):
        if tag == "span" and self.state == "question-content":
            self.state = "question"
        elif tag == "span" and self.state == "question-title":
            self.state = "question"
        elif tag == "div" and self.state == "question":
            self.state = "none"

        elif tag == "pre" and self.state == "re-answer-content":
            self.state = "none"
        elif tag == "span" and self.state == "multi-answer-content":
            self.state = "none"

    def handle_data(self, data):
        data = data.strip()
        if self.state == "question-title":
            self.content["question"] += data
        elif self.state == "question-content":
            self.content["question_detail"] += data

        elif self.state == "re-answer-content":
            self.content["answer"] += data

        elif self.state == "multi-answer-content":
            self.content["answer"] += data

    def handle_comment(self, data):
        pass

    def refresh(self):
        self.__init__()