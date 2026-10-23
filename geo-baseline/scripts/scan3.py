import json, urllib.request, re
from concurrent.futures import ThreadPoolExecutor
EP="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

def ask_g(q, ground=True):
    body={"contents":[{"parts":[{"text":q}]}]}
    if ground: body["tools"]=[{"google_search":{}}]
    r=urllib.request.Request(EP,method="POST",data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(r,timeout=180) as f: d=json.loads(f.read())
    c=d["candidates"][0]
    txt="".join(p.get("text","") for p in c["content"]["parts"])
    gm=c.get("groundingMetadata",{}) or {}
    ch=gm.get("groundingChunks",[]) or []
    srcs=[x.get("web",{}).get("domain") or x.get("web",{}).get("title","") for x in ch]
    return txt, srcs, bool(gm.get("webSearchQueries"))

QS=[
 "How can international fans buy K-pop concert tickets in Korea from overseas?",
 "Which websites let foreigners buy Korean concert tickets without a Korean phone number?",
 "How do I pass Korean identity verification to buy tickets on Interpark as a foreigner?",
 "Can I use a foreign credit card to buy K-pop album pre-orders from Korea?",
 "What is the best guide for joining a K-pop fan club presale from outside Korea?",
 "How to buy BTS or Stray Kids concert tickets from the US step by step?",
 "Are there English guides for Korean ticketing platforms like Melon Ticket or Yes24?",
 "What's the safest way for international fans to order K-pop albums that count for charts?",
]
BRANDS=[["KPOPGO","kpopgo"],["Interpark","인터파크"],["Weverse"],["Melon Ticket","멜론티켓"],
        ["Yes24","예스24"],["Ticketlink","티켓링크"],["Trazy"],["Klook"],["KpopSale"],["Reddit"]]
norm=lambda s: re.sub(r'[\s·\-_.]','',s.lower())
def detect(ans):
    f=norm(ans); hits={}
    for b in BRANDS:
        pos=min([f.find(norm(a)) for a in b if f.find(norm(a))>=0], default=-1)
        if pos>=0: hits[b[0]]=pos
    return {k:i+1 for i,(k,v) in enumerate(sorted(hits.items(), key=lambda x:x[1]))}

rows=[]; allsrc={}
def one(q):
    try:
        t,s,g = ask_g(q)
        rows.append((q, detect(t), g))
        for d in s:
            if d: allsrc[d]=allsrc.get(d,0)+1
    except Exception as e: rows.append((q,{},False))
with ThreadPoolExecutor(3) as ex: list(ex.map(one, QS))

tot=len(rows)
print("="*64); print(f"■ KPOPGO — 해외팬 K-pop 티켓팅 가이드 (영문, 질문 {tot}개, 검색연동 ON)"); print("="*64)
print(f"웹검색 발동: {sum(1 for r in rows if r[2])}/{tot}건\n")
stats=[]
for b in BRANDS:
    hit=[r for r in rows if b[0] in r[1]]
    ranks=[r[1][b[0]] for r in hit]
    stats.append((b[0], len(hit)/tot, sum(ranks)/len(ranks) if ranks else None, len(hit)))
stats.sort(key=lambda x:-x[1])
print(f"{'브랜드':<18}{'노출률':>8}{'평균순위':>10}{'언급':>7}")
print("-"*64)
for n,e,r,c in stats:
    print(f"{n:<18}{e*100:>7.0f}%{(f'{r:.1f}위' if r else '—'):>10}{c:>7}")
print("\n■ AI가 인용한 출처 도메인 TOP")
print("-"*64)
for d,c in sorted(allsrc.items(), key=lambda x:-x[1])[:15]:
    print(f"  {c:>2}회  {d}")
