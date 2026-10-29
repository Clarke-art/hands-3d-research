import os,sys,json,collections
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","scripts"))
import s6br_common as F
ctx=F.B.build_context()
own=ctx["own_r1a"]; EDGES=ctx["edges"]; NV=ctx["NV"]
ADJ={}
for a,b in EDGES:
    ADJ.setdefault(a,set()).add(b); ADJ.setdefault(b,set()).add(a)
SEAM=[k for k,(a,b) in enumerate(EDGES) if {own[a],own[b]}=={"THUMB","INDEX"}]
rows=[]
iso=0
for k in SEAM:
    a,b=EDGES[k]
    if own[a]!="THUMB": a,b=b,a
    ra=collections.Counter(own[w] for w in ADJ[a])
    rb=collections.Counter(own[w] for w in ADJ[b])
    rows.append((k,a,b,dict(ra),dict(rb)))
    if all(own[w]=="INDEX" for w in ADJ[a]) and all(own[w]=="THUMB" for w in ADJ[b]): iso+=1
print("RESULT edges=%d ; both endpoints FULLY surrounded by the opposite label: %d"%(len(rows),iso))
agg=collections.Counter()
for k,a,b,ra,rb in rows:
    agg[(tuple(sorted(ra.items())),tuple(sorted(rb.items())))]+=1
print("distinct 1-ring label patterns:",len(agg))
for pat,n in sorted(agg.items(),key=lambda kv:-kv[1])[:6]:
    print("  n=%-3d v0ring=%s v1ring=%s"%(n,dict(pat[0]),dict(pat[1])))
# how many seam vertices are 'isolated label islands' -- every neighbour opposite
islandA=[a for k,a,b,ra,rb in rows if all(own[w]=="INDEX" for w in ADJ[a])]
print("v0 (THUMB-labelled) vertices whose ENTIRE 1-ring is INDEX-labelled: %d / %d"%(len(set(islandA)),len(rows)))
