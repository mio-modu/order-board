#!/usr/bin/env python3
"""
기준선과 같은 조건으로 재측정하고 전후를 비교한다.

사용법:
    GEMINI_API_KEY=... python3 remeasure.py                  # 전체
    GEMINI_API_KEY=... python3 remeasure.py kpopgo_en        # 특정 세트만
    GEMINI_API_KEY=... python3 remeasure.py --repeat 2       # 질문당 2회 질의

질문을 바꾸면 비교가 깨진다. baseline-*.json의 questions는 수정하지 말 것.
결과는 result-<날짜>.json 으로 저장되고, 직전 결과와 자동 비교된다.
"""
import json, os, re, sys, glob, urllib.request, datetime
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "gemini-3-flash-preview"
EP = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
KEY = os.environ.get("GEMINI_API_KEY", "")
BRAND_PAT = re.compile(r"kpopgo", re.I)


def ask(q, tries=3):
    body = {"contents": [{"parts": [{"text": q}]}], "tools": [{"google_search": {}}]}
    headers = {"Content-Type": "application/json"}
    if KEY:
        headers["x-goog-api-key"] = KEY
    req = urllib.request.Request(EP, method="POST", data=json.dumps(body).encode(), headers=headers)
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=240) as f:
                d = json.loads(f.read())
            c = d["candidates"][0]
            txt = "".join(p.get("text", "") for p in c["content"]["parts"])
            gm = c.get("groundingMetadata", {}) or {}
            chunks = gm.get("groundingChunks", []) or []
            # 기준선(scripts/precise.py)과 동일한 방식으로 뽑아야 비교가 성립한다.
            # grounding chunk의 uri는 리다이렉트 주소라 도메인이 아니다.
            # domain이 없으면 title로 떨어뜨린다 — 기준선이 그렇게 집계했다.
            doms = []
            for ch in chunks:
                w = ch.get("web", {}) or {}
                dm = (w.get("domain") or w.get("title") or "").lower()
                if dm:
                    doms.append(dm)
            return txt, sorted(set(doms)), bool(gm.get("webSearchQueries")) or bool(chunks)
        except Exception:
            if attempt == tries - 1:
                return "", [], False
    return "", [], False


def run_set(name, spec, repeat):
    qs = spec["questions"]
    rows = [None] * len(qs)

    def one(i):
        hits, srcs, fired = 0, set(), 0
        for _ in range(repeat):
            txt, doms, searched = ask(qs[i])
            if BRAND_PAT.search(txt) or any(BRAND_PAT.search(d) for d in doms):
                hits += 1
            srcs |= set(doms)
            fired += 1 if searched else 0
        rows[i] = {"q": qs[i], "cited": hits / repeat, "sources": sorted(srcs),
                   "search_rate": fired / repeat}

    with ThreadPoolExecutor(4) as ex:
        list(ex.map(one, range(len(qs))))

    n = len(rows) or 1
    return {
        "label": spec["label"], "language": spec["language"], "repeat": repeat,
        "rows": rows,
        "summary": {
            "questions": len(rows),
            "search_fired": round(sum(r["search_rate"] for r in rows), 2),
            "kpopgo_cited": round(sum(r["cited"] for r in rows), 2),
            "avg_sources": round(sum(len(r["sources"]) for r in rows) / n, 2),
        },
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    repeat = 1
    if "--repeat" in sys.argv:
        repeat = int(sys.argv[sys.argv.index("--repeat") + 1])

    base = json.load(open(os.path.join(HERE, "baseline-2026-10-23.json"), encoding="utf-8"))
    sets = base["sets"]
    targets = args or list(sets)

    today = datetime.date.today().isoformat()
    out = {"measured_at": today, "engine": MODEL, "repeat": repeat, "sets": {}}

    for name in targets:
        if name not in sets:
            print(f"  (없는 세트: {name})")
            continue
        print(f"▶ {name} — {sets[name]['label']} ({len(sets[name]['questions'])}문항 × {repeat}회)")
        out["sets"][name] = run_set(name, sets[name], repeat)

    path = os.path.join(HERE, f"result-{today}.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n저장: {path}\n")

    # ── 전후 비교 ──────────────────────────────────────
    print("=" * 72)
    print(f"{'세트':<16}{'지표':<14}{'기준선':>10}{'이번':>10}{'변화':>12}")
    print("-" * 72)
    for name, cur in out["sets"].items():
        b = sets[name]["baseline"]
        c = cur["summary"]
        for key, label in [("search_fired", "검색 발동"), ("kpogo", None),
                           ("kpopgo_cited", "KPOPGO 인용"), ("avg_sources", "평균 인용출처")]:
            if label is None:
                continue
            was, now = b.get(key, 0), c.get(key, 0)
            d = now - was
            mark = "→" if abs(d) < 1e-9 else ("▲" if d > 0 else "▼")
            print(f"{name:<16}{label:<14}{was:>10}{now:>10}{mark + f'{d:+.2f}':>12}")
        print("-" * 72)
    print("\n※ 평균 인용출처는 낮아지는 것이 좋다 (경쟁 밀도 감소).")
    print("※ 같은 날 여러 번 돌리면 결과가 흔들린다. --repeat 2 이상을 권장한다.")


if __name__ == "__main__":
    main()
