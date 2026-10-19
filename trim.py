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
def entries(b):
    i=0
    while i<len(b):
        k,i=varint(b,i); t=k&7
        assert t==2
        l,i=varint(b,i); yield k>>3, b[i:i+l]; i+=l
def code_of(e):
    for f,v in entries_any(e):
        if f==1: return v.decode()
def entries_any(b):
    i=0
    while i<len(b):
        k,i=varint(b,i); f,t=k>>3,k&7
        if t==0: v,i=varint(b,i)
        elif t==2:
            l,i=varint(b,i); v=b[i:i+l]; i+=l
        elif t==5: v=b[i:i+4]; i+=4
        elif t==1: v=b[i:i+8]; i+=8
        yield f,v
src, dst, want = sys.argv[1], sys.argv[2], set(x.lower() for x in sys.argv[3].split(','))
data=open(src,'rb').read()
out=bytearray(); found=[]; allcodes=[]
for f,e in entries(data):
    c=code_of(e); allcodes.append(c)
    if c and c.lower() in want:
        out+=enc((1<<3)|2)+enc(len(e))+e; found.append(c)
open(dst,'wb').write(out)
print('found', found, 'missing', sorted(want-set(x.lower() for x in found)), 'size', len(out))
