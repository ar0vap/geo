# Сборка облегчённой geosite.dat / geoip.dat для iOS (лимит памяти ~50 МБ)
import sys
def varint(b, i):
    r=0; s=0
    while True:
        c=b[i]; i+=1; r|=(c&0x7f)<<s; s+=7
        if not c&0x80: return r,i
def enc(n):
    out=bytearray()
    while True:
        b=n&0x7f; n>>=7
        if n: out.append(b|0x80)
        else: out.append(b); return bytes(out)
def fields(b):
    i=0
    while i<len(b):
        k,i=varint(b,i); f,t=k>>3,k&7
        if t==0: v,i=varint(b,i)
        elif t==2:
            l,i=varint(b,i); v=b[i:i+l]; i+=l
        elif t==5: v=b[i:i+4]; i+=4
        elif t==1: v=b[i:i+8]; i+=8
        yield f,v
def ld(tag, payload): return enc((tag<<3)|2)+enc(len(payload))+payload
def entry(code, domain_blobs): return ld(1, ld(1, code.encode()) + b''.join(ld(2, d) for d in domain_blobs))
def dom(value, typ=2): return enc((1<<3)|0)+enc(typ)+ld(2, value.encode())
def code_of(e):
    for f,v in fields(e):
        if f==1: return v.decode()

KEEP = {'category-ru','yandex','vk','mailru','ru-available-only-inside'}
RU_ZONES = ('.ru','.su','.xn--p1ai')
KEYWORDS = ('youtube','youtu.be','googlevideo','ytimg','ggpht','gstatic','googleapis','googleusercontent',
            'google','gvt1','gvt2','facebook','fbcdn','instagram','cdninstagram','whatsapp','twitter','twimg',
            'x.com','discord','linkedin','licdn','soundcloud','spotify','netflix','tiktok','medium.com')
ADS = ['doubleclick.net','googlesyndication.com','googleadservices.com','adservice.google.com',
       'an.yandex.ru','yabs.yandex.ru','adfox.ru','ads.adfox.ru','mytarget.ru','ad.mail.ru','rs.mail.ru',
       'adriver.ru','criteo.com','criteo.net','taboola.com','outbrain.com','adnxs.com','amazon-adsystem.com',
       'adcolony.com','applovin.com','unityads.unity3d.com','moatads.com','scorecardresearch.com',
       'appsflyer.com','adjust.com','app-measurement.com','ads.vk.com','ad.vk.com','ads.tiktok.com']

src_site, src_ip, out_site, out_ip = sys.argv[1:5]
data=open(src_site,'rb').read()
out=bytearray(); stats={}
for f,e in fields(data):
    if f!=1: continue
    c=code_of(e); cl=c.lower()
    if cl in KEEP:
        out+=ld(1,e); stats[c]='all'
    elif cl=='ru-blocked':
        kept=[]
        for f2,v in fields(e):
            if f2!=2: continue
            val=''
            for f3,v3 in fields(v):
                if f3==2: val=v3.decode(errors='replace')
            if val.endswith(RU_ZONES) or any(k in val for k in KEYWORDS):
                kept.append(v)
        out+=entry('RU-BLOCKED', kept); stats[c]=len(kept)
out+=entry('CATEGORY-ADS-ALL', [dom(d) for d in ADS]); stats['CATEGORY-ADS-ALL']=len(ADS)
open(out_site,'wb').write(out)
ipdata=open(src_ip,'rb').read(); ipout=bytearray()
for f,e in fields(ipdata):
    if f==1 and code_of(e).lower() in ('ru','private'): ipout+=ld(1,e)
open(out_ip,'wb').write(ipout)
print(stats, 'geosite', len(out), 'geoip', len(ipout))
