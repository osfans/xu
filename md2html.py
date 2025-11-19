#!/usr/bin/env python3

import re, os, glob

template = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<style>
body {
  font-family: PMingLiu, HanaMinA, HanaMinB, Helvetica, arial, sans-serif;
  writing-mode: vertical-rl;
  -webkit-writing-mode: vertical-rl; }

.sm {
  margin: 20px 0 10px;
  padding: 0;
  font-weight: bold;
  font-size: 30px;
  border-left: 1px solid #cccccc;
  margin: 0 5px;
  cursor: text;
  position: static;
  clear: both;
  text-align: right;
}

.sd, .sd2, .zy, .zi, .zi1, .yi {
  font-size: 10px;
  text-align: center;
  cursor: text;
  float: left;
  margin-left: 10px;
  margin-right: 10px;
  line-height: 10px;
  letter-spacing: 0.35em;
}

.sd, .sd2 {
  margin-right: 25px;
  clear: both;
}

.sd2 {
  margin-right: 20px;
}

.zi, .zi1 {
  padding-top: 20px;
  padding-bottom: 10px;
  font-size: 20px;
  line-height: 20px;
}

.zi1 {
  padding-top: 10px;
}

.yi {
  min-height: 40px;
  text-align: left;
  line-height: 12px;
  margin-right: 8px;
}

.clear {
  clear: both;
}

.new {color: #BFBFBF;}

</style>
<title>徐氏類音字彙</title>

</head>
<body>
%s
</body>
</html>
"""

lines = list()

def append(fmt, s):
    #print(s)
    lines.append(fmt % s)

def parse(s):
    s = s.strip().strip("`").replace("〜", "—").replace("～", "—").replace("※", "").replace(" ", "")
    if "（" in s:
        s = re.sub(r"(.[\?=]?)（(.+?)）", r'<a title="\2">\1</a>', s)
    return s

def break_yi(yi):
    n = len(yi)
    if 0 < n < 4:
        yi = yi + (4-n) * "　"
        n = 4
    if n > 0 and '<' not in yi:
        yi = yi[:(n+1)//2]+"<br/>"+yi[(n+1)//2:]
    return yi

def md2html(filename):
    sm = ""
    sd = ""
    zi_count = 0
    zi_single = ""
    lines.clear()
    for line in open(filename, encoding="U8"):
        line = line.strip()
        if line:
            if line.startswith(">") or line.startswith("---") :
                continue
            if line.startswith("##"):
                line = line[2:].strip()
                if line == sd:
                    continue
                sd = line
                zi_count = 0
            elif line.startswith("#"):
                line = line[1:].strip()
                if line == sm:
                    continue
                sm = line
                append("<div class=sm>%s</div>", sm)
            else:
                zi, yi= "", ""
                if line.startswith("`"):
                    yi = line #無字
                elif line.count("`") == 2:
                    zi, yi = line.split("`", 1)
                if zi or yi:
                    zi = parse(zi)
                    yi = parse(yi)
                    if not yi:
                        zi_single += zi
                        continue
                    if zi:
                        zi = zi_single + zi
                        zi_single = ""
                        yi = break_yi(yi)
                    zi_count+=1
                    if zi_count == 1:
                        sd_title = sd
                        if not zi:
                            sd_title = yi
                            yi = ""
                        if len(sd_title) == 2:
                            sd_title = sd[0]+"<br/>" + sd[1]
                            append("<div class=sd2>%s</div>", sd_title)
                        else:
                            append("<div class=sd>%s</div>", sd_title)
                        append("<div class=zy><div class=zi1>%s</div><div class=yi>%s</div></div>",(zi, yi))
                    else:
                        zi = re.sub("(.)[\\+\\^]", lambda x: "<span class=new>%s</span>" % x.group(1), zi)
                        append("<div class=zy><div class=zi>%s</div><div class=yi>%s</div></div>",(zi, yi))

    target = open("docs/" + os.path.basename(filename).replace(".md", ".html"), "w", encoding="U8")
    target.write(template % ("\n".join(lines)))
    target.close()

def copy_readme():
    target = open("README.md", "w", encoding="U8")
    target.write(open("wiki/Home.md", encoding="U8").read().replace("/osfans/xu/wiki/", "https://osfans.github.io/xu/"))
    target.close()

copy_readme()
for filename in glob.glob("wiki/??.md"):
   md2html(filename)
