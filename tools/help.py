import sys,struct,os; sys.path.insert(0,os.path.dirname(__file__)); import lz
from PIL import Image
D='disc/BANK00.BIN'
def ops(d):
    L=[]
    for i in range(len(d)-9):
        if d[i]==0x0c and d[i+1:i+3]==b'\x06\x02' and d[i+5:i+9]==bytes.fromhex('25e3eb80'):
            L.append((i,int.from_bytes(d[i+1:i+5],'big')-0x06020000))
    return L
def tree(d): return d[0x5878:0x5878+4096]
if __name__=='__main__':
    d=open(D,'rb').read(); v=open('shots/p0.v2','rb').read(); L=ops(d)
    im=Image.new('L',(512,len(L)*20))
    for n,(op,s) in enumerate(L):
        o,e=lz.decode(d,s,tree(d),0x1000)
        print(n,hex(op),hex(s),hex(e-s),len(o),' '.join('%04x'%x for x in struct.unpack_from('>40H',o,0) if x!=0x1549))
        for r in range(2):
            for c in range(64):
                pn=struct.unpack_from('>H',o,(r*64+c)*2)[0]; ch=pn&0x7fff
                for y in range(8):
                    for x in range(8):
                        b=v[ch*32+y*4+x//2]; p=(b>>(4*(1-x%2)))&15
                        im.putpixel((c*8+x,n*20+r*8+y),p*17)
    im.crop((0,0,320,len(L)*20)).resize((960,len(L)*60)).save('shots/help.png')
