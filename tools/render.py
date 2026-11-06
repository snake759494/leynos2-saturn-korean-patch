import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from bdf import BDF
F=BDF('Galmuri11.bdf')
W=168
def render(text,font=F,base=13):
    img=np.zeros((16,W),np.uint8); x=0
    for ch in text:
        x+=font.draw(img,x,base,ch)
    return img,x
def to_bytes(img):
    out=bytearray()
    for c in range(W):
        v=0
        for y in range(16):
            if img[y,c]: v|=1<<y
        out+=v.to_bytes(2,'big')
    return bytes(out)
