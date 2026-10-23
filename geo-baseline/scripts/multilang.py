import json, urllib.request, re
from concurrent.futures import ThreadPoolExecutor
EP="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

def call(prompt, ground=False, jsonmode=False):
    b={"contents":[{"parts":[{"text":prompt}]}]}
    if ground: b["tools"]=[{"google_search":{}}]
    if jsonmode and not ground: b["generationConfig"]={"responseMimeType":"application/json"}
    r=urllib.request.Request(EP,method="POST",data=json.dumps(b).encode(),
        headers={"Content-Type":"application/json"})
    for a in range(3):
        try:
            with urllib.request.urlopen(r,timeout=200) as f: d=json.loads(f.read())
            c=d["candidates"][0]
            txt="".join(p.get("text","") for p in c["content"]["parts"])
            gm=c.get("groundingMetadata",{}) or {}
            ch=gm.get("groundingChunks",[]) or []
            doms=[( (x.get("web",{}) or {}).get("domain") or (x.get("web",{}) or {}).get("title") or "").lower() for x in ch]
            return txt,[d for d in doms if d],bool(gm.get("webSearchQueries"))
        except Exception:
            if a==2: return "",[],False
    return "",[],False

LANGS={"en":"English","id":"Bahasa Indonesia","th":"Thai","vi":"Vietnamese",
       "fil":"Filipino/Tagalog","pt-br":"Brazilian Portuguese","es":"Spanish","ja":"Japanese"}
TOPICS=["buying Korean concert tickets from abroad",
        "passing Korean identity verification as a foreigner for ticketing",
        "foreign credit card declined on Korean ticketing site",
        "joining a K-pop fan club presale from overseas",
        "ordering K-pop albums from Korea so they count for charts"]

def make_q(code,name):
    if code=="en": 
        return ["How can international fans buy Korean concert tickets from overseas?",
                "How do foreigners pass Korean identity verification for ticketing?",
                "Why was my foreign credit card declined on a Korean ticketing site?",
                "How do international fans join a K-pop fan club presale?",
                "How to order K-pop albums from Korea so they count for charts?"]
    p=(f"Write 5 search queries in {name} exactly as a real K-pop fan from that country "
       f"would type them into ChatGPT. Topics, one query each: {'; '.join(TOPICS)}. "
       f"Natural native phrasing, not translationese. No brand names. "
       f'JSON array of 5 strings only.')
    t,_,_=call(p,jsonmode=True)
    try: a=json.loads(t)
    except: a=[s[1:-1] for s in re.findall(r'"([^"]{10,})"',t)]
    return a[:5]

QS={}
with ThreadPoolExecutor(4) as ex:
    for code,qs in zip(LANGS, ex.map(lambda kv: make_q(*kv), LANGS.items())): QS[code]=qs

jobs=[(c,q) for c,qs in QS.items() for q in qs]
out={}
def run(j):
    c,q=j
    t,doms,g=call(q,ground=True)
    out[(c,q)]=(t,sorted(set(doms)),g)
with ThreadPoolExecutor(5) as ex: list(ex.map(run,jobs))

print("="*74)
print("■ 언어별 AI 검색 경쟁 밀도 — kpopgo.app 보유 언어 기준")
print("="*74)
print(f"{'언어':<22}{'검색발동':>9}{'평균 인용출처':>14}{'KPOPGO':>9}")
print("-"*74)
rank=[]
for c,name in LANGS.items():
    rs=[out[(c,q)] for q in QS[c] if (c,q) in out]
    if not rs: continue
    g=sum(1 for r in rs if r[2]); avg=sum(len(r[1]) for r in rs)/len(rs)
    kp=sum(1 for r in rs if "kpopgo" in (r[0]+" "+" ".join(r[1])).lower())
    rank.append((avg,c,name,g,len(rs),kp))
    print(f"{name:<22}{g}/{len(rs):<7}{avg:>13.1f}{kp:>8}")
print()
print("■ 비어 있는 순서 (인용 출처가 적을수록 뚫기 쉬움)")
print("-"*74)
for i,(avg,c,name,g,n,kp) in enumerate(sorted(rank),1):
    print(f"  {i}. {name:<22} 평균 {avg:.1f}개  {'█'*int(avg)}")
print()
print("■ 언어별 지배 도메인")
print("-"*74)
for c,name in LANGS.items():
    dc={}
    for q in QS.get(c,[]):
        if (c,q) in out:
            for d in out[(c,q)][1]: dc[d]=dc.get(d,0)+1
    top=sorted(dc.items(),key=lambda x:-x[1])[:5]
    print(f"  {name:<22}{', '.join(f'{d}({n})' for d,n in top) or '(없음)'}")
json.dump({f"{c}|{q}":[out[(c,q)][1],out[(c,q)][2]] for c,q in out}, open("multilang.json","w"), ensure_ascii=False)
