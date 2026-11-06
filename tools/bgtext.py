"""generic text-BG rebuild: segments of original image replaced by Korean text"""
import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from PIL import Image,ImageDraw
import bgr,bgk
def index_img(d,off,W):
    m=np.frombuffer(d[off:],'>u2'); m=m[:len(m)//W*W].reshape(-1,W); H=m.shape[0]
    img=np.zeros((H*16,W*16),np.uint8)
    for r in range(H):
        for c in range(W):
            a=0x800+int(m[r,c])*0x80; b=np.frombuffer(d[a:a+256],np.uint8)
            img[r*16:r*16+16,c*16:c*16+16]=b.reshape(2,2,8,8).transpose(0,2,1,3).reshape(16,16)
    return img
def segments(img,th=0):
    rows=img.max(1)>th; segs=[];s=None
    for y,v in enumerate(list(rows)+[False]):
        if v and s is None: s=y
        if not v and s is not None:
            cols=np.nonzero(img[s:y].max(0)>th)[0]; segs.append([s,y,cols[0],cols[-1]+1]); s=None
    return segs
def palette(d):
    p=np.frombuffer(d[:0x200],'>u2'); return np.stack([(p&31),((p>>5)&31),((p>>10)&31)],1).astype(float)
def ramp(d,tidx,levels=32):
    """alpha level -> palette index approximating alpha*color[tidx]"""
    P=palette(d); t=P[tidx]; out=[]
    for k in range(levels+1):
        tg=t*k/levels; out.append(int(np.argmin(((P-tg)**2).sum(1)+ (np.arange(256)==0)*0)))
    out[0]=0; return out
def tri(draw,x,y,w,h,dirn):
    if dirn=='r': pts=[(x,y),(x+w,y+h/2),(x,y+h)]
    elif dirn=='d': pts=[(x,y),(x+w,y),(x+w/2,y+h)]
    else: pts=[(x,y+h),(x+w,y+h),(x+w/2,y)]
    draw.polygon(pts,fill=255)
