import re, base64, io, html
from fontTools import subset
from fontTools.ttLib import TTFont

src=open('momiji.src.html',encoding='utf-8').read()
text=html.unescape(re.sub(r'<[^>]+>',' ',src))
chars=set(text)|set(chr(c) for c in range(0x20,0x7f))|{'—','–','’','“','”','×','·','→','◐','…'}
# kana + fullwidth punctuation for jp text
chars|=set(chr(c) for c in range(0x3040,0x30ff))|{'、','。','？','・'}
def sub(path, out_flavor='woff2', latin_only=False):
    f=TTFont(path)
    cmap=f.getBestCmap()
    cs=[c for c in chars if ord(c) in cmap and (not latin_only or ord(c)<0x2500)]
    opts=subset.Options(); opts.flavor=out_flavor; opts.layout_features=['kern','liga','palt','pnum','tnum','onum','lnum']
    opts.hinting=False; opts.desubroutinize=True; opts.name_IDs=['*']; opts.notdef_outline=True
    s=subset.Subsetter(opts); s.populate(text=''.join(cs)); s.subset(f)
    b=io.BytesIO(); f.save(b); return base64.b64encode(b.getvalue()).decode()
faces=[]
def face(fam,file,weight,style,latin_only=False):
    d=sub('fonts/'+file,latin_only=latin_only)
    faces.append(f"@font-face{{font-family:'{fam}';font-weight:{weight};font-style:{style};font-display:swap;src:url(data:font/woff2;base64,{d}) format('woff2');}}")
    print(fam,weight,style,len(d)//1024,'KB')
face('Cormorant','cg-300.ttf',300,'normal',True)
face('Cormorant','cg-300i.ttf',300,'italic',True)
face('Cormorant','cg-400.ttf',400,'normal',True)
face('Cormorant','cg-400i.ttf',400,'italic',True)
face('Cormorant','cg-500.ttf',500,'normal',True)
face('Shippori','sm-400.ttf',400,'normal')
face('ZenKaku','zk-400.ttf',400,'normal')
face('ZenKaku','zk-500.ttf',500,'normal')
face('ZenKaku','zk-700.ttf',700,'normal')
import json
emb=json.load(open('img/embed.json'))
def figure(m):
    kind,name,cap=m.group(1),m.group(2),m.group(3)
    e=emb[name]; cls='plate' if kind=='IMG' else 'fig'
    lic=e['license']; art=e['artist'] or 'Wikimedia Commons'
    cr=f'<span class="cr">Photo: {art} · {lic} · <a href="{e["page"]}" target="_blank" rel="noopener">Wikimedia Commons</a></span>'
    return f'<figure class="{cls} reveal"><img src="{e["data"]}" width="{e["w"]}" height="{e["h"]}" alt="{cap.split(" — ")[0]}" loading="lazy" decoding="async"><figcaption>{cap}{cr}</figcaption></figure>'
src=re.sub(r'<!--(IMG|FIG):([a-z0-9]+)\|(.*?)-->',figure,src)
RATE=215.0
def gbp(y):
    v=int(y.replace(',',''))/RATE
    if v<10: return ('£%.1f'%round(v*2)/2 if False else '£%.1f'%v).replace('.0','') if v<10 else ''
    return f'£{round(v):,}'
def yen(m):
    a,b=m.group(1),m.group(3)
    if b: return f'¥{a}–{b} <span class="gbp">(~{gbp(a)}–{gbp(b)[1:]})</span>'
    return f'¥{a} <span class="gbp">(~{gbp(a)})</span>'
# only convert inside text, not inside tags/attributes: split on tags
parts=re.split(r'(<[^>]+>)',src)
parts=[p if p.startswith('<') else re.sub(r'¥(\d{1,3}(?:,\d{3})*|\d+)(–(\d{1,3}(?:,\d{3})*|\d+))?(?![\d,]\d)',yen,p) for p in parts]
src=''.join(parts)
out=src.replace('/*FONTS*/','\n'.join(faces))
open('momiji.html','w',encoding='utf-8').write(out)
print('total',len(out)//1024,'KB')
