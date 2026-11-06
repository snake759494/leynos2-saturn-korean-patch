import os
TREE=open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'tree.bin'),'rb').read()
def decode(src,pos=0,tree=TREE,maxout=1<<22):
    p92,p93,p94,s86,s87=src[pos:pos+5]; pos+=5
    ops={0xfd:(s87>>4,p94),0xfc:(s87&15,p93),0xfb:(s86>>4,p92),0xfa:(s86&15,0)}
    out=bytearray(); cnt=0; buf=0
    def hist(d): return out[-d] if d and len(out)>=d else 0
    while True:
        node=0
        while True:
            if cnt>0: cnt-=1
            else: cnt=7; buf=src[pos]; pos+=1
            bit=buf&1; buf>>=1
            off=tree[node+bit]; node=node+2+2*off
            m=tree[node+1]
            if m>=0xfa: break
        v=tree[node]
        if m==0xfe: return bytes(out),pos
        if m==0xff: out.append(v)
        else:
            sel,par=ops[m]
            for _ in range(v+1): out.append((par+hist(sel))&0xff)
        if len(out)>maxout: raise Exception('overflow')
def leaves(tree=TREE):
    res={}
    def walk(node,code,depth):
        for bit in (0,1):
            off=tree[node+bit]; n=node+2+2*off; m=tree[n+1]
            c=code+[bit]
            if m>=0xfa: res[(m,tree[n])]=c
            else:
                if depth<40: walk(n,c,depth+1)
    walk(0,[],0); return res
_codes={}
def encode(data,header,tree=TREE):
    tree=bytes(tree)
    if tree not in _codes: _codes[tree]=leaves(tree)
    C=_codes[tree]
    p92,p93,p94,s86,s87=header
    ops={0xfd:(s87>>4,p94),0xfc:(s87&15,p93),0xfb:(s86>>4,p92),0xfa:(s86&15,0)}
    runlens={m:sorted(v for (mm,v) in C if mm==m) for m in ops}
    n=len(data); INF=1<<60
    cost=[INF]*(n+1); back=[None]*(n+1); cost[n]=len(C[(0xfe,0)])
    # backward DP: cost[i] = min bits to encode data[i:]
    def h(j): return data[j] if j>=0 else 0
    for i in range(n-1,-1,-1):
        best=len(C[(0xff,data[i])])+cost[i+1]; bk=(0xff,data[i])
        for m,(sel,par) in ops.items():
            # max run length L such that matches
            L=0
            while i+L<n and L<256:
                j=i+L
                src=(h(j-sel) if sel else 0)
                if data[j]!=(par+src)&0xff: break
                L+=1
            if L==0: continue
            for v in runlens[m]:
                if v+1>L: break
                c=len(C[(m,v)])+cost[i+v+1]
                if c<best: best=c; bk=(m,v)
        cost[i]=best; back[i]=bk
    bits=[]; i=0
    while i<n:
        m,v=back[i]; bits+=C[(m,v)]
        i+= 1 if m==0xff else v+1
    bits+=C[(0xfe,0)]
    out=bytearray(header)
    for k in range(0,len(bits),8):
        byte=0
        for t,b in enumerate(bits[k:k+8]): byte|=b<<t
        out.append(byte)
    return bytes(out)
