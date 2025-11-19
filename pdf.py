#!/usr/bin/env python3

import re, os, glob, datetime

from collections import defaultdict
import fileinput
from md2pdf.core import md2pdf

def hex2chr(uni):
    "把unicode轉換成漢字"
    return chr(int(uni[2:], 16))

def append(dic, items):
    "添加到字典"
    for each in items:
        py = norm(each)
        if py not in dic:
            dic.append(py)

def order(py):
    sm = "b p m f d t n l g k h j q x zh ch sh r z c s y w".split(" ")
    s = 0
    if py[:2] in sm: s = 2
    elif py[0] in sm: s = 1
    return sm.index(py[:s]) if s > 0 else -1, py

def norm(py):
    if py == "wòng": return "ong"
    tones="āáǎàēéěèīíǐìōóǒòūúǔùǘǚǜ"
    toneb="aaaaeeeeiiiioooouuuuüüü"
    for i in py:
        if i in tones:
            py=py.replace(i,toneb[tones.index(i)])
    py=re.sub("(?<=[zcs])h","",py)
    py=re.sub('(?<=[zcs])i$', 'z', py)
    py=py.replace('yu','ü').replace('y','i').replace('ii','i').replace('ü','y')
    py=re.sub('(?<=[jqx])u','y',py)
    py=py.replace('w','u').replace('uu','u')
    py=re.sub('(?<=[bpmf])eng','on',py)
    py=py.replace('ing','ien').replace('in','ien').replace('un','uen')
    py=re.sub('ian$','in',py)
    py=re.sub('(uan|uo)$','un',py)
    py=re.sub('an$','aen',py)
    py=re.sub('(?<=[bpmf])o$','un',py)
    py=re.sub('(ie|ei)$','in',py)
    py=re.sub('(?<=[bpmfdntlgkhzcsr])u$','v',py)
    py=re.sub('^u$','v',py)
    py=py.replace('ng','n').replace('ai','ae').replace('ao','o').replace('er','o').replace('ou','eu').replace('r','l')
    py=re.sub('(?<=[dntl])uen$','en',py)
    py=re.sub('(?<=[dntl])ui$','in',py)
    py=re.sub('(?<=[zcs])e$','in',py)
    return py

template = "%s\n"
yms=["on","an","en","aen","un","in","i","in","un","v","ae","o","a","ien","eu"]
sds={"陰平":1,"陽平":2,"上":3,"去":5,"入":7}
lines = list()
zy=dict()
zs=set()
ys=set()

def parse(s):
    #s = s.replace("𠀍","&#131085;").replace("𰀀","&#196608;").replace("𠀟", "&#131103;")
    s = s.strip().strip("`").replace("〜", "～").replace("※", "")
    s = re.sub(r'(.([\d\*]=?)?)([+^])', r'<span class=new>\1</span>', s)
    s = re.sub(r'[+^？]', r'', s)
    s = re.sub(r"(.)(\d)=", r'<span class=f\2>\1</span>', s)
    s = re.sub(r"(.)(\*)", r'<span class=pua>\1</span>\2', s)
    if "（" in s:
        s = re.sub("(.)（(.+?)❌）", r'\1<strike>\2</strike>', s)
        s = re.sub("□（(.+?)）", r'<u>\1</u>', s)
        s = re.sub("（(.+?)）", r'<sub>\1</sub>', s)
    return s

def get_py(s,m,d):
    py = s+m+str(sds[d])
    py = py.replace('0','').replace('yin','iun').replace('uin','ui').replace('yi','y').replace('n7','h7')
    py = re.sub(r'(?<=[zcs])i(?=\d)', 'z', py)
    return py

def md2mb(filename):
    sm = ""
    ym = yms[int(filename[-5:-3])-1]
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
            else:
                zi, yi= "", ""
                if line.startswith("`"):#無字
                    continue
                elif line.count("`") == 2:
                    zi, yi = line.split("`", 1)
                if zi or yi:
                    zi = parse(zi)
                    yi = parse(yi)
                    global zs,ys
                    zs=zs.union(set(zi))
                    ys=ys.union(set(yi))
                    #if not yi:
                    #    zi_single += zi
                    #    continue
                    if zi:
                        zi = zi_single + zi
                        zi_single = ""
                    zi_count+=1
                    if zi_count == 1:
                        if not zi:
                            continue
                    #yi = yi.replace('仝', '同')
                    #if yi.endswith('同上'):
                    #    yi = yi.replace('同上', '同'+last_zi)
                    last_zi = zi
                    py=get_py(sm,ym,sd)
                    if py.endswith('eu7'):
                        continue
                    if py in zy:
                        zy[py].append([zi,yi])
                    else:
                        zy[py]=[[zi,yi]]

yml=['z', 'i', 'v', 'y', 
'ae', 'iae', 'uae', 
'u',
'ii','ui', 
'a', 'ia', 'ua',
'eu', 'ieu', 
'o', 'io', 

'aen', 'iaen', 'uaen', 
'un', 'iun', 
'in', 
'an', 'ian', 'uan', 
'en', 'ien', 'uen', 'yen', 
'on', 'ion', 

'aeh', 'iaeh', 'uaeh', 
'uh', 'iuh', 
'ih',
'ah', 'iah', 'uah', 
'eh', 'ieh', 'ueh', 'yeh',
'oh', 'ioh', 
]
sml='bpmfdtnlzcsjqxgkhØ'

ipas={
    r'z(\d?)$':'ɿ\\1',
    r'\bp':'pʰ',
    r'\bb':'p',
    r'\bt':'tʰ',
    r'\bd':'t',
    r"\bz":"ʦ",
    r"\bc":"ʦʰ",
    r'\bj':'ʨ',
    r'\bq':'ʨʰ',
    r'\bx':'ɕ',
    r'\bk':'kʰ',
    r'\bg':'k',
    r'\bh':'x',
    'ae':'ɛ',
    r'a(?=\d)?$':'ɑ',
    'iu':'yu',
    'eu':'ɤɯ',
    r'u(?=[nh]\d?)':'ʊ',
    '(?<=[iu])i':'ɪ',
    'i(?=[nh])':'ɪ',
    'v':'ʋ',
    'e':'ə',
    'o':'ɔ',
    '(?<=ɔ)n':'ŋ',
    '(?<=[aɪʊɛ])n':'̃',
    '1':'³¹',
    '2':'²¹³',
    '3':'⁵⁵',
    '5':'³⁵',
    '7':'⁵',
    'h':'ʔ'}

def pykey(py):
    sm=''
    if py[0] in sml:
        sm=py[0]
    ym=py[len(sm):-1]
    sd=py[-1]
    if sm == '': sm='Ø'
    return yml.index(ym),sml.index(sm),sd

def py2ipa(py):
    for a,b in ipas.items():
        py=re.sub(a,b,py)
    return py
    
contents = [open("README.md", encoding="U8").read()]
contents[0] = contents[0].replace("[在線版本]", str(datetime.date.today()) + "\n\n" + "[在線版本]")
for filename in range(1,16):
   md2mb("wiki/%02d.md" % filename)

ym=-1
sy=""
for py in sorted(zy.keys(),key=pykey):
    ymt = pykey(py)[0]
    if ymt!=ym:
        ym=ymt
        contents.append("# <span class=py>%s</span> <span class=ipa>[%s]</span>\n" % (yml[ym], py2ipa(yml[ym])))
    if py[:-1]!=sy:
        sy=py[:-1]
        if py.endswith("7"):
            contents.append("## <span class=py>%s</span> <span class=ipa>[%s]</span>\n" % (sy, py2ipa(py)))
        else:
            contents.append("## <span class=py>%s</span> <span class=ipa>[%s]</span>\n" % (sy, py2ipa(sy)))
    if not py.endswith("7"):
        contents.append("%s <span class=ipa>[%s]</span>\n"%(py.replace("7",""),py2ipa(py)))
    for zi,yi in zy[py]:
        contents.append("%s <span class=sub>%s</span> "%(zi,yi))
    contents.append("\n")
md2pdf("xu.pdf", md_content="\n".join(contents), css_file_path="pdf.css")