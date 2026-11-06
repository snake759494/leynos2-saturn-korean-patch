import numpy as np,os
from PIL import Image
def parse(path):
    d=open(path,'rb').read()
    m=[o for o in range(0x800,len(d),0x800) if d[o:o+4]==b'\x00\x02\x00\x04'][-1]
    mp=np.frombuffer(d[m:],'>u2').reshape(-1,23)
    return d,m,mp
def blk(d,n):
    n=int(n)
    return np.frombuffer(d[0x800+n*0x80:0x800+n*0x80+256],np.uint8).reshape(2,2,8,8).transpose(0,2,1,3).reshape(16,16)
def render(path):
    d,m,mp=parse(path); R=mp.shape[0]
    img=np.zeros((R*16,23*16),np.uint8)
    for r in range(R):
        for c in range(23): img[r*16:r*16+16,c*16:c*16+16]=blk(d,mp[r,c])
    return img
if __name__=='__main__':
    for k in range(1,8):
        img=render(f'disc/DIR04/BG/S{k}.TXT')
        Image.fromarray((img.astype(int)*255//max(1,img.max())).astype(np.uint8)).save(f'sheets/S{k}.png'); print(k,img.shape,img.max())
