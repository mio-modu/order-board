# massscan.json + medscan.json -> 카테고리별 기업 리포트 + 발송 명단
import json, html, os, re, sys, collections

OUT = sys.argv[1] if len(sys.argv)>1 else 'out'
os.makedirs(OUT, exist_ok=True)
e = lambda s: html.escape(str(s))
pct = lambda v: f"{v*100:.0f}%"
rankstr = lambda r: (f"{r:.1f}위" if r else "—")

def _jong(w):
    w=(w or "").strip()
    if not w: return False
    c=ord(w[-1])
    if 0xAC00 <= c <= 0xD7A3: return (c-0xAC00)%28 != 0
    return bool(re.search(r"[1368lmnr]$", w, re.I))
def J(w,k):
    p={"iga":("이","가"),"eun":("은","는")}[k]
    return w + (p[0] if _jong(w) else p[1])

def slug(s): return re.sub(r'[^A-Za-z0-9가-힣]+','_',s).strip('_')[:60]

CSS = """
:root{--bg:#FFFDF8;--ink:#17160F;--muted:#5E5A4E;--line:#E3DDCC;--soft:#F7F3E8;--acc:#8F3522}
*{box-sizing:border-box}
body{font-family:-apple-system,'Pretendard',Segoe UI,sans-serif;max-width:880px;margin:36px auto;
 padding:0 24px;background:var(--bg);color:var(--ink);line-height:1.65;font-size:14px}
h1{font-size:26px;margin:0 0 6px;letter-spacing:-.01em}
h2{font-size:15px;margin:30px 0 10px;border-bottom:2px solid var(--acc);padding-bottom:6px}
.sub{color:var(--muted);font-size:12.5px;margin-bottom:22px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0}
.grid>div{background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:14px}
.k{font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.v{font-size:24px;font-weight:700;margin-top:4px;color:var(--acc)}
.n{font-size:11.5px;color:var(--muted);margin-top:2px}
.box{background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:16px;margin:12px 0}
table{width:100%;border-collapse:collapse;font-size:12.5px;margin:8px 0}
th,td{padding:9px 10px;text-align:left;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-size:10.5px;text-transform:uppercase;letter-spacing:.04em}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tr.me td{background:#F2ECDC;font-weight:700}
.muted{color:var(--muted)}
.foot{margin-top:28px;font-size:11.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
@media print{body{margin:0;background:#fff}}
"""

def build(me, meta, rows, stats):
    st=next(s for s in stats if s['name']==me)
    leader=stats[0]
    avg=sum(s['exposure'] for s in stats)/len(stats)
    lost=[]
    for r in rows:
        if me in r['hits'] or not r['hits']: continue
        win=sorted(r['hits'].items(), key=lambda x:x[1]['rank'])[0][0]
        lost.append((r['q'],win,len(r['srcs'])))
    lost.sort(key=lambda x:x[2])
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(me)} — AI 검색 노출 진단</title><style>{CSS}</style></head><body>
<h1>{e(me)} — AI 검색 노출 진단</h1>
<div class="sub">{e(meta['label'])} · 측정일 {meta['date']} · 엔진 {e(meta['engine'])} ·
언어 {e(meta['lang'])} · 구매 의도 질문 {meta['questions']}개 × {meta['repeat']}회 반복 · 비교 {len(stats)}곳</div>
<div class="grid">
 <div><div class="k">노출률</div><div class="v">{pct(st['exposure'])}</div>
   <div class="n">{meta['questions']}개 중 {st['mentions']}개에서 언급</div></div>
 <div><div class="k">평균 순위</div><div class="v">{rankstr(st['avgRank'])}</div>
   <div class="n">언급될 때의 평균 위치</div></div>
 <div><div class="k">시장 평균</div><div class="v">{pct(avg)}</div>
   <div class="n">{'평균 이상' if st['exposure']>=avg else '평균 미달'}</div></div>
</div>
<div class="grid">
 <div><div class="k">AI 웹검색 발동률</div><div class="v">{pct(meta['search_rate'])}</div>
   <div class="n">개입 가능한 질문의 비율</div></div>
 <div><div class="k">평균 인용 출처</div><div class="v">{meta['avg_src']:.1f}</div>
   <div class="n">질문당 AI가 참고한 사이트 수</div></div>
 <div><div class="k">미노출 질문</div><div class="v">{len(st['missing'])}</div>
   <div class="n">한 번도 등장하지 않은 질문</div></div>
</div>
<div class="box"><b>요약.</b> 해외 고객이 실제로 물어볼 법한 구매 질문 {meta['questions']}개를 AI에 직접
질의한 결과 <b>{e(me)}</b> 노출률은 <b>{pct(st['exposure'])}</b>였습니다.
같은 조건에서 가장 많이 등장한 곳은 <b>{e(leader['name'])}</b>({pct(leader['exposure'])})입니다.
{len(st['missing'])}개 질문에서는 {e(J(me,'iga'))} 한 번도 등장하지 않았습니다.</div>
<h2>1. 경쟁 구도</h2>
<table><thead><tr><th>기업</th><th class="num">노출률</th><th class="num">평균 순위</th><th class="num">미노출</th></tr></thead><tbody>
{''.join(f'<tr class="{"me" if s["name"]==me else ""}"><td>{e(s["name"])}</td>'
 f'<td class="num">{pct(s["exposure"])}</td><td class="num">{rankstr(s["avgRank"])}</td>'
 f'<td class="num">{len(s["missing"])}</td></tr>' for s in stats)}
</tbody></table>
<h2>2. 놓치고 있는 질문</h2>
<div class="muted" style="font-size:12.5px;margin-bottom:8px">인용 출처가 적을수록 아직 아무도 답을 제대로 쓰지 않은 자리입니다.</div>
<table><thead><tr><th>질문</th><th>대신 1위로 나온 곳</th><th class="num">인용 출처</th></tr></thead><tbody>
{''.join(f'<tr><td>{e(q)}</td><td class="muted">{e(w)}</td><td class="num">{c}</td></tr>' for q,w,c in lost[:12]) or '<tr><td colspan="3">해당 없음</td></tr>'}
</tbody></table>
<h2>3. AI는 어디를 보고 답하는가</h2>
<div class="box">측정된 {meta['questions']}개 질의 중 <b>{pct(meta['search_rate'])}</b>에서 AI가 실제로 웹을 검색했습니다.
콘텐츠와 인용 확보로 <b>개입이 작동하는 영역</b>이라는 뜻입니다.<br><br>
다만 인용된 출처를 보면 <b>기업 자체 홈페이지는 소수</b>이고 제3자 사이트와 커뮤니티가 대부분입니다.
홈페이지 개선만으로는 AI 답변에 반영되지 않습니다.</div>
<table><thead><tr><th>AI가 인용한 사이트</th><th class="num">인용 횟수</th></tr></thead><tbody>
{''.join(f'<tr><td>{e(dm)}</td><td class="num">{c}</td></tr>' for dm,c in meta['top_domains'][:12])}
</tbody></table>
<h2>4. 권고</h2>
<ol>
<li>위 <b>놓치고 있는 질문</b> 중 인용 출처가 적은 것부터 공략합니다. 질문 문장을 그대로 제목으로 쓰고 답을 첫 문단에 둡니다.</li>
<li>영문 콘텐츠의 절대량이 부족하면 위 작업이 성립하지 않습니다. 먼저 영문 페이지를 확보해야 합니다.</li>
<li>AI가 인용하는 제3자 매체에 정확한 정보가 실리도록 정리합니다.</li>
<li>월 1회 <b>동일한 질문 세트</b>로 재측정해 변화를 추적합니다.</li>
</ol>
<div class="foot"><b>측정 방법.</b> {e(meta['engine'])}에 {e(meta['lang'])}로 동일 질문을 질의해 응답 본문에
기업명이 등장하는지와 등장 순서를 집계했습니다. 각 질문을 {meta['repeat']}회씩 질의해 등장 빈도의 평균으로
노출률을 계산했습니다. AI 응답은 시점·지역·계정에 따라 달라지므로 단일 측정값이 아니라 추세로 해석해야 합니다.
본 진단은 {e(meta['engine'])} 기준이며 다른 AI 서비스의 결과를 보장하지 않습니다.
노출률은 위 {meta['questions']}개 질문에 한정된 수치입니다.</div></body></html>"""

cats={}
if os.path.exists('massscan.json'): cats.update(json.load(open('massscan.json',encoding='utf-8')))
if os.path.exists('medscan.json'):
    m=json.load(open('medscan.json',encoding='utf-8'))
    m['meta'].setdefault('label','의료관광 (성형·피부과)')
    cats['plastic']=m

master=[]
for key,v in cats.items():
    meta,rows,stats = v['meta'],v['rows'],v['stats']
    d=os.path.join(OUT, slug(meta['label'])); os.makedirs(d, exist_ok=True)
    for s in stats:
        open(os.path.join(d, slug(s['name'])+'.html'),'w',encoding='utf-8').write(
            build(s['name'],meta,rows,stats))
        master.append({"cat":meta['label'],"name":s['name'],"exposure":s['exposure'],
                       "missing":len(s['missing']),"q":meta['questions'],
                       "file":f"{slug(meta['label'])}/{slug(s['name'])}.html"})
master.sort(key=lambda x:(x['exposure'], -x['missing']))
json.dump(master, open(os.path.join(OUT,'master.json'),'w'), ensure_ascii=False, indent=1)
print(f"리포트 {len(master)}건 생성 → {OUT}/")
print(f"{'카테고리':<22}{'기업':<30}{'노출률':>7}{'미노출':>8}")
print('-'*70)
for m in master:
    print(f"{m['cat'][:20]:<22}{m['name'][:28]:<30}{m['exposure']*100:>6.0f}%{m['missing']:>6}/{m['q']}")
