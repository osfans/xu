#!/usr/bin/env python3

import re, os, glob, datetime

from collections import defaultdict
import fileinput

template = "%s\n"
yms=["on","an","en","aen","un","in","i","in","un","v","ae","o","a","ien","eu"]
sds={"陰平":1,"陽平":2,"上":3,"去":5,"入":7}
lines = list()
zy=dict()
zs=set()
ys=set()

def parse(s):
    s = s.strip().strip("`").replace("〜", "～").replace("※", "")
    s = re.sub('(.([\d\*]=?)?)([+^])', r'\1', s)
    s = re.sub(r'[+^？]', r'', s)
    s = re.sub(r"(.)(\d)=", r'\1', s)
    if "（" in s:
        s = re.sub("(.)（(.+?)❌）", r'\1', s)
        #s = re.sub("●（(.+?)）", r'\1', s)
        s = re.sub("=（(.+?)）", r'', s)
        s = re.sub(r"(.)(\*)（(.+?)）", r'●（\3）', s)
        s = re.sub("([^●])（(.+?)）", r'\1', s)
    s = s.replace("=","")
    return s

def get_py(s,m,d):
    py = s+m+str(sds[d])
    py = py.replace('0','').replace('yin','iun').replace('uin','ui').replace('yi','y').replace('n7','h7')
    py = re.sub('(?<=[zcs])i(?=\d)', 'z', py)
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
                    yi = yi.replace('仝', '同')
                    if yi.endswith('同上') or '同上 ' in yi:
                        yi = yi.replace('同上', '同'+last_zi)
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
    r'z\b':'ɿ',
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
    'a(?=\d)?$':'ɑ',
    'iu':'yu',
    'eu':'ɤɯ',
    'u(?=[\dnh])?$':'ʊ',
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

def parsezi(zi):
    zi = zi.replace(" ", "")
    groups = map(lambda x:x[0], re.finditer("((.)(（.*）)?)", zi))
    return " ".join(groups)
    
target=open("docs/xu.csv","w",encoding="U8")
for filename in range(1,16):
   md2mb("wiki/%02d.md" % filename)

ym=-1
sy=""
count=0
for py in sorted(zy.keys(),key=pykey):
    ymt = pykey(py)[0]
    if ymt!=ym:
        ym=ymt
    if py[:-1]!=sy:
        sy=py[:-1]
    ipa = py2ipa(py)
    for zi,yi in zy[py]:
        target.write('"%d","%s","%s","%s"\n'%(count, parsezi(zi), py, yi))
        count+=1
target.close()
