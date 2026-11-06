import sys,numpy as np
from PIL import Image
def bestw(b,ws=range(8,400,8)):
    r=[]
    for w in ws:
        n=len(b)//w
        if n<4: continue
        a=(b[:n*w].reshape(n,w)>0)
        r.append(((a[1:]==a[:-1]).mean(),w))
    return max(r)[1]
f,o0,o1=sys.argv[1],int(sys.argv[2],16),int(sys.argv[3],16)
d=np.frombuffer(open(f,'rb').read(),np.uint8)[o0:o1]
w=int(sys.argv[4]) if len(sys.argv)>4 and int(sys.argv[4]) else bestw(d)
n=len(d)//w; a=(d[:n*w].reshape(n,w)>0).astype(np.uint8)*255
print('w',w,n); Image.fromarray(a).save(sys.argv[5] if len(sys.argv)>5 else 'shots/sp.png')
