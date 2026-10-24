import json, urllib.request, re, collections
from concurrent.futures import ThreadPoolExecutor
EP="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

def call(p, ground=True):
    b={"contents":[{"parts":[{"text":p}]}]}
    if ground: b["tools"]=[{"google_search":{}}]
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

QS=[
 "Best plastic surgery clinics in Seoul for foreigners with English-speaking staff",
 "Which Seoul clinics are safest for foreigners getting cosmetic procedures?",
 "How do international patients book a consultation at a Korean plastic surgery clinic?",
 "Medical tourism agency in Korea for plastic surgery — which one is reliable?",
 "How much does double eyelid surgery cost in Seoul for a foreigner?",
 "Is it safe to get cosmetic surgery in Korea as a foreigner, and how do I choose a clinic?",
 "Korean skin clinic recommendations for tourists visiting Seoul",
 "What should I check before choosing a plastic surgery hospital in Gangnam?",
 "Which Korean clinics offer aftercare for patients who fly home soon after surgery?",
 "How do I avoid broker scams when arranging plastic surgery in Korea?",
 "Rhinoplasty in Korea for foreigners — which hospitals are recommended?",
 "Do Korean plastic surgery clinics provide interpreters for English speakers?",
 "What is the typical recovery timeline if I get surgery in Seoul as a tourist?",
 "Korean dermatology clinic for laser treatment — recommendations for visitors",
 "Which Seoul hospitals handle revision surgery for international patients?",
 "How far in advance should a foreigner book plastic surgery in Korea?",
 "Are there all-inclusive medical tourism packages in Korea including hotel?",
 "What documents does a foreigner need for cosmetic surgery in Korea?",
 "Best clinics in Korea for jawline or facial contouring for overseas patients",
 "How do I verify a Korean clinic is legitimate before paying a deposit?",
]

BRANDS=[
 ["Wonjin Plastic Surgery","Wonjin"],
 ["Dream Plastic Surgery","Dream Medical Group","DreamPS"],
 ["Eunogo"],
 ["Docfinderkorea","Doc Finder Korea"],
 ["Seoul Guide Medical"],
 ["ID Hospital","IDHospital"],
 ["Banobagi"],
 ["View Plastic Surgery"],
 ["JK Plastic Surgery","JK Plastic"],
 ["Gangnam Unni","GangnamUnni"],
]
REPEAT=2
norm=lambda s: re.sub(r'[\s·\-_.]','',s.lower())
def detect(ans):
    f=norm(ans); hits={}
    for al in BRANDS:
        pos=min([f.find(norm(a)) for a in al if f.find(norm(a))>=0], default=-1)
        if pos>=0: hits[al[0]]=pos
    return {k:i+1 for i,(k,v) in enumerate(sorted(hits.items(), key=lambda x:x[1]))}

rows=[None]*len(QS)
def one(i):
    freq={}; ranks=collections.defaultdict(list); srcs=set(); fired=0
    for _ in range(REPEAT):
        t,doms,g=call(QS[i])
        for k,r in detect(t).items():
            freq[k]=freq.get(k,0)+1; ranks[k].append(r)
        srcs|=set(doms); fired+=1 if g else 0
    rows[i]={"q":QS[i],
             "hits":{k:{"freq":v/REPEAT,"rank":sum(ranks[k])/len(ranks[k])} for k,v in freq.items()},
             "srcs":sorted(srcs),"search":fired/REPEAT}
with ThreadPoolExecutor(4) as ex: list(ex.map(one, range(len(QS))))

n=len(rows)
stats=[]
for al in BRANDS:
    b=al[0]
    hit=[r for r in rows if b in r["hits"]]
    exp=sum(r["hits"].get(b,{}).get("freq",0) for r in rows)/n
    rk=[r["hits"][b]["rank"] for r in hit]
    stats.append({"name":b,"exposure":exp,"mentions":len(hit),
                  "avgRank":(sum(rk)/len(rk)) if rk else None,
                  "missing":[r["q"] for r in rows if b not in r["hits"]]})
stats.sort(key=lambda x:-x["exposure"])
dc=collections.Counter()
for r in rows:
    for s in r["srcs"]: dc[s]+=1
meta={"date":"2026-10-24","engine":"Gemini 3 Flash","lang":"English","repeat":REPEAT,
      "questions":n,"search_rate":sum(r["search"] for r in rows)/n,
      "avg_src":sum(len(r["srcs"]) for r in rows)/n,
      "top_domains":dc.most_common(14)}
json.dump({"meta":meta,"rows":rows,"stats":stats}, open("medscan.json","w"), ensure_ascii=False)

print(f"질문 {n}개 × {REPEAT}회 · 검색발동 {meta['search_rate']*100:.0f}% · 평균출처 {meta['avg_src']:.1f}")
print("-"*58)
for s in stats:
    print(f"  {s['name'][:30]:<30}{s['exposure']*100:>5.0f}%  "
          f"{(f'{s[chr(34)+chr(34)]}' if False else (f'{s['avgRank']:.1f}위' if s['avgRank'] else '—')):>7}  미노출 {len(s['missing'])}")
