#!/usr/bin/env python3

import re

sm = ""
sd = ""
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
            append("<div class=sd>%s</div>", sd[0]+"<br/>" + sd[1] if len(sd) == 2 else sd)
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

.sd, .zy, .zi, .yi {
  cursor: text;
  position: static;
  float: left;
  text-align: center;
}

.sd {
  font-size: 10px;
  line-height: 10px;
  margin-left: 10px;
  margin-right: 10px;
  clear: both;
}

.zy {
  line-height: 20px;
  margin-left: 10px;
  margin-right: 10px;
}

.zi {
  margin-top: 20px;
  font-size: 20px;
  line-height: 20px;
}

.yi {
  margin-top: 8px;
  margin-bottom: 8px;
  font-size: 10px;
  line-height: 12px;
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
