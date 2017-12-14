#coding:utf-8
f = open("douban.raw", 'r')

'''
char_list = {}
word_list = {}

for line in f:
    words = line[:-1].split(" ")
    sen = "".join(words)
    sen = sen.decode('utf-8')
    for char in sen:
        if char not in char_list:
            char_list[char] = 0
        char_list[char] += 1
    for word in words:
        if word not in word_list:
            word_list[word] = 0
        word_list[word] += 1

char_dict= sorted(char_list.iteritems(), key=lambda d: d[1], reverse=True)
word_dict = sorted(word_list.iteritems(), key=lambda d: d[1], reverse=True)
print "================"
print "word num", len(word_dict)
for x in word_dict[:5]:
    print x[0], x[1]
for x in word_dict[-5:0]:
    print x[1], x[0]
print "char num", len(char_dict)
for x in char_dict[:5]:
    print x[0], x[1]
for x in char_dict[-5:0]:
    print x[1], x[0]

f.seek(0)

count = 0
total = 0
for line in f:
    total += 1
    line = "".join(line[:-1].split(" ")).decode("utf-8")

    sens = line.split("</s>")
    bad = False
    for sen in sens:
        if len(sen) > 60:
            bad = True
            break
    if bad:
        continue
    count += 1

print "================"
print count, "/", total
'''

count = 0
total = 0
for line in f:
    total += 1
    if "星座" in line or "白羊" in line or "金牛" in line or "双子" in line or \
        "巨蟹" in line or "狮子" in line or "处女" in line or "天秤" in line or \
        "天蝎" in line or "射手" in line or "摩羯" in line or "水瓶" in line or "双鱼" in line:
        count += 1
print count, "/", total
