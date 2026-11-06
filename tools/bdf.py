import os
FD=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'fonts')
class BDF:
    def __init__(s,name):
        s.g={}; s.asc=0
        cur=None
        for l in open(os.path.join(FD,name),encoding='latin1'):
            t=l.split()
            if not t: continue
            if t[0]=='FONT_ASCENT': s.asc=int(t[1])
            elif t[0]=='ENCODING': cur={'enc':int(t[1])}
            elif t[0]=='DWIDTH': cur['dw']=int(t[1])
            elif t[0]=='BBX': cur['bbx']=list(map(int,t[1:5]))
            elif t[0]=='BITMAP': cur['rows']=[]; cur['inb']=True
            elif t[0]=='ENDCHAR':
                cur['inb']=False; s.g[cur['enc']]=cur
            elif cur and cur.get('inb'): cur['rows'].append(int(t[0],16)); cur['bits']=len(t[0])*4
    def draw(s,img,x,base,ch):
        """draw char at pen x, baseline y=base into 2D numpy array; return advance"""
        g=s.g.get(ord(ch))
        if g is None: raise KeyError(ch)
        w,h,ox,oy=g['bbx']
        top=base-oy-h
        for r,row in enumerate(g['rows']):
            for c in range(w):
                if row>>(g['bits']-1-c)&1:
                    yy=top+r; xx=x+ox+c
                    if 0<=yy<img.shape[0] and 0<=xx<img.shape[1]: img[yy,xx]=1
        return g['dw']
    def width(s,text): return sum(s.g[ord(c)]['dw'] for c in text)
