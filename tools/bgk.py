import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from PIL import Image,ImageDraw,ImageFont
ROOT=os.environ.get('LEYNOS2_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def font(name,size): return ImageFont.truetype(os.path.join(ROOT,name),size)
def text_img(t,fnt,h,xs=1.0,dy=0):
    w=int(fnt.getlength(t))+4
    im=Image.new('L',(w,h),0); ImageDraw.Draw(im).text((1,dy),t,font=fnt,fill=255)
    if xs!=1.0: im=im.resize((max(1,int(w*xs)),h),Image.LANCZOS)
    a=np.asarray(im,float)/255
    nz=np.nonzero(a.max(0))[0]
    return a[:,:nz[-1]+1] if len(nz) else a
def pack(d,map_off,W,img,levels,cap_end=None):
    """img: HxW*16 float 0..1 -> rebuild char blocks from 0x800 and map at map_off"""
    R=img.shape[0]//16; q=np.clip(np.round(img*levels),0,levels).astype(np.uint8)
    blocks=[bytes(256)]; idx={bytes(256):0}; M=np.zeros((R,W),'>u2')
    for r in range(R):
        for c in range(W):
            b=q[r*16:r*16+16,c*16:c*16+16].reshape(2,8,2,8).transpose(0,2,1,3).tobytes()
            if b not in idx: idx[b]=len(blocks); blocks.append(b)
            M[r,c]=idx[b]*2
    cap=((cap_end or map_off)-0x800)//256
    if len(blocks)>cap: raise Exception(f'blocks {len(blocks)}>{cap}')
    out=bytearray(d)
    out[0x800:0x800+cap*256]=b''.join(blocks)+bytes(256*(cap-len(blocks)))
    out[map_off:map_off+M.size*2]=M.tobytes()
    return bytes(out),len(blocks),cap
