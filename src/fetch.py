import json, urllib.request, io, time, base64
from PIL import Image, ImageOps
UA={'User-Agent':'MomijiItinerary/1.0 (personal; rancematthew@gmail.com)'}
c=json.load(open('img/candidates.json'))
picks={'shinjuku':('shinjuku',1),'jindai':('jindai3',6),'rikugien':('rikugien',2),'omiya':('omiya',3),'koishikawa':('koishikawa',0),
'eikando':('eikando',0),'murinan':('murinan',4),'tofukuji':('tofukuji',0),'kyotobg':('kyotobg',1),'saihoji':('saihoji',2),'katsura':('katsura',2),'kodaiji':('kodaiji',0),
'ryoanji':('ryoanji',1),'zuihoin':('zuihoin',0),'kitano':('kitano',1),'shisendo':('shisendo',1),'tenryuji':('tenryuji',1),'arashiyama':('arashiyama',2),'ginkakuji':('ginkakuji',1),
'kenrokuen':('kenrokuen',1),'nomura':('nomura',0),'hamarikyu':('hamarikyu',0)}
meta={}
for name,(k,i) in picks.items():
    it=c[k][i]
    # request a 1400px-wide server-side thumb to avoid huge originals
    import urllib.parse; url='https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(it['title'][5:])+'?width=1400'
    for attempt in range(3):
        try:
            b=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90).read(); break
        except Exception as e:
            print('retry',name,e); time.sleep(3)
    im=Image.open(io.BytesIO(b)); im=ImageOps.exif_transpose(im).convert('RGB')
    im.thumbnail((1400,1400))
    buf=io.BytesIO(); im.save(buf,'JPEG',quality=70,optimize=True,progressive=True)
    data=buf.getvalue(); open(f'img/{name}.jpg','wb').write(data)
    meta[name]={'title':it['title'],'license':it['license'],'artist':it['artist'],'page':'https://commons.wikimedia.org/wiki/'+it['title'].replace(' ','_'),'w':im.width,'h':im.height,'kb':len(data)//1024}
    print(name,im.size,len(data)//1024,'KB',it['license'],it['artist'][:30])
    time.sleep(0.8)
json.dump(meta,open('img/meta.json','w'),indent=1,ensure_ascii=False)
print('total KB',sum(m['kb'] for m in meta.values()))
