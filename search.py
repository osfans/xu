#!/usr/bin/env python3
"""Generate docs/index.html — a searchable static page for 徐氏類音字彙."""

import json, re

# Load all entries from xu.tsv: zi, py, ipa, yi (ipa excluded from html DATA)
entries = []
with open("xu.tsv", encoding="U8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 4:
            zi, py, ipa, yi = parts
            entries.append([zi, py, yi])

data_json = json.dumps(entries, ensure_ascii=False)

HTML = """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>徐氏類音字彙</title>
<style>
* { box-sizing: border-box; }
body {
  font-family: 'Noto Sans KR', 'Noto Sans CJK KR', 'Source Han Sans', sans-serif;
  margin: 0; padding: 0 1em 2em;
  background: #faf9f7; color: #222;
}
h1 { text-align: center; font-size: 1.4em; margin: .6em 0 .4em; }
#bar {
  display: flex; gap: .5em; align-items: center; max-width: 640px;
  margin: 0 auto .8em; padding: .4em 0;
  position: sticky; top: 0; background: #faf9f7; z-index: 10;
}
#q {
  flex: 0 1 320px; padding: .4em .6em; font-size: 1.1em;
  border: 1px solid #bbb; border-radius: 4px;
  font-family: inherit;
}
#count {
  line-height: 2.2em; color: #888; font-size: .85em; white-space: nowrap;
}
table {
  width: 100%; max-width: 640px; margin: 0 auto;
  border-collapse: collapse; font-size: 1em;
}
th {
  text-align: left; padding: .3em .5em;
  border-bottom: 2px solid #888; color: #555; font-weight: normal;
}
td {
  padding: .35em .5em; border-bottom: 1px solid #e8e6e2;
  vertical-align: top;
}
td.zi { font-size: 1.3em; white-space: nowrap; }
td.py { color: #555; white-space: nowrap; }
.ipa { font-family: 'Charis SIL', 'Noto Sans', sans-serif; color: #999; font-size: .85em; }
td.yi { color: #333; }
tr:hover td { background: #f0ede8; }
mark { background: #ffe58a; border-radius: 2px; }
#none { text-align: center; color: #aaa; padding: 2em; display: none; }
</style>
</head>
<body>
<h1>徐氏類音字彙</h1>
<div id="bar">
  <label style="white-space:nowrap;font-size:1.1em;color:#555"><input id="zionly" type="checkbox"> 僅字頭</label>
  <input id="q" type="search" placeholder="搜索字頭、拼音或釋義…" autofocus>
  <span id="count"></span>
</div>
<table id="tbl">
  <thead><tr><th>字頭</th><th>拼音</th><th>釋義</th></tr></thead>
  <tbody id="tbody"></tbody>
</table>
<div id="none">無匹配結果</div>
<script>
const DATA = PLACEHOLDER_DATA;

const tbody = document.getElementById('tbody');
const countEl = document.getElementById('count');
const noneEl = document.getElementById('none');
const zionlyEl = document.getElementById('zionly');
const qEl = document.getElementById('q');

const SM = {'b':'p','p':'pʰ','m':'m','f':'f','d':'t','t':'tʰ','n':'n','l':'l','z':'ts','c':'tsʰ','s':'s','j':'tɕ','q':'tɕʰ','x':'ɕ','g':'k','k':'kʰ','h':'x','ng':'ŋ','':''}
const YM = {'ae':'e','ieh':'iəʔ','ii':'iɪ̃','eh':'əʔ','io':'iɔ','ieu':'iɤɯ','u':'ʊ̃','v':'uᵝ','en':'ən','a':'ɑ','on':'ɔŋ','an':'ã','oh':'ɔʔ','i':'iᶽ','ien':'in','ion':'iɔŋ','ah':'aʔ','ih':'iʔ','y':'yᶽ','ui':'uɪ','uae':'ue','aeh':'ɛʔ','in':'iɪ̃','ia':'iɑ','z':'ɿ','uh':'ʊʔ','aen':'ɛ̃','eu':'ɤɯ','iah':'iaʔ','ueh':'uəʔ','iae':'ie','iuh':'yʊʔ','yen':'yn','ian':'iã','iun':'yʊ̃','un':'ʊ̃','o':'ɔ','uan':'uã','ua':'uɑ','uen':'uən','ioh':'iɔʔ','iaen':'iɛ̃','uaen':'uɛ̃','uaeh':'uɛʔ','iaeh':'iɛʔ','uah':'uaʔ','yeh':'yəʔ','ya':'yɑ','':''}
function py2ipa(py) {
  const m = py.match(/^([^aeiouvy]?g?)/);
  const sm = m ? m[1] : '';
  const sd = /[12357]$/.test(py) ? py.slice(-1) : '';
  const ym = py.slice(sm.length, py.length - sd.length);
  return (SM[sm] ?? sm) + (YM[ym] ?? ym) + sd;
}
function esc(s) {
  return s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}
function render(q) {
  const raw = q.trim();
  const low = raw.toLowerCase();
JS_PAT_PLACEHOLDER
  // split tokens by space; each token must match at least one field
  const tokens = raw ? raw.split(' ').filter(t => t) : [];
  function highlight(s, toks) {
    let out = esc(s);
    for (const t of toks) {
      const re = new RegExp('(' + t.replace(HIGHLIGHT_ESC_PLACEHOLDER, HIGHLIGHT_REPL_PLACEHOLDER) + ')', 'gi');
      out = out.replace(re, '<mark>$1</mark>');
    }
    return out;
  }
  let rows = '', n = 0;
  if (raw) for (const [zi, py, yi] of DATA) {
    if (zionlyEl.checked) {
      // any char in raw (excluding spaces) matches zi
      if (![...raw].filter(ch => ch !== ' ').some(ch => zi.includes(ch))) continue;
    } else {
      // every token must appear in zi, py (prefix) or yi
      if (!tokens.every(t => zi.includes(t) || py.toLowerCase().startsWith(t.toLowerCase()) || yi.includes(t))) continue;
    }
    n++;
    const hp = highlight(py, tokens);
    const hzi = highlight(zi, tokens);
    const hyi = highlight(yi, tokens);
    rows += '<tr><td class=zi>' + hzi + '</td><td class=py>' + hp
      + ' <span class=ipa>/' + esc(py2ipa(py)) + '/</span></td><td class=yi>' + hyi + '</td></tr>';
  }
  tbody.innerHTML = rows;
  countEl.textContent = (low ? n : DATA.length) + ' 條';
  noneEl.style.display = (n === 0 && low) ? '' : 'none';
}

render('');
qEl.addEventListener('input', () => render(qEl.value));
zionlyEl.addEventListener('change', () => render(qEl.value));
</script>
</body>
</html>
"""

JS_PAT = (
    "  const pat = low ? new RegExp('(' + low.replace(/[.*+?^${}()|["
    + chr(92) + chr(93) + chr(92) + chr(92)
    + "]/g, '" + chr(92) + chr(92) + "$&') + ')', 'gi') : null;"
)

HIGHLIGHT_ESC = "/[.*+?^${}()|[" + chr(92) + chr(93) + chr(92) + chr(92) + "]/g"
HIGHLIGHT_REPL = "'" + chr(92) + chr(92) + "$&'"

html = HTML.replace("PLACEHOLDER_DATA", data_json).replace("JS_PAT_PLACEHOLDER", JS_PAT).replace("HIGHLIGHT_ESC_PLACEHOLDER", HIGHLIGHT_ESC).replace("HIGHLIGHT_REPL_PLACEHOLDER", HIGHLIGHT_REPL)

with open("index.html", "w", encoding="U8") as f:
    f.write(html)

print(f"Generated docs/index.html ({len(entries)} entries)")
