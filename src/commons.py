import json, sys, urllib.request, urllib.parse, re, os
subjects = {
 'shinjuku':'Shinjuku Gyoen greenhouse',
 'jindai':'Jindai Botanical Garden chrysanthemum',
 'omiya':'Omiya Bonsai Art Museum',
 'koishikawa':'Koishikawa Botanical Garden autumn',
 'rikugien':'Rikugien autumn',
 'murinan':'Murin-an garden',
 'eikando':'Eikan-do autumn leaves',
 'tofukuji':'Tofuku-ji Tsutenkyo autumn',
 'tofukuji_hojo':'Tofuku-ji Hojo garden checkerboard moss',
 'kyotobg':'Kyoto Botanical Garden conservatory',
 'katsura':'Katsura Imperial Villa garden',
 'saihoji':'Saiho-ji moss garden',
 'ryoanji':'Ryoan-ji rock garden',
 'zuihoin':'Zuiho-in garden Daitoku-ji',
 'kitano':'Kitano Tenmangu autumn leaves momiji',
 'shisendo':'Shisen-do garden',
 'tenryuji':'Tenryu-ji Sogenchi garden',
 'arashiyama':'Arashiyama bamboo grove',
 'ginkakuji':'Ginkaku-ji sand garden Ginshadan',
 'kenrokuen':'Kenrokuen yukitsuri',
 'nomura':'Nomura samurai house garden Kanazawa',
 'hamarikyu':'Hama-rikyu garden pine',
 'okochi':'Okochi Sanso garden',
 'kodaiji':'Kodai-ji garden autumn',
}
UA={'User-Agent':'MomijiItinerary/1.0 (personal travel page; contact: rancematthew@gmail.com)'}
out={}
for k,q in subjects.items():
    params={'action':'query','generator':'search','gsrsearch':q+' filetype:bitmap','gsrnamespace':'6','gsrlimit':'8','prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':'400','format':'json'}
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
    try:
        r=urllib.request.Request(url,headers=UA); data=json.load(urllib.request.urlopen(r,timeout=30))
    except Exception as e:
        print(k,'ERR',e); continue
    pages=data.get('query',{}).get('pages',{})
    items=[]
    for p in sorted(pages.values(), key=lambda p:p.get('index',99)):
        ii=p['imageinfo'][0]; md=ii.get('extmetadata',{})
        lic=md.get('LicenseShortName',{}).get('value',''); 
        if ii['width']<1200 or ii['height']<700: continue
        items.append({'title':p['title'],'thumb':ii['thumburl'],'url':ii['url'],'w':ii['width'],'h':ii['height'],'license':lic,'artist':re.sub('<[^>]+>','',md.get('Artist',{}).get('value','')).strip()[:80],'desc':re.sub('<[^>]+>','',md.get('ImageDescription',{}).get('value',''))[:100]})
    out[k]=items
    print(k,len(items))
json.dump(out,open('img/candidates.json','w'),indent=1,ensure_ascii=False)
