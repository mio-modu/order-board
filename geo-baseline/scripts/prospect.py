import json, urllib.request, re
from concurrent.futures import ThreadPoolExecutor
EP="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

def call(p, ground=False, jm=False):
    b={"contents":[{"parts":[{"text":p}]}]}
    if ground: b["tools"]=[{"google_search":{}}]
    if jm and not ground: b["generationConfig"]={"responseMimeType":"application/json"}
    r=urllib.request.Request(EP,method="POST",data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
    for a in range(3):
        try:
            with urllib.request.urlopen(r,timeout=200) as f: d=json.loads(f.read())
            c=d["candidates"][0]
            txt="".join(x.get("text","") for x in c["content"]["parts"])
            gm=c.get("groundingMetadata",{}) or {}
            ch=gm.get("groundingChunks",[]) or []
            doms=[((x.get("web",{}) or {}).get("domain") or (x.get("web",{}) or {}).get("title") or "").lower() for x in ch]
            return txt,[d for d in doms if d],bool(gm.get("webSearchQueries")) or bool(ch)
        except Exception:
            if a==2: return "",[],False
    return "",[],False

# 영어권을 노리는 한국 기업 카테고리 — 예산이 있고 영문 검색 수요가 확실한 곳
CATS = {
 "의료관광 (성형·피부과)": {
   "desc":"foreign patients choosing a plastic surgery or dermatology clinic in Seoul",
   "qs":[
    "Best plastic surgery clinics in Seoul for foreigners with English-speaking staff",
    "How do international patients book a consultation at a Korean dermatology clinic?",
    "Which Seoul clinics are safest for foreigners getting cosmetic procedures?",
    "Korean skin clinic recommendations for tourists visiting Seoul",
    "Medical tourism agency in Korea for plastic surgery — which one is reliable?",
    "How much does double eyelid surgery cost in Seoul for a foreigner?",
    "Is it safe to get cosmetic surgery in Korea as a foreigner, and how do I choose a clinic?",
   ]},
 "K-뷰티 해외 판매": {
   "desc":"overseas shoppers buying Korean beauty products",
   "qs":[
    "Where can I buy authentic Korean skincare and have it shipped internationally?",
    "Best Korean beauty online stores that ship worldwide",
    "How to buy K-beauty products directly from Korea without a proxy service",
    "Which Korean cosmetics brands ship internationally with good customer service?",
    "Trusted K-beauty retailers for international customers 2026",
    "How do I know if Korean skincare bought online is authentic?",
    "Korean beauty subscription box that ships overseas",
   ]},
 "한국 여행·투어 상품": {
   "desc":"foreign travelers booking tours and activities in Korea",
   "qs":[
    "Best websites to book tours and activities in Korea as a foreigner",
    "How do international travelers buy Korea rail passes and transport cards online?",
    "Reliable DMZ tour booking site for foreign tourists in Seoul",
    "Where to book a Korean cooking class or hanbok experience in Seoul in English",
    "Best Korea travel booking platform for English speakers",
    "How to book a private guide in Seoul who speaks English",
    "Korea travel SIM or eSIM — where should foreigners buy it?",
   ]},
}

def discover(cat, desc):
    p=(f"List the real companies, brands or websites that actually compete for {desc}, "
       f"focused on those operating from Korea or serving this market. "
       f"Return a JSON array of 10 exact brand names only, no description.")
    t,_,_=call(p, jm=True)
    try: a=json.loads(t)
    except: a=[s[1:-1] for s in re.findall(r'"([^"]{2,40})"',t)]
    return [x.strip() for x in a if isinstance(x,str)][:10]

norm=lambda s: re.sub(r'[\s·\-_.]','',s.lower())
def detect(ans, brands):
    f=norm(ans); hits={}
    for b in brands:
        i=f.find(norm(b))
        if i>=0: hits[b]=i
    return {k:n+1 for n,(k,v) in enumerate(sorted(hits.items(), key=lambda x:x[1]))}

REPEAT=2
report={}
for cat,spec in CATS.items():
    brands=discover(cat, spec["desc"])
    rows=[]
    def one(q):
        freq={}; srcs=set(); fired=0
        for _ in range(REPEAT):
            t,doms,g=call(q, ground=True)
            for k in detect(t,brands): freq[k]=freq.get(k,0)+1
            srcs|=set(doms); fired+= 1 if g else 0
        rows.append({"q":q,"freq":{k:v/REPEAT for k,v in freq.items()},
                     "srcs":sorted(srcs),"search":fired/REPEAT})
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, spec["qs"]))
    n=len(rows)
    stats=[]
    for b in brands:
        e=sum(r["freq"].get(b,0) for r in rows)/n
        stats.append((b, e))
    stats.sort(key=lambda x:-x[1])
    sr=sum(r["search"] for r in rows)/n
    avg=sum(len(r["srcs"]) for r in rows)/n
    report[cat]={"brands":brands,"stats":stats,"rows":rows,"search_rate":sr,"avg_src":avg}
    print(f"\n{'='*70}\n■ {cat}  (질문 {n}개 × {REPEAT}회)")
    print(f"  검색 발동률 {sr*100:.0f}%   평균 인용출처 {avg:.1f}")
    print(f"{'-'*70}")
    for b,e in stats:
        bar='█'*int(e*20)
        print(f"  {b[:34]:<34}{e*100:>5.0f}%  {bar}")
json.dump(report, open("prospect.json","w"), ensure_ascii=False)
