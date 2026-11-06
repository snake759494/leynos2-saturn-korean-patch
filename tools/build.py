import sys,os,json,shutil
sys.path.insert(0,os.path.dirname(__file__))

import lz
from dlg import *
import cdimg
from render import render,to_bytes
REPO=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT=os.environ.get('LEYNOS2_ROOT') or os.path.dirname(REPO)
ORIG=os.path.join(ROOT,'Assault Suit Leynos 2 (Japan) (Track 01).bin')
OUT=os.environ.get('LEYNOS2_OUT') or os.path.join(ROOT,'Assault Suit Leynos 2 (Korean) (Track 01).bin')
def patch_chunk(d,op,newdata):
    """replace compressed chunk referenced by op 0C at offset op; returns new file bytes"""
    d=bytearray(d); s=src_of(d,op)
    _,end=lz.decode(bytes(d),s)
    enc=lz.encode(newdata,bytes(d[s:s+5]))
    if len(enc)<=end-s:
        d[s:s+len(enc)]=enc
        for k in range(s+len(enc),end): d[k]=0
    else:
        ns=len(d); d+=enc
        a=ns-4+0x200000; d[op+1:op+5]=a.to_bytes(4,'big')
        d[0:4]=(len(d)-4).to_bytes(4,'big')
    return bytes(d)
def write_file(im,ents,name,data):
    e=next(x for x in ents if x['name']==name)
    cap=((e['size']+2047)//2048)*2048
    if len(data)>cap: raise Exception(f'{name} too big {len(data)}>{cap}')
    im.write_data(e['lba'],data+bytes(cap-len(data)) if len(data)%2048 else data)
    if len(data)!=e['size']: im.set_entry(e,e['lba'],len(data))
def dialog_map():
    order=json.load(open(os.path.join(REPO,'sheets','order.json')))
    per={}
    for n,h in order: per.setdefault(n,[]).append(h)
    M={}
    for n,hs in per.items():
        L=open(os.path.join(REPO,'tr',n+'.txt'),encoding='utf-8').read().rstrip('\n').split('\n')
        assert len(L)==len(hs),n
        for h,t in zip(hs,L): M[h]=t
    return M
def build_dialog(im,ents):
    M=dialog_map(); miss=0
    for n,f,dl,ev in blocks():
        d,dlg,_=load(n); new=bytearray(dlg)
        for i in range(0x3180,len(dlg),0x150):
            b=dlg[i:i+0x150]
            if not any(b): continue
            t=M.get(lid(b))
            if t is None: miss+=1; continue
            img,w=render(t); assert w<=168,(t,w)
            new[i:i+0x150]=to_bytes(img)
        nd=patch_chunk(d,dl,bytes(new))
        name=os.path.relpath(f,'disc').replace(os.sep,'/')
        write_file(im,ents,name,nd)
    print('dialog done, missing',miss)
import storyk
def build_story(im,ents):
    for k in range(1,8):
        L=open(os.path.join(REPO,'tr','story',f'S{k}.txt'),encoding='utf-8').read().rstrip('\n').split('\n')
        o,img,n,cap=storyk.build(f'disc/DIR04/BG/S{k}.TXT',L)
        write_file(im,ents,f'DIR04/BG/S{k}.TXT',o)
    print('story done')
import bgk
def build_mission(im,ents):
    d=open('disc/DIR04/BG/MISSION.BG','rb').read()
    L=open(os.path.join(REPO,'tr','mission.txt'),encoding='utf-8').read().rstrip('\n').split('\n')
    W=34; H=len(L)*32; img=np.zeros((H,W*16))
    f=bgk.font('NanumSquareNeo-cBd.ttf',22)
    for i,t in enumerate(L):
        a=bgk.text_img(t,f,26,0.92)
        if a.shape[1]>W*16-8: raise Exception('wide '+t)
        x=(W*16-a.shape[1])//2; y=i*32
        img[y:y+26,x:x+a.shape[1]]=np.maximum(img[y:y+26,x:x+a.shape[1]],a[:26])
    o,n,cap=bgk.pack(d,0x16800,W,img,31)
    write_file(im,ents,'DIR04/BG/MISSION.BG',o); print('mission',n,cap)
import helpk
def build_help(im,ents):
    L=open(os.path.join(REPO,'tr','help.txt'),encoding='utf-8').read().rstrip('\n').split('\n')
    b,d=helpk.gen(L,open('disc/BANK00.BIN','rb').read(),open('disc/DIR01/DIR01_0.BIN','rb').read())
    write_file(im,ents,'BANK00.BIN',b); write_file(im,ents,'DIR01/DIR01_0.BIN',d)
import bgtext
def build_backup(im,ents,save=None):
    from PIL import ImageDraw
    d=open('disc/DIR04/BG/BACKUP.BG','rb').read(); MO=0x3c800; W=40
    idx=bgtext.index_img(d,MO,W); segs=[s for s in bgtext.segments(idx) if s[1]-s[0]>4]
    L=open(os.path.join(REPO,'tr','backup.txt'),encoding='utf-8').read().rstrip('\n').split('\n')
    assert len(segs)==len(L),(len(segs),len(L))
    vals,cnt=np.unique(idx[idx>0],return_counts=True); tidx=int(vals[np.argmax(cnt)])
    f=bgk.font('NanumSquareNeo-bRg.ttf',22); fb=bgk.font('NanumSquareNeo-bRg.ttf',27)
    canvas=Image.new('L',(W*16,idx.shape[0]),0); dr=ImageDraw.Draw(canvas)
    def put(t,fnt,x,cy,xs=1.0):
        a=bgk.text_img(t,fnt,40,xs,dy=4); r=np.nonzero(a.max(1))[0]; a=a[r[0]:r[-1]+1]
        y=int(round(cy-a.shape[0]/2)); canvas.paste(Image.fromarray((a*255).astype(np.uint8)),(int(x),y),Image.fromarray((a*255).astype(np.uint8)))
        return a.shape[1]
    for i,((s,e,c0,c1),t) in enumerate(zip(segs,L)):
        cy=(s+e)/2
        if '|' in t:
            a,b=t.split('|'); put(a,f,c0,cy); bgtext.tri(dr,332,cy-7,13,14,'r'); put(b,f,358,cy)
        elif i==len(L)-3:
            w=int(fb.getlength(t)); x=(W*16-w)//2; put(t,fb,x,cy)
            bgtext.tri(dr,x-46,cy-11,28,22,'d'); bgtext.tri(dr,x+w+18,cy-11,28,22,'u')
        elif i==len(L)-2:
            bgtext.tri(dr,c0,cy-7,13,14,'r'); put(t,f,166,cy)
        elif i==len(L)-1: put(t,f,c0,cy)
        else:
            w=int(f.getlength(t)); put(t,f,(c0+c1)/2-w/2,cy)
    A=np.asarray(canvas,float)/255; R=bgtext.ramp(d,tidx)
    out=np.array(R,np.uint8)[np.round(A*32).astype(int)]
    o,n,cap=bgk.pack(d,MO,W,out/255.0,255)
    if save: Image.fromarray(np.array(bgtext.bgr.render(o,MO,W))).save(save)
    if im: write_file(im,ents,'DIR04/BG/BACKUP.BG',o)
    print('backup',n,cap)
def build_bkspr(im,ents,save=None):
    from bdf import BDF
    f=BDF('Galmuri9.bdf'); d=bytearray(open('disc/DIR04/SPRITE/BACKUP.SPR','rb').read())
    for k,t in enumerate(['시작할 디스크를 선택하십시오','데이터를 삭제합니다']):
        a=np.zeros((11,184),np.uint8); x=0
        for ch in t: x+=f.draw(a,x,10,ch)
        assert x<=184,(t,x)
        off=0x6ba8+k*184*11; d[off:off+184*11]=(a*2).astype(np.uint8).tobytes()
        if save: Image.fromarray(a*255).resize((368,22),0).save(save%k)
    if im: write_file(im,ents,'DIR04/SPRITE/BACKUP.SPR',bytes(d))
def build_setting(im,ents,save=None):
    from render import F
    d=bytearray(open('disc/DIR04/BG/SETTING.BG','rb').read()); MO=0x39800; W=40
    m=np.frombuffer(bytes(d[MO:]),'>u2').copy(); M=m[:len(m)//W*W].reshape(-1,W)
    from collections import Counter
    C=Counter(m.tolist()); free=[k for k in range(1810,1824,2) if k not in C]
    def blk(k): return np.frombuffer(bytes(d[0x800+k*0x80:0x800+k*0x80+256]),np.uint8).reshape(2,2,8,8).transpose(0,2,1,3).reshape(16,16)
    R0,R1,C0,C1=22,24,9,31
    reg=np.zeros(((R1-R0)*16,(C1-C0)*16),np.uint8)
    for r in range(R0,R1):
        for c in range(C0,C1): reg[(r-R0)*16:(r-R0+1)*16,(c-C0)*16:(c-C0+1)*16]=blk(int(M[r,c]))
    reg[reg==1]=17
    t='사용할 기체를 선택해 주십시오'
    a=np.zeros((16,200),np.uint8); x=0
    for ch in t: x+=F.draw(a,x,13,ch)
    rows=np.nonzero(a.max(1))[0]; a=a[rows[0]:rows[-1]+1,:x]
    a=np.kron(a,np.ones((2,2),np.uint8))
    cx=(142+499)//2-C0*16; cy=(346+379)//2-R0*16
    y0=0; x0=cx-a.shape[1]//2
    sub=reg[y0:y0+a.shape[0],x0:x0+a.shape[1]]; sub[a>0]=1
    seen=set()
    for r in range(R0,R1):
        for c in range(C0,C1):
            k=int(M[r,c]); b=reg[(r-R0)*16:(r-R0+1)*16,(c-C0)*16:(c-C0+1)*16]
            if C[k]>1 or k in seen:
                if (b==blk(k)).all(): continue
                k=free.pop(0); M[r,c]=k
            seen.add(k)
            d[0x800+k*0x80:0x800+k*0x80+256]=b.reshape(2,8,2,8).transpose(0,2,1,3).tobytes()
    d[MO:MO+M.size*2]=M.astype('>u2').tobytes()
    if save:
        I=bgtext.index_img(bytes(d[:MO+W*30*2]),MO,W); Image.fromarray((I[330:400,120:520]*12).astype(np.uint8)).resize((800,140),0).save(save)
    if im: write_file(im,ents,'DIR04/BG/SETTING.BG',bytes(d))
    print('setting free left',len(free))
def build_ending(im,ents,save=None):
    d=open('disc/DIR04/BG/ENDSTORY.BG','rb').read(); MO=0x3f000-42; W=40
    idx=bgtext.index_img(d,MO,W); segs=[s for s in bgtext.segments(idx) if s[1]-s[0]>4]
    L=open(os.path.join(REPO,'tr','ending.txt'),encoding='utf-8').read().rstrip('\n').split('\n')
    assert len(segs)==len(L),(len(segs),len(L))
    vals,cnt=np.unique(idx[idx>0],return_counts=True); tidx=int(vals[np.argmax(cnt)])
    P=bgtext.palette(d); tidx=int(max(vals,key=lambda v:P[v].sum()))
    f=bgk.font('NanumSquareNeo-cBd.ttf',22)
    canvas=Image.new('L',(W*16,idx.shape[0]),0)
    for (s,e,c0,c1),t in zip(segs,L):
        a=bgk.text_img(t,f,40,0.97,dy=4); r=np.nonzero(a.max(1))[0]; a=a[r[0]:r[-1]+1]
        assert a.shape[1]<=W*16-24,(t,a.shape)
        g=Image.fromarray((a*255).astype(np.uint8)); canvas.paste(g,(12,int(round((s+e)/2-a.shape[0]/2))),g)
    A=np.asarray(canvas,float)/255; R=bgtext.ramp(d,tidx)
    out=np.array(R,np.uint8)[np.round(A*32).astype(int)]
    o,n,cap=bgk.pack(d,MO,W,out/255.0,255,cap_end=0x3e800)
    if save: bgtext.bgr.render(o,MO,W).crop((0,0,640,800)).save(save)
    if im: write_file(im,ents,'DIR04/BG/ENDSTORY.BG',o)
    print('ending',n,cap)
def _clear_paste(canvas,a,x,cy):
    g=Image.fromarray((a*255).astype(np.uint8)); canvas.paste(g,(int(x),int(round(cy-a.shape[0]/2))),g)
def _crop(a):
    r=np.nonzero(a.max(1))[0]; return a[r[0]:r[-1]+1]
def build_demo(im,ents,save=None):
    d=open('disc/DIR04/BG/DEMO.BG','rb').read(); MO=0x1790a; W=19
    idx=bgtext.index_img(d,MO,W)
    segs=[s for s in bgtext.segments(idx) if s[1]-s[0]>18]
    L=open(os.path.join(REPO,'tr','demo.txt'),encoding='utf-8').read().rstrip('\n').split('\n')
    assert len(segs)==len(L),(len(segs),len(L))
    keep=np.zeros_like(idx)
    for s in bgtext.segments(idx):
        if s[1]-s[0]<=18 and s[1]-s[0]>4: keep[s[0]:s[1]]=idx[s[0]:s[1]]   # A.D. lines
    f=bgk.font('NanumSquareNeo-bRg.ttf',20)
    canvas=Image.new('L',(W*16,idx.shape[0]),0)
    for (s,e,c0,c1),t in zip(segs,L):
        a=_crop(bgk.text_img(t,f,32,1.0,dy=4)); a=(a>0.45).astype(float)
        assert a.shape[1]<=W*16-2,(t,a.shape)
        _clear_paste(canvas,a,271-a.shape[1],(s+e)/2)
    out=np.maximum((np.asarray(canvas)>127).astype(np.uint8),keep)
    o,n,cap=bgk.pack(d,MO,W,out/1.0,1)
    if save: bgtext.bgr.render(o,MO,W).crop((0,700,304,1760)).save(save)
    if im: write_file(im,ents,'DIR04/BG/DEMO.BG',o)
    print('demo',n,cap)
def build_end1(im,ents,save=None):
    d=open('disc/DIR04/BG/END1.BG','rb').read(); MO=0xe4e6; W=40
    idx=bgtext.index_img(d,MO,W); segs=bgtext.segments(idx)
    P=bgtext.palette(d); vals=np.unique(idx[idx>0]); tidx=int(max(vals,key=lambda v:P[v].sum()))
    canvas=Image.new('L',(W*16,idx.shape[0]),0)
    ft=bgk.font('NanumSquareNeo-bRg.ttf',40); fc=bgk.font('NanumSquareNeo-bRg.ttf',27)
    # title (italic by shear)
    s,e,c0,c1=segs[0]
    a=bgk.text_img('아직 보지 못한 하늘을 향해',ft,64,0.95,dy=8)
    g=Image.fromarray((a*255).astype(np.uint8)); sh=0.2
    g=g.transform((g.size[0]+int(g.size[1]*sh),g.size[1]),Image.AFFINE,(1,sh,-g.size[1]*sh,0,1,0),Image.BICUBIC)
    a=_crop(np.asarray(g,float)/255); nz=np.nonzero(a.max(0))[0]; a=a[:,nz[0]:nz[-1]+1]
    assert a.shape[1]<=W*16-8,a.shape
    _clear_paste(canvas,a,(W*16-a.shape[1])//2 if a.shape[1]>c1-c0 else c0,(s+e)/2)
    for (s,e,c0,c1),(lab,name) in zip(segs[1:],[('작사','요시다 나호코'),('작곡',''),('편곡',''),('노래','호조 시즈카')]):
        a=_crop(bgk.text_img(lab+' :',fc,48,1.0,dy=6)); _clear_paste(canvas,a,240-a.shape[1],(s+e)/2)
        if name: a=_crop(bgk.text_img(name,fc,48,1.0,dy=6)); _clear_paste(canvas,a,252,(s+e)/2)
    A=np.asarray(canvas,float)/255; R=bgtext.ramp(d,tidx)
    out=np.array(R,np.uint8)[np.round(A*32).astype(int)]
    o,n,cap=bgk.pack(d,MO,W,out/255.0,255)
    if save: bgtext.bgr.render(o,MO,W).save(save)
    if im: write_file(im,ents,'DIR04/BG/END1.BG',o)
    print('end1',n,cap)
def build_setspr(im,ents,save=None):
    """SETTING.SPR: help messages stored as a ribbon of 64x11 8bpp strips (value 4)"""
    from bdf import BDF
    F11=BDF('Galmuri11.bdf'); FC=BDF('Galmuri11-Condensed.bdf')
    d=bytearray(open('disc/DIR04/SPRITE/SETTING.SPR','rb').read())
    B=0x59700; R0=14; NR=(len(d)-B)//64
    rows=np.frombuffer(bytes(d[B:B+NR*64]),np.uint8).reshape(NR,64).copy()
    rows=np.vstack([rows,np.zeros((11,64),np.uint8)])
    n=(NR+1-R0)//11
    rib=np.hstack([rows[R0+11*k:R0+11*k+11] for k in range(n)])
    for l in open(os.path.join(REPO,'tr','setspr.txt'),encoding='utf-8').read().rstrip('\n').split('\n'):
        a,b,t=l.split('\t'); a=int(a); b=int(b)
        f=F11 if F11.width(t)<=b-a+2 else FC
        assert f.width(t)<=b-a+2,(t,f.width(t),b-a)
        seg=rib[:,a:b]; seg[seg==4]=0
        g=np.zeros((11,f.width(t)+2),np.uint8); x=0
        for ch in t: x+=f.draw(g,x,11,ch)
        w=min(b-a,g.shape[1]); m=g[:,:w]>0; seg[:,:w][m]=4
    for k in range(n): rows[R0+11*k:R0+11*k+11]=rib[:,64*k:64*k+64]
    d[B:B+NR*64]=rows[:NR].tobytes()
    if save: Image.fromarray((rib==4).astype(np.uint8)*255).save(save)
    if im: write_file(im,ents,'DIR04/SPRITE/SETTING.SPR',bytes(d))
    print('setspr ok')
