import sys,os,struct,glob,re
sys.path.insert(0,os.path.dirname(__file__))
import lz, numpy as np
from PIL import Image
BASE=0x2d4000
def blocks():
    """yield (name, file, dlg_off(op offset), ev_off) for every mission dialog pack"""
    res=[]
    for f in sorted(glob.glob('disc/DIR00/*'))+sorted(glob.glob('disc/DIR03/*')):
        d=open(f,'rb').read(); dl=ev=None
        for m in re.finditer(rb'\x0c\x00[\x20-\x2f]..\x00\x2d[\x40\xc0]\x00',d,re.S):
            dst=int.from_bytes(d[m.start()+5:m.start()+9],'big')
            if dst==0x2d4000 and dl is None: dl=m.start()
            if dst==0x2dc000 and ev is None: ev=m.start()
        if dl is not None: res.append((os.path.basename(f),f,dl,ev))
    return res
def src_of(d,op): return int.from_bytes(d[op+1:op+5],'big')-0x200000+4
def line_img(b):
    w=np.frombuffer(b,'>u2')
    return np.array([[(c>>y)&1 for c in w] for y in range(16)],np.uint8)
def events(ev):
    """parse event script -> list of (offset, op, arg16, ptr)"""
    out=[]
    for i in range(0,len(ev)-7,4):
        h=ev[i:i+2]
        if h in (b'\x03\xa8',b'\x04\xa8'):
            p=int.from_bytes(ev[i+4:i+8],'big')
            if BASE<=p<0x2dc000 and (p-BASE)%2==0: out.append((i,ev[i],int.from_bytes(ev[i+2:i+4],'big'),p))
    return out
def load(name):
    for n,f,dl,ev in blocks():
        if n==name:
            d=open(f,'rb').read()
            dlg,_=lz.decode(d,src_of(d,dl))
            evb=lz.decode(d,src_of(d,ev))[0] if ev is not None else None
            return d,dlg,evb
def is_line(b):
    w=np.frombuffer(b,'>u2')
    return bool(np.all(w<0x2000))
def line_region(dlg,ev):
    if ev is not None:
        E=events(ev)
        if E:
            st=min(p for *_,p in E)-BASE
            return st
    st=len(dlg)
    while st-0x150>=0 and is_line(dlg[st-0x150:st]): st-=0x150
    return st
import hashlib
def lid(b): return hashlib.md5(b).hexdigest()[:8]
