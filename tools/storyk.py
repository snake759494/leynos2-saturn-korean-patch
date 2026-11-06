import sys,os,numpy as np,struct
sys.path.insert(0,os.path.dirname(__file__))
from PIL import Image,ImageDraw,ImageFont
from story import parse
ROOT=os.environ.get('LEYNOS2_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT=ImageFont.truetype(os.path.join(ROOT,'NanumSquareNeo-bRg.ttf'),21)
XS=0.80
def line_img(t):
    if not t: return np.zeros((24,1))
    w=int(FONT.getlength(t))+4
    im=Image.new('L',(w,26),0); ImageDraw.Draw(im).text((0,1),t,font=FONT,fill=255)
    im=im.resize((max(1,int(w*XS)),26),Image.LANCZOS)
    return np.asarray(im,float)/255
def compose(lines,H,W=368):
    img=np.zeros((H,W)); y=1
    for t in lines:
        if not t: y+=16; continue
        a=line_img(t)
        if a.shape[1]>W: raise Exception(f'too wide {a.shape[1]}: {t}')
        if y+26>H: raise Exception(f'too tall: {t}')
        img[y:y+26,:a.shape[1]]=np.maximum(img[y:y+26,:a.shape[1]],a)
        y+=40
    return np.clip(np.round(img*16),0,16).astype(np.uint8)
def build(path,lines):
    d,m,mp=parse(path); R=mp.shape[0]
    img=compose(lines,R*16)
    blocks=[bytes(256)]; idx={bytes(256):0}; M=np.zeros((R,23),'>u2')
    for r in range(R):
        for c in range(23):
            b=img[r*16:r*16+16,c*16:c*16+16].reshape(2,8,2,8).transpose(0,2,1,3).tobytes()
            if b not in idx: idx[b]=len(blocks); blocks.append(b)
            M[r,c]=idx[b]*2
    cap=(m-0x800)//256
    if len(blocks)>cap: raise Exception(f'{path}: blocks {len(blocks)}>{cap}')
    out=bytearray(d)
    pal=b''.join(struct.pack('>H',(v*31//16)*0x421) for v in range(17))
    out[0:0x200]=pal+bytes(0x200-len(pal))
    out[0x800:m]=b''.join(blocks)+bytes(m-0x800-256*len(blocks))
    out[m:m+M.size*2]=M.tobytes()
    return bytes(out),img,len(blocks),cap
if __name__=='__main__':
    for k in range(1,8):
        L=open(f'tr/story/S{k}.txt',encoding='utf-8').read().rstrip('\n').split('\n')
        try:
            o,img,n,cap=build(f'disc/DIR04/BG/S{k}.TXT',L); print(k,n,cap)
            Image.fromarray((img.astype(int)*255//16).astype(np.uint8)).save(f'sheets/K{k}.png')
        except Exception as e: print(k,e)
