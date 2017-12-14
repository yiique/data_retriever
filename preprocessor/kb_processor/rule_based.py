#-*- coding: UTF-8 -*-

import json
import time

MOVIE_ATTRIBUTE = [
    "中文名".decode('utf-8'), "外文名".decode('utf-8'),
    "出品时间".decode('utf-8'), "上映时间".decode('utf-8'), "首播时间".decode('utf-8'),
    "导演".decode('utf-8'),
    "类型".decode('utf-8')
]


class RulePrecessor(object):
    def __init__(self, raw_file, new_file):
        # self.rule = yaml.load(open(rule_file))

        self.raw_file = open(raw_file, 'r')
        self.new_file = open(new_file, 'w')

        self.buffer_list = []

    def __del__(self):
        self.raw_file.close()
        self.new_file.close()

    def refresh(self):
        self.raw_file.seek(0)

    def scan(self):
        count = [0, 0, 0, 0]

        info_dict = {}
        for line in self.raw_file:
            info = json.loads(line[:-1])

            if count[0] % 2000 == 0:
                print "--------------------"
                for tup in info["basic_info"][0:5]:
                    print tup[0], tup[1]

                print "-- actors"
                print " ".join(info["actors"])

            '''if info["basic_info"][0][1] == "范冰冰".decode('utf-8'):
                print "~~~~~~~~~~~~~~~~~~~~"
                for tup in info["basic_info"]:
                    print tup[0], tup[1]
                print "url"
                print info["url"]
                print "-- movies"
                print " ".join(info["movies"])'''
            for tup in info["basic_info"]:
                if tup[0] not in info_dict:
                    info_dict[tup[0]] = 0
                info_dict[tup[0]] += 1

        print len(info_dict)
        for tup in info_dict:
            print tup, info_dict[tup]

    def clean_movie(self, line, clean_count):
        # clean_count:  [22039, 622, 13946, 2307, 2711, 1749, 9369, 10498]

        if line[:-1] == "":
            return ""
        info = json.loads(line[:-1])

        # tuples filter
        basic_info_new = [["中文名".decode('utf-8'), 'UNKNOWN'],
                          ["外文名".decode('utf-8'), 'UNKNOWN'],
                          ["时间".decode('utf-8'), 'UNKNOWN'],
                          ["导演".decode('utf-8'), 'UNKNOWN'],
                          ["类型".decode('utf-8'), 'UNKNOWN']]
        for i in range(0, len(info["basic_info"])):
            tup = info["basic_info"][i]
            if tup[0] in MOVIE_ATTRIBUTE:
                if tup[0] == MOVIE_ATTRIBUTE[0]:
                    basic_info_new[0][1] = tup[1]
                elif tup[0] == MOVIE_ATTRIBUTE[1]:
                    basic_info_new[1][1] = tup[1]
                elif tup[0] == MOVIE_ATTRIBUTE[2]:
                    # if 1800 <= tup[1][0:4] <= 2020:
                    basic_info_new[2][1] = tup[1][0:4]
                elif tup[0] == MOVIE_ATTRIBUTE[3] and basic_info_new[2][1] == 'UNKNOWN':
                    # if 1800 <= tup[1][0:4] <= 2020:
                    basic_info_new[2][1] = tup[1][0:4]
                elif tup[0] == MOVIE_ATTRIBUTE[4] and basic_info_new[2][1] == 'UNKNOWN':
                    # if 1800 <= tup[1][0:4] <= 2020:
                    basic_info_new[2][1] = tup[1][0:4]
                elif tup[0] == MOVIE_ATTRIBUTE[5]:
                    basic_info_new[3][1] = tup[1]
                elif tup[0] == MOVIE_ATTRIBUTE[6]:
                    basic_info_new[4][1] = tup[1]

        for i in range(0, len(info["actors"]))[::-1]:
            if info["actors"][i] == "":
                del info["actors"][i]

        # null
        if basic_info_new[0][1] == 'UNKNOWN':
            clean_count[1] += 1
            return ""
        if basic_info_new[1][1] == 'UNKNOWN':
            clean_count[2] += 1
        if basic_info_new[2][1] == 'UNKNOWN':
            clean_count[3] += 1
        if basic_info_new[3][1] == 'UNKNOWN':
            clean_count[4] += 1
            return ""
        if basic_info_new[4][1] == 'UNKNOWN':
            clean_count[5] += 1
        info["basic_info"] = basic_info_new

        if len(info["actors"]) == 0:
            clean_count[6] += 1
            return ""

        # duplicate
        for uni_info in self.buffer_list:
            mark = True
            if "!".join(uni_info["actors"]) == "!".join(info["actors"]):
                pass
            else:
                mark = False
            if mark:
                for i in range(0, 5):
                    if uni_info["basic_info"][i] == info["basic_info"][i]:
                        pass
                    else:
                        mark = False
                        break
            else:
                mark = False

            if mark:
                clean_count[7] += 1
                return ""

        self.buffer_list.append(info)
        # error data
        return json.dumps(info) + "\n"

    def clean_actor(self, line, clean_count):
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

    def entity_extractor(self, entity_file):
        e_file = open(entity_file, 'w')
        for line in self.raw_file:
            try:
                info = json.loads(line[:-1])
                for tup in info["basic_info"]:
                    # e_file.write(tup[0].encode('utf-8'))
                    # e_file.write(" ")
                    e_file.write(tup[1].encode('gbk'))
                    # e_file.write("\n")
                '''for movie in info["actors"]:
                    e_file.write(movie.encode('utf-8'))
                    e_file.write(" ")'''
                e_file.write("\n")
            except:
                pass
        e_file.close()


def clean():
    # rule_p = RulePrecessor("../raw_corpus/actor_content.txt", "actor_content.temp1")
    # rule_p = RulePrecessor("actor_content.temp1", "test.txt")

    # rule_p = RulePrecessor("../raw_corpus/movie_content.txt", "movie_content.temp1")
    rule_p = RulePrecessor("../../temp/kb/movie_content.txt", "test.txt")

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

    # rule_p.entity_extractor("movie_entities.txt")


if __name__ == "__main__":
    clean()
