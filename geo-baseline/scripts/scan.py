import json, urllib.request, re, sys
from concurrent.futures import ThreadPoolExecutor
EP="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

def ask(q, json_mode=False):
    body={"contents":[{"parts":[{"text":q}]}]}
    if json_mode: body["generationConfig"]={"responseMimeType":"application/json"}
    r=urllib.request.Request(EP,method="POST",data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"})
    for a in range(3):
        try:
            with urllib.request.urlopen(r,timeout=180) as f: d=json.loads(f.read())
            c=d["candidates"][0]
            return "".join(p.get("text","") for p in c["content"]["parts"])
        except Exception as e:
            if a==2: raise
    return ""

def gen_questions(industry, n=12):
    p=f'''당신은 한국 시장 조사 전문가입니다.
"{industry}" 업종에서 실제 한국 사람이 ChatGPT 같은 AI에게 물어볼 법한, 구매/선택 의도가 있는 질문 {n}개를 만드세요.
- 특정 브랜드명을 질문에 넣지 마세요.
- 추천형/비교형/문제해결형/상황형을 섞으세요.
JSON 배열로만 출력: ["질문1",...]'''
    t=ask(p, True)
    try: return json.loads(t)[:n]
    except: return [s[1:-1] for s in re.findall(r'"([^"]{8,})"', t)][:n]

norm=lambda s: re.sub(r'[\s·\-_.]','',s.lower())
def detect(ans, brands):
    f=norm(ans); hits={}
    for b in brands:
        pos=min([f.find(norm(a)) for a in b if f.find(norm(a))>=0], default=-1)
        if pos>=0: hits[b[0]]=pos
    return {k:i+1 for i,(k,v) in enumerate(sorted(hits.items(), key=lambda x:x[1]))}

def scan(label, industry, brands, n=12):
    qs=gen_questions(industry, n)
    rows=[]
    def one(q):
        try: rows.append((q, detect(ask(q), brands)))
        except Exception as e: rows.append((q, {}))
    with ThreadPoolExecutor(3) as ex: list(ex.map(one, qs))
    tot=len(rows)
    stats=[]
    for b in brands:
        hit=[r for r in rows if b[0] in r[1]]
        ranks=[r[1][b[0]] for r in hit]
        stats.append((b[0], len(hit)/tot, sum(ranks)/len(ranks) if ranks else None, len(hit)))
    stats.sort(key=lambda x:-x[1])
    print(f"\n{'='*64}\n■ {label}  (질문 {tot}개)\n{'='*64}")
    print("질문 예시:")
    for q in qs[:4]: print("   ·", q)
    print(f"\n{'기업':<22}{'노출률':>8}{'평균순위':>10}{'언급':>7}")
    print("-"*64)
    for n_,e,r,c in stats:
        print(f"{n_:<22}{e*100:>7.0f}%{(f'{r:.1f}위' if r else '—'):>10}{c:>7}")
    return rows, stats

A=scan("오더투게더 / 단체주문·주문취합 카테고리",
  "회사나 모임에서 여러 명 점심·단체 주문을 취합하는 방법/앱",
  [["오더투게더","Order Together","오더 투게더"],["배달의민족","배민"],["쿠팡이츠"],["요기요"],
   ["식권대장"],["구글폼","Google Forms","구글 폼"],["네이버폼","네이버 폼"],["카카오톡 투표","카톡 투표"]])

B=scan("GEO 업체 카테고리 (본인이 진입할 시장)",
  "한국에서 AI 검색 노출 최적화(GEO) 대행사·업체 선택",
  [["제스트컴퍼니"],["서치폴라리스","Search Polaris"],["지오랭크","GeoRank"],["넥스트티","Next-T","OPTIGEO"],
   ["셀라벤토"],["디아이컴퍼니"],["스톤파티앤코프"],["딜라이트커뮤니케이션"],["써밋피드"],["오픈타임"]])

json.dump({"A":A[1],"B":B[1]}, open("scan_result.json","w"), ensure_ascii=False)
