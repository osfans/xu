#!/usr/bin/env python3

import re

sm = ""
sd = ""
zi_count = 0
lines = list()

def append(fmt, s):
    #print(s)
    lines.append(fmt % s)

for line in open("wiki/12.md", encoding="U8"):
    line = line.strip()
    if line:
        if line.startswith(">"):
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
            line = line.replace("～", "—").replace("` ","`\n")
            fields = line.split("\n")
            for line in fields:
                zi, yi= "", ""
                if " " not in line:
                    if line.startswith("`"):
                        yi = line.strip("`")
                    else:
                        zi = line
                elif line.count("`") == 2:
                    zi, yi = line.split("`", 1)
                    zi = zi.strip()
                    yi = yi.strip("`").replace(" ", "")
                if zi or yi:
                    #zi = zi.replace("?", "").replace("=", "")
                    #yi = yi.replace("?", "").replace("=", "")
                    if zi:
                        n = len(yi)
                        if 0 < n < 4:
                            yi = yi + (4-n) * "　"
                            n = 4
                        if n % 2 == 1:
                           yi += "　"
                        if n > 0:
                            yi = yi[:(n+1)//2]+"<br/>"+yi[(n+1)//2:]
                    zi_count+=1
                    if zi_count == 1:
                        sd_title = sd
                        if yi.startswith("入聲"):
                            sd_title = yi
                            yi = ""
                        if len(sd_title) == 2:
                            sd_title = sd[0]+"<br/>" + sd[1]
                            append("<div class=sd2>%s</div>", sd_title)
                        else:
                            append("<div class=sd>%s</div>", sd_title)
                        append("<div class=zy><div class=zi1>%s</div><div class=yi>%s</div></div>",(zi, yi))
                    else:
                        append("<div class=zy><div class=zi>%s</div><div class=yi>%s</div></div>",(zi, yi))

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
  font-size: 28px;
  border-left: 1px solid #cccccc;
  margin: 0 5px;
  cursor: text;
  position: static;
  clear: both;
  align: right;
}

.sd, .sd2, .zy, .zi, .zi1, .yi {
  cursor: text;
  position: static;
  float: left;
  text-align: center;
  margin-left: 10px;
  margin-right: 10px;
  line-height: 10px;
  padding-bottom: 5px;
}

.sd, .sd2 {
  padding-right: 15px;
  padding-bottom: 0px;
  font-size: 10px;
  clear: both;
}

.sd2 {
  padding-right: 10px;
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
  font-size: 10px;
}

.clear {
  clear: both;
}

</style>
<title>徐氏類音字彙</title>

</head>
<body>
%s
</body>
</html>
"""

target = open("index.html", "w", encoding="U8")
target.write(template % ("\n".join(lines)))
target.close()
