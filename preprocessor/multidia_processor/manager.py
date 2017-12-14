# too long/short
# dialog turn
# first sentence is a title(it can be removed)
#                   eg: 27, 33, 36
# punc
#
# fan ti zi replace
# special word
#   url             eg: 5, 19, 35
#   phone number    eg: 26
#   emoji           eg: 27
# lexical

import zh_wiki


def main():
    f_old = open("douban.raw")
    f_new = open("douban.processed", 'w')

    count = [0, 0, 0, 0]
    for line in f_old:
        sens = line[:-1].split("</s>")
        new_sens = []

        # special words
        for sen in sens:
            words = sen.split(" ")
            new_words = []

            url_mark = False
            for word in words:
                if "url" in word:
                    url_mark = True
                    new_words.append("<url>")
                    continue
                if url_mark is True:
                    url_mark = False
                    eng = True
                    for char in word:
                        if "a" <= char <= "z" or "A" <= char <= "Z":
                            pass
                        else:
                            eng = False
                            break
                    if eng:
                        continue
                try:
                    if 13000000000 < int(word) < 13999999999:
                        new_words.append("<phone_number>")
                        continue
                except:
                    pass
                new_words.append(word)
            new_sens.append(new_words)

        # first sentence/dialog turn
        # new_sens = new_sens[1:]
        if len(new_sens) < 2:
            count[1] += 1
            continue

        new_sens = ["".join(x) for x in new_sens]

        # length
        correct_l = True
        correct_s = False
        for sen in new_sens:
            if len(sen.decode('utf-8')) > 60:
                correct_l = False
            if len(sen.decode('utf-8')) >= 2:
                correct_s = True
        if not correct_l or not correct_s:
            count[2] += 1
            continue

        # complicate
        com_dict = {}
        for key in zh_wiki.zh2Hant:
            com_dict[zh_wiki.zh2Hant[key]] = key

        for i in range(0, len(new_sens)):
            sen = new_sens[i].decode("utf-8")
            new_sen = ""
            for char in sen:
                if char.encode('utf-8') in com_dict:
                    new_sen += com_dict[char.encode('utf-8')]
                else:
                    new_sen += char.encode('utf-8')
            new_sens[i] = new_sen

        f_new.write("</s>".join(new_sens) + "\n")
        count[0] += 1
        if count[0] % 5000 == 0:
            print count[0], "</s>".join(new_sens)
    print "total_number", count


if __name__ == "__main__":
    main()