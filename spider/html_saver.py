#-*- coding: UTF-8 -*-  

import json

# MCONTENT = "./movie_content.txt"
# ACONTENT = "./actor_content.txt"


class HtmlSaver(object):
      
    def __init__(self, file_name):
        self.file = open(file_name, "a")

    def write_file(self, content):
        line = json.dumps(content)
        self.file.write(line + "\n")

    def __del__(self):
        self.file.close()