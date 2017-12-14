#-*- coding: UTF-8 -*-

import os


class UrlManager(object):
    def __init__(self, new_file, old_file, bad_file):
        self.temp_url = ""
        self.new_urls = []
        self.old_urls = []
        self.bad_urls = []
        self.total_count = 0

        if os.path.exists(new_file):
            for line in open(new_file):
                self.new_urls.append(line[:-1])
        self.new_url_file = open(new_file, 'w')
        if os.path.exists(old_file):
            for line in open(old_file):
                self.old_urls.append(line[:-1])
                self.total_count += 1
        self.old_url_file = open(old_file, 'w')
        if os.path.exists(bad_file):
            for line in open(bad_file):
                self.bad_urls.append(line[:-1])
        self.bad_url_file = open(bad_file, 'w')

    def __del__(self):
        for url in self.new_urls:
            self.new_url_file.write(url + "\n")
        for url in self.old_urls:
            self.old_url_file.write(url + "\n")
        for url in self.bad_urls:
            self.bad_url_file.write(url + "\n")
        self.new_url_file.close()
        self.old_url_file.close()
        self.bad_url_file.close()

    def has_url(self):
        return len(self.new_urls) != 0

    def get_url(self):
        self.temp_url = self.new_urls[0]
        del self.new_urls[0]
        return self.temp_url

    def complete_url(self):
        self.old_urls.append(self.temp_url)
        self.temp_url = ""
        self.total_count += 1

    def add_url(self, url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls and url not in self.bad_urls:
            self.new_urls.append(url)

    def add_urls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_url(url)

    def add_bad_url(self, url):
        if url is None:
            return
        if url not in self.bad_urls:
            self.bad_urls.append(url)