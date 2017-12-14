#-*- coding: UTF-8 -*-  

import random
import requests
import urllib
import urllib2  

USER_AGENT_LIST = ["Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",     # safari mac
                   "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",              # safari win
                   "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",   # IE9
                   "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",   # IE8
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",   # firefox mac
                   "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",                   # firefox win
                   "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",     #opera mac
                   "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",                       #opera win
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",    # chrome mac
                   "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",   # tecent
                   "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",  # sougou
                   "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"]     # 360


class HtmlDownloader(object):  
      
    def download(self, url):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        req.add_header('User-Agent',
                       USER_AGENT_LIST[random.randint(0, 11)])

        if url is None:  
            return None  
        response = urllib2.urlopen(req)
          
        if response.getcode() != 200:
            return None  

        return response.read()

    def download_by_request(self, url):
        response = requests.get(url)
        response.encoding = ('gbk')

        return response.text                # unicode