#-*- coding: UTF-8 -*-

import json
import time

'''
    entity:
        movie, director, actor, type, character, gender
    relation:
        movie: name_is, foreign_name_is, time_is(divided), direct_by, type_is, actor_by
        director: direct_movie
        actor: act_movie
        type: has_movie
'''


class Builder(object):
    def __init__(self, actor_file, movie_file, entity_file, triple_file):
        self.actor_file = open(actor_file, 'r')
        self.movie_file = open(movie_file, 'r')
        self.entity_file = open(entity_file, 'w')
        self.triple_file = open(triple_file, 'w')

        self.entity_dict = {
            "movie": {},
            "director": {},
            "actor": {},
            "type": {}
        }

    def __del__(self):
        self.actor_file.close()
        self.movie_file.close()
        self.entity_file.close()
        self.triple_file.close()

    def refresh(self):
        pass

    def scan(self):
        director_dict = {}
        type_dict = {}

        for line in self.movie_file:
            info = json.loads(line[:-1])
            director_dict[info["basic_info"][3][1]] = 0

            type_info = info["basic_info"][4][1].strip().encode('utf-8')
            types = []
            if "，" in type_info:
                types = type_info.split("，")
            elif "," in type_info:
                types = type_info.split(",")
            elif "\\" in type_info:
                types = type_info.split("\\")
            elif "/" in type_info:
                types = type_info.split("/")
            elif "／" in type_info:
                types = type_info.split("／")
            elif " " in type_info:
                types = type_info.split(" ")
            elif ";" in type_info:
                types = type_info.split(";")
            elif "；" in type_info:
                types = type_info.split("；")
            elif "、" in type_info:
                types = type_info.split("、")
            elif type_info == "UNKNOWN":
                pass
            else:
                types.append(type_info)

            for t in types:
                type_dict[t.strip()] = 0

        print len(type_dict)
        for t in type_dict:
            print t



    def clean_value(self, line, clean_count):
        # total/clean1/clean2/clean3:  [12165, 104, 9098, 10308]

        if line[:-1] == "":
            return ""
        info = json.loads(line[:-1])

        # tuples filter
        for i in range(0, len(info["basic_info"]))[::-1]:
            tup = info["basic_info"][i]
            if ("中文名".decode("utf-8") == tup[0] or "姓名".decode("utf-8") == tup[0]) and tup[1] != "":
                tup[0] = "中文名".decode("utf-8")
            else:
                del info["basic_info"][i]

        for i in range(0, len(info["movies"]))[::-1]:
            if info["movies"][i] == "":
                del info["movies"][i]

        # null
        if len(info["basic_info"]) == 0:
            clean_count[1] += 1
            return ""
        if len(info["movies"]) == 0:
            clean_count[2] += 1
            return ""

        # duplicate
        for uni_info in self.buffer_list:
            mark = True
            if "!".join(uni_info["movies"]) == "!".join(info["movies"]):
                pass
            else:
                mark = False
            if mark:
                for i in range(0, len(uni_info["basic_info"])):
                    if uni_info["basic_info"][i] == info["basic_info"][i]:
                        pass
                    else:
                        mark = False
                        break
            else:
                mark = False

            if mark:
                clean_count[3] += 1
                return ""

        self.buffer_list.append(info)

        # error data

        return json.dumps(info) + "\n"

    def extract_info(self, info):
        pass


def build():
    rule_p = Builder("actor_content.temp1", "movie_content.temp1",
                     "entities.kb", "triples.kb")

    rule_p.scan()
    # rule_p.refresh()

    '''clean_count = [0, 0, 0, 0, 0, 0, 0, 0]
    for line in rule_p.raw_file:
        # count += 1
        if clean_count[0] % 1000 == 0:
            print clean_count[0], "...", time.ctime()

        line = rule_p.clean_movie(line, clean_count)
        rule_p.new_file.write(line)
        if line != "":
            clean_count[0] += 1

    print "clean_count: ", clean_count'''


if __name__ == "__main__":
    build()
