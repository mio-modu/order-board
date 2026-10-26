import json, urllib.request, re, collections, os
from concurrent.futures import ThreadPoolExecutor
EP="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

def call(p, ground=False, jm=False):
    b={"contents":[{"parts":[{"text":p}]}]}
    if ground: b["tools"]=[{"google_search":{}}]
    if jm and not ground: b["generationConfig"]={"responseMimeType":"application/json"}
    r=urllib.request.Request(EP,method="POST",data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
    for a in range(3):
        try:
            with urllib.request.urlopen(r,timeout=220) as f: d=json.loads(f.read())
            c=d["candidates"][0]
            txt="".join(x.get("text","") for x in c["content"]["parts"])
            gm=c.get("groundingMetadata",{}) or {}
            ch=gm.get("groundingChunks",[]) or []
            doms=[((x.get("web",{}) or {}).get("domain") or (x.get("web",{}) or {}).get("title") or "").lower() for x in ch]
            return txt,[d for d in doms if d],bool(gm.get("webSearchQueries")) or bool(ch)
        except Exception:
            if a==2: return "",[],False
    return "",[],False

CATS = {
 "dental":   ("dental-implant-and-orthodontic-treatment-in-Korea-for-foreign-patients",
              "치과 의료관광 (임플란트·교정)"),
 "kbeauty":  ("buying-Korean-skincare-and-cosmetics-from-overseas",
              "K-뷰티 해외 판매"),
 "travel":   ("booking-tours-activities-and-travel-services-in-Korea-as-a-foreigner",
              "한국 여행·투어"),
 "language": ("studying-Korean-language-in-Korea-as-an-international-student",
              "한국어 어학연수·유학원"),
 "kfood":    ("buying-Korean-food-snacks-and-groceries-shipped-internationally",
              "K-푸드 해외 직구"),
}

def gen_q(topic, n=20):
    p=(f"Write {n} search queries in English that a real foreign customer would type into "
       f"ChatGPT or Google when they are close to choosing or buying, on this topic: "
       f"{topic.replace('-',' ')}. Mix recommendation, comparison, price, safety/trust, "
       f"and how-to-start queries. Do NOT include any brand name. "
       f"Return a JSON array of {n} strings only.")
    t,_,_=call(p, jm=True)
    try: a=json.loads(t)
    except: a=[s[1:-1] for s in re.findall(r'"([^"]{12,})"',t)]
    return [x for x in a if isinstance(x,str)][:n]

def discover(topic, n=12):
    p=(f"List the real companies, brands or websites that actually compete for customers on: "
       f"{topic.replace('-',' ')}. Prefer those based in Korea or serving this market directly. "
       f"Return a JSON array of {n} exact brand names only.")
    t,_,_=call(p, jm=True)
    try: a=json.loads(t)
    except: a=[s[1:-1] for s in re.findall(r'"([^"]{2,40})"',t)]
    return [x.strip() for x in a if isinstance(x,str)][:n]

norm=lambda s: re.sub(r'[\s·\-_.]','',s.lower())
REPEAT=2

def run_cat(key):
    topic, label = CATS[key]
    qs = gen_q(topic); brands = discover(topic)
    rows=[None]*len(qs)
    def one(i):
        freq={}; ranks=collections.defaultdict(list); srcs=set(); fired=0
        for _ in range(REPEAT):
            t,doms,g=call(qs[i], ground=True)
            f=norm(t); hits={}
            for b in brands:
                p=f.find(norm(b))
                if p>=0: hits[b]=p
            for r,(b,_) in enumerate(sorted(hits.items(), key=lambda x:x[1]),1):
                freq[b]=freq.get(b,0)+1; ranks[b].append(r)
            srcs|=set(doms); fired+=1 if g else 0
        rows[i]={"q":qs[i],
                 "hits":{b:{"freq":v/REPEAT,"rank":sum(ranks[b])/len(ranks[b])} for b,v in freq.items()},
                 "srcs":sorted(srcs),"search":fired/REPEAT}
    with ThreadPoolExecutor(5) as ex: list(ex.map(one, range(len(qs))))
    n=len(rows) or 1
    stats=[]
    for b in brands:
        hit=[r for r in rows if b in r["hits"]]
        rk=[r["hits"][b]["rank"] for r in hit]
        stats.append({"name":b,
                      "exposure":sum(r["hits"].get(b,{}).get("freq",0) for r in rows)/n,
                      "mentions":len(hit),
                      "avgRank":(sum(rk)/len(rk)) if rk else None,
                      "missing":[r["q"] for r in rows if b not in r["hits"]]})
    stats.sort(key=lambda x:-x["exposure"])
    dc=collections.Counter()
    for r in rows:
        for s in r["srcs"]: dc[s]+=1
    meta={"date":"2026-10-26","engine":"Gemini 3 Flash","lang":"English","repeat":REPEAT,
          "questions":n,"label":label,
          "search_rate":sum(r["search"] for r in rows)/n,
          "avg_src":sum(len(r["srcs"]) for r in rows)/n,
          "top_domains":dc.most_common(14)}
    return {"meta":meta,"rows":rows,"stats":stats}

out={}
with ThreadPoolExecutor(3) as ex:
    for k,v in zip(CATS, ex.map(run_cat, list(CATS))): out[k]=v
json.dump(out, open("massscan.json","w"), ensure_ascii=False)

for k,v in out.items():
    m=v["meta"]
    print(f"\n{'='*66}\n■ {m['label']}  (질문 {m['questions']}개 × {REPEAT}회)")
    print(f"  검색 발동 {m['search_rate']*100:.0f}%  ·  평균 인용출처 {m['avg_src']:.1f}")
    print('-'*66)
    for s in v["stats"]:
        tag = "🔥" if s["exposure"]<=0.10 else ("·" if s["exposure"]<0.30 else " ")
        print(f"  {tag} {s['name'][:32]:<32}{s['exposure']*100:>5.0f}%  미노출 {len(s['missing'])}/{m['questions']}")
