import sys,numpy as np,struct
from PIL import Image
def find_map(d):
    res=[]
    for off in range(0x800,len(d),0x800):
        w=np.frombuffer(d[off:off+64],'>u2')
        if len(w)==32 and all(x%2==0 for x in w) and max(w)< (off-0x800)//128 and w.max()>0: res.append(off)
    return res
def render(d,off,W,end=None):
    end=end or len(d); m=np.frombuffer(d[off:end-(end-off)%(2*W)],'>u2').reshape(-1,W)
    pal=np.frombuffer(d[0:0x200],'>u2'); rgb=np.stack([(pal&31)<<3,((pal>>5)&31)<<3,((pal>>10)&31)<<3],1).astype(np.uint8)
    H=m.shape[0]; img=np.zeros((H*16,W*16),np.uint8)
    for r in range(H):
        for c in range(W):
            a=0x800+int(m[r,c])*0x80
            b=np.frombuffer(d[a:a+256],np.uint8)
            if len(b)<256: continue
            img[r*16:r*16+16,c*16:c*16+16]=b.reshape(2,2,8,8).transpose(0,2,1,3).reshape(16,16)
    return Image.fromarray(rgb[img])
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read(); print([hex(x) for x in find_map(d)][:10])
    if len(sys.argv)>3: render(d,int(sys.argv[2],16),int(sys.argv[3])).save(sys.argv[4])
