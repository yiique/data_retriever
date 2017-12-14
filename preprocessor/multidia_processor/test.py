
import json

prefix = "../../raw_corpus/movie/multi_dia/article.txt-"
count = [0, 0]
for i in range(1, 18):
    f = open(prefix + str(i))
    for line in f:
        count[0] += 1
        info = json.loads(line[:-1])
        count[1] += len(info["multi_dialogues"])
        if count[0] % 2500 == 0:
            print "======================="
            print "url"
            print "topic", info["topic"]
            print "topic content", info["topic_content"]
            print "multi_dia"
            for dia in info["multi_dialogues"]:
                print "----------------"
                for sen in dia:
                    print sen[0], sen[1]

print count