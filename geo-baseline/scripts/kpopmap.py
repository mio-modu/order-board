import json, urllib.request, re
from concurrent.futures import ThreadPoolExecutor
EP="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

def ask_g(q):
    body={"contents":[{"parts":[{"text":q}]}],"tools":[{"google_search":{}}]}
    r=urllib.request.Request(EP,method="POST",data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"})
    for a in range(3):
        try:
            with urllib.request.urlopen(r,timeout=200) as f: d=json.loads(f.read())
            c=d["candidates"][0]
            txt="".join(p.get("text","") for p in c["content"]["parts"])
            gm=c.get("groundingMetadata",{}) or {}
            ch=gm.get("groundingChunks",[]) or []
            doms=[]
            for x in ch:
                w=x.get("web",{}) or {}
                doms.append((w.get("domain") or w.get("title") or "").lower())
            return txt,[d for d in doms if d],bool(gm.get("webSearchQueries"))
        except Exception:
            if a==2: return "",[],False
    return "",[],False

# 퍼널 단계별 질문 — kpopgo.app의 실제 페이지 주제에 맞춤
Q = {
 "티켓팅 기초":[
  "How can international fans buy K-pop concert tickets in Korea from overseas?",
  "Step by step guide to buying tickets on Interpark Global as a foreigner",
  "How do I buy Korean concert tickets if I don't live in Korea?",
  "What time do K-pop concert tickets go on sale in Korea and what timezone?",
  "Why can't foreigners buy tickets on Melon Ticket and what are the alternatives?",
 ],
 "본인인증":[
  "How to pass Korean identity verification to buy concert tickets as a foreigner",
  "What is a foreigner registration number and do I need one to buy K-pop tickets?",
  "Can I verify my identity on Korean ticketing sites with a foreign phone number?",
  "How to get a Korean phone verification for ticketing without living in Korea",
  "PASS app alternative for foreigners buying Korean tickets",
 ],
 "결제":[
  "Can I use a foreign credit card to buy K-pop tickets from Korean sites?",
  "Which payment methods work for international fans on Weverse Shop?",
  "Why does my foreign card get declined on Korean ticketing websites?",
  "Best way to pay for Korean concert tickets from abroad in 2026",
 ],
 "팬클럽 선예매":[
  "How do international fans join a K-pop fan club presale from outside Korea?",
  "Is it worth buying a K-pop fan club membership for presale access as a foreigner?",
  "How does Weverse membership presale work for international fans?",
 ],
 "앨범 주문":[
  "How to order K-pop albums from Korea so they count for Hanteo and Circle charts",
  "Which K-pop album shops ship internationally and count for charts?",
  "Is Weverse Shop or Ktown4u better for international album orders?",
  "How to buy K-pop album pre-orders from overseas safely",
 ],
 "사이트 사용법":[
  "What do the Korean words on Interpark ticketing page mean in English?",
  "English translation guide for Korean ticket booking websites",
  "How to navigate Yes24 ticket site if you don't read Korean",
 ],
 "문제해결":[
  "I got an error buying Korean concert tickets from abroad, what do I do?",
  "Is it safe to use a ticket proxy service for K-pop concerts in Korea?",
  "How to avoid scams when buying K-pop tickets from overseas resellers",
  "What happens if my Korean ticket order is cancelled for being a foreigner?",
 ],
 "브랜드 인지":[
  "What is kpopgo.app?",
  "Best English guides for K-pop ticketing for international fans",
  "Where can international K-pop fans find reliable ticketing instructions?",
 ],
}

ALL=[(cat,q) for cat,qs in Q.items() for q in qs]
res={}
def one(item):
    cat,q=item
    t,doms,g=ask_g(q)
    res[q]=(cat,t,doms,g)
with ThreadPoolExecutor(4) as ex: list(ex.map(one, ALL))

norm=lambda s: re.sub(r'[\s·\-_.]','',s.lower())
def has_kpopgo(t,doms):
    f=norm(t)
    return ("kpopgo" in f) or any("kpopgo" in d for d in doms)

dom_count={}; dom_q={}
rows=[]
for cat,q in ALL:
    c,t,doms,g=res.get(q,(cat,"",[],False))
    uniq=sorted(set(doms))
    for d in uniq:
        dom_count[d]=dom_count.get(d,0)+1
        dom_q.setdefault(d,[]).append(q)
    rows.append((cat,q,has_kpopgo(t,doms),len(uniq),uniq,g))

print("="*78)
print(f"■ KPOPGO 공략 지도 — 질문 {len(ALL)}개 / 검색발동 {sum(1 for r in rows if r[5])}건 / KPOPGO 노출 {sum(1 for r in rows if r[2])}건")
print("="*78)

print("\n[1] 카테고리별 경쟁 밀도 (인용 출처 수가 적을수록 뚫기 쉬움)")
print("-"*78)
bycat={}
for cat,q,hit,n,uniq,g in rows: bycat.setdefault(cat,[]).append(n)
for cat,ns in sorted(bycat.items(), key=lambda x: sum(x[1])/len(x[1])):
    avg=sum(ns)/len(ns)
    bar="█"*int(avg)
    print(f"  {cat:<12} 평균 인용출처 {avg:4.1f}개  {bar}")

print("\n[2] 질문별 난이도 — 인용 출처가 적은 순 (공략 우선순위)")
print("-"*78)
for cat,q,hit,n,uniq,g in sorted(rows, key=lambda r:r[3])[:14]:
    mark="★" if hit else " "
    print(f" {mark}[{n:>2}개] ({cat}) {q[:62]}")
    if uniq: print(f"        └ {', '.join(uniq[:5])}")

print("\n[3] AI가 가장 많이 인용하는 도메인 (= 인용 확보 타깃)")
print("-"*78)
for d,c in sorted(dom_count.items(), key=lambda x:-x[1])[:18]:
    print(f"  {c:>2}회  {d}")

json.dump({"rows":[(c,q,h,n,u) for c,q,h,n,u,_ in rows],"dom":dom_count,"dom_q":dom_q},
          open("kpopmap.json","w"), ensure_ascii=False)
