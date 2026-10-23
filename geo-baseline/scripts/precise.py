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
            with urllib.request.urlopen(r,timeout=220) as f: d=json.loads(f.read())
            c=d["candidates"][0]
            txt="".join(x.get("text","") for x in c["content"]["parts"])
            gm=c.get("groundingMetadata",{}) or {}
            ch=gm.get("groundingChunks",[]) or []
            doms=[((x.get("web",{}) or {}).get("domain") or (x.get("web",{}) or {}).get("title") or "").lower() for x in ch]
            return txt,[d for d in doms if d],bool(gm.get("webSearchQueries"))
        except Exception:
            if a==2: return "",[],False
    return "",[],False

LANGS={"fil":"Filipino/Tagalog","pt-br":"Brazilian Portuguese","th":"Thai"}
TOPICS=[
 "how to buy Korean concert tickets from abroad",
 "which Korean ticketing site sells tickets for my favorite group",
 "passing Korean identity verification as a foreigner",
 "getting a Korean phone number or alternative for ticket verification",
 "NOL World (formerly Interpark Global) sign up as a foreigner",
 "foreign credit card declined on a Korean ticketing site",
 "which payment methods work for overseas fans",
 "ticketing day timezone and what time tickets open in Korea",
 "waiting room queue and seat selection on Korean ticket sites",
 "joining a fan club presale from overseas",
 "is a paid fan club membership worth it for presale access",
 "Weverse membership and how it works for international fans",
 "ordering from Weverse Shop outside Korea",
 "buying K-pop albums so they count for Korean charts",
 "customs duty and shipping when ordering K-pop albums",
 "what the Korean words on a ticketing screen mean",
 "my Korean ticket order was cancelled, what now",
 "is it safe to use a ticket proxy or reseller",
 "mobile ticket and entry on the concert day in Korea",
 "refund and cancellation rules for Korean concert tickets",
]
def mkq(code,name):
    p=(f"Write 20 search queries in {name}, exactly as a real K-pop fan from that country "
       f"would type them into ChatGPT or Google. One query per topic, in order:\n"
       + "\n".join(f"{i+1}. {t}" for i,t in enumerate(TOPICS))
       + f"\nUse natural native phrasing, not translationese. Do not include brand names of guide sites. "
         f"Return a JSON array of exactly 20 strings.")
    t,_,_=call(p,jm=True)
    try: a=json.loads(t)
    except: a=[s[1:-1] for s in re.findall(r'"([^"]{10,})"',t)]
    return a[:20]

QS={}
with ThreadPoolExecutor(3) as ex:
    for c,q in zip(LANGS, ex.map(lambda kv: mkq(*kv), LANGS.items())): QS[c]=q
for c in QS: print(c, len(QS[c]), "문항")

jobs=[(c,i,q) for c,qs in QS.items() for i,q in enumerate(qs)]
out={}
def run(j):
    c,i,q=j
    t,doms,g=call(q,ground=True)
    out[(c,i)]=(q,t,sorted(set(doms)),g)
with ThreadPoolExecutor(6) as ex: list(ex.map(run,jobs))
json.dump({f"{c}|{i}":[v[0],v[2],v[3],("kpopgo" in (v[1]+" "+" ".join(v[2])).lower())] for (c,i),v in out.items()},
          open("precise.json","w"), ensure_ascii=False)
print("DONE", len(out))
