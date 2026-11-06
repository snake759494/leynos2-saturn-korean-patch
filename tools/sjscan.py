import sys,os
def runs(d,minlen=4):
    i=0;n=len(d);res=[]
    while i<n-1:
        j=i;s=[]
        while j<n-1:
            a,b=d[j],d[j+1]
            if (0x81<=a<=0x9f or 0xe0<=a<=0xea) and (0x40<=b<=0xfc and b!=0x7f):
                try: s.append(bytes([a,b]).decode('cp932')); j+=2; continue
                except: pass
            break
        if len(s)>=minlen: res.append((i,''.join(s))); i=j
        else: i+=1
    return res
root=sys.argv[1]
for dp,_,fs in os.walk(root):
    for f in fs:
        p=os.path.join(dp,f)
        if os.path.getsize(p)>3_000_000: continue
        r=runs(open(p,'rb').read())
        if r: print(f'## {os.path.relpath(p,root)} {len(r)} runs, {sum(len(x[1]) for x in r)} chars'); [print(f'  {o:06x} {t[:60]}') for o,t in r[:4]]
