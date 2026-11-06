import sys,struct,os; sys.path.insert(0,os.path.dirname(__file__)); import lz, help as H
import numpy as np
from render import F
BLANK=0x1549; TB=0x1480  # DIR01_0 chunk dst 0x29000 = char 0x1480
DIR01_BASE=0x238000-4
def gen(lines,bank,dir01):
    """returns new bank, new dir01 bytes"""
    t2=H.tree(bank); ops=H.ops(bank)
    # chunk of tiles in DIR01_0
    op1=0x184; s1=int.from_bytes(dir01[op1+1:op1+5],'big')-DIR01_BASE
    tiles,e1=lz.decode(dir01,s1,t2); tiles=bytearray(tiles)
    U=set()
    for _,s in ops: U|=set(struct.unpack('>128H',lz.decode(bank,s,t2)[0]))
    U.discard(BLANK)
    def kind(ch): return {x for b in tiles[(ch-TB)*32:(ch-TB)*32+32] for x in (b>>4,b&15)}
    free=sorted(set(U)|{c for c in range(0x15f6,0x18d7) if kind(c)<= {1,2,11}}-{BLANK})
    blank=bytes(tiles[(BLANK-TB)*32:(BLANK-TB)*32+32]); assert blank==b'\x11'*32
    cache={blank:BLANK}; maps={}
    for n,t in enumerate(lines):
        img=np.zeros((16,320),np.uint8); x=0
        for i,ch in enumerate(t):
            a=np.zeros((16,320),np.uint8); dx=F.draw(a,x,13,ch); x+=dx
            col=11 if t.startswith('ERROR:') and i<6 else 2
            img[a>0]=col
        assert x<=36*8,(t,x)
        m=[BLANK]*128
        for r in range(2):
            for c in range((x+7)//8):
                blk=img[r*8:r*8+8,c*8:c*8+8]; blk=np.where(blk==0,1,blk)
                b=bytes((blk[y,2*k]<<4)|blk[y,2*k+1] for y in range(8) for k in range(4))
                if b not in cache:
                    ch=free.pop(0) if free else (_ for _ in ()).throw(Exception("need more "+str(n))); cache[b]=ch; tiles[(ch-TB)*32:(ch-TB)*32+32]=b
                m[r*64+4+c]=cache[b]
        maps[n]=struct.pack('>128H',*m)
    print('help tiles used',len(cache)-1,'of',len(U))
    # rebuild DIR01 chunk
    dir01=bytearray(dir01); enc=lz.encode(bytes(tiles),bytes(dir01[s1:s1+5]),t2)
    assert lz.decode(enc,0,t2)[0]==bytes(tiles)
    if len(enc)<=e1-s1: dir01[s1:s1+len(enc)]=enc; dir01[s1+len(enc):e1]=bytes(e1-s1-len(enc))
    else:
        ns=len(dir01); dir01+=enc; dir01[op1+1:op1+5]=(ns+DIR01_BASE).to_bytes(4,'big'); dir01[0:4]=(len(dir01)-4).to_bytes(4,'big')
        print('dir01 chunk appended')
    # rebuild maps in BANK00 region
    bank=bytearray(bank)
    ends=[lz.decode(bytes(bank),s,t2)[1] for _,s in ops]
    lo=min(s for _,s in ops); hi=max(ends)
    hdr=bytes(bank[ops[0][1]:ops[0][1]+5]); pos=lo; done={}
    for n,(op,s) in enumerate(ops):
        if s in done: a=done[s]
        else:
            enc=min((lz.encode(maps[n],bytes([1,h,0x49,0x22,0]),t2) for h in (0x15,0x16,0x17,0x18)),key=len); a=pos
            bank[pos:pos+len(enc)]=enc; pos+=len(enc); done[s]=a
        bank[op+1:op+5]=(a+0x06020000).to_bytes(4,'big')
    assert pos<=hi,(hex(pos),hex(hi))
    bank[pos:hi]=bytes(hi-pos)
    return bytes(bank),bytes(dir01)
