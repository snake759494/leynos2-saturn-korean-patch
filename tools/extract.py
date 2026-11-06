import sys,os,json
sys.path.insert(0,os.path.dirname(__file__))
from cdimg import Image
im=Image(sys.argv[1]); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
ents=im.dir_entries(); json.dump(ents,open(os.path.join(out,'..','files.json'),'w'),indent=0)
for e in ents:
    p=os.path.join(out,e['name']); os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,'wb').write(im.read(e['lba'],(e['size']+2047)//2048)[:e['size']])
    print(e['lba'],e['size'],e['name'])
open(os.path.join(out,'..','ip.bin'),'wb').write(im.read(0,16))
# 미션 팩 압축 해제용 허프만 트리 (BANK00.BIN 0x1122C, 4096바이트)
b=open(os.path.join(out,'BANK00.BIN'),'rb').read()
open(os.path.join(out,'..','tree.bin'),'wb').write(b[0x1122C:0x1122C+4096])
