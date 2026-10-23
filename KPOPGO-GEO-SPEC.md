# KPOPGO GEO 실행 지시서

측정일 2026-10-23 · Gemini 검색연동 질문 31개 + 사이트 기술 실측

---

## ⚠️ 앞선 진단 정정

처음에 "글을 써라, 스키마를 넣어라"라고 했는데 **틀렸다.** 실제로 사이트를 뜯어보니 이미 되어 있다.

| 항목 | 실측 결과 |
|---|---|
| sitemap URL | **234개** |
| 가이드 JSON-LD | **HowTo + FAQPage + BreadcrumbList** 전 페이지 적용 |
| dateModified | 있음 (10/20~22 대량 갱신) |
| robots.txt | `User-Agent: * / Allow: /` — AI 크롤러 차단 없음 |
| H1 | 질문형으로 이미 작성됨 |
| 추천하려던 글들 | `fan-club-presale-checklist`, `foreign-card-declined-korean-ticketing`, `order-from-weverse-shop-overseas` — **전부 이미 존재** |

**기술 GEO는 상위 1% 수준으로 이미 끝나 있다.** 남은 기술 공백은 `llms.txt` 하나뿐이다.

### 그럼 왜 31개 질문 중 3개에서만 인용되나

```
datePublished : 2026-10-14  (전 페이지 동일)
측정일         : 2026-10-23
사이트 나이     : 9일
```

**이게 답이다.** 사이트가 9일 됐다. 콘텐츠 문제도, 기술 문제도 아니다.

오히려 **9일짜리 신생 도메인이 31개 질문 중 3개에서 인용된 건 빠른 편이다.**
비교 대상인 haniseoul.com(11회), kpoptrips.com(9회), whatsonkr.com(9회)은 축적된 사이트들이다.

> **가장 큰 리스크는 지금 성급하게 판단하는 것이다.** 9일 데이터로 GEO 효과를 결론내면 안 된다.
> 최소 4주, 가능하면 8주를 봐야 한다.

---

## A. 사이트 제작 툴에 넘길 것 (전체의 약 10%)

아래를 그대로 지시서로 전달하면 된다.

### A-1. ~~`llms.txt` 생성~~ — **완료됨 (2026-10-23 확인)**

`/llms.txt`(14,574자)와 `/llms-full.txt` 모두 배포되어 서빙 중이다. 아래는 생성 당시 기록이다.

(이전 상태: 둘 다 404였다.) AI 크롤러가 사이트 구조를 파악하는 신규 표준이다.

```
# KPOPGO

> English-language procedural guides for international K-pop fans buying
> concert tickets, fan club memberships and albums from outside Korea.
> Every guide is checked against the live platform and dated.

## Guides
- [Buying K-pop concert tickets from overseas](https://kpopgo.app/guides/buy-k-pop-concert-tickets-from-overseas): Full procedure for fans outside Korea
- [NOL World ticketing (formerly Interpark Global)](https://kpopgo.app/guides/nol-world-ticketing-guide): ...
(234개 중 주요 가이드를 이 형식으로 나열)

## Reference
- [All guides index](https://kpopgo.app/guides)
- [Korean words on ticketing sites](https://kpopgo.app/words)
- [Editorial policy](https://kpopgo.app/editorial-policy)
```

`llms-full.txt`는 각 가이드의 본문 요약까지 포함한 확장판으로 생성한다.

### A-2. FAQPage에 날짜 추가

현재 `HowTo`에는 `dateModified`가 있으나 **`FAQPage`에는 없다.**
AI가 FAQ 블록에서 답을 뽑을 때 신선도를 판단할 근거가 사라진다. HowTo와 동일한 날짜를 넣는다.

### A-3. 가시적 날짜 표기

스키마상의 날짜 말고, **사람이 보는 본문 상단에** 표기한다. AI는 본문 텍스트도 읽는다.

```
Last checked on the live platform: 21 October 2026
```

### A-4. 신규 페이지 3개 — 측정으로 확인된 빈 자리

인용 출처가 극단적으로 적은 질문들이다. 기존 페이지와 **각도가 겹치지 않게** 분리한다.

| 신규 슬러그 | 겨냥 질문 | 현재 인용 출처 | 기존 페이지와의 차이 |
|---|---|---|---|
| `weverse-shop-payment-methods-international` | "Which payment methods work for international fans on Weverse Shop?" | **weverse.io 1개뿐** | `order-from-weverse-shop-overseas`는 주문 절차. 이건 **결제수단 자체**(카드사별·페이팔·간편결제 가부) |
| `weverse-membership-presale-walkthrough` | "How does Weverse membership presale work for international fans?" | facebook, reddit (전문 가이드 0) | `weverse-membership-renewal-overseas`는 갱신. 이건 **선예매 참여 절차** |
| `weverse-shop-vs-ktown4u` | "Is Weverse Shop or Ktown4u better for international album orders?" | paysable, reddit | `buy-k-pop-albums-from-overseas`는 총론. 이건 **1:1 비교표** |

**작성 규칙 (AI 인용 확률을 올리는 형식)**

1. `<h1>`을 **질문 문장 그대로** 쓴다 (AI는 질문↔제목을 매칭한다)
2. **첫 문단에 답을 먼저 쓴다.** 배경 설명은 그 뒤
3. 비교·목록은 반드시 **표**로. AI는 구조화된 데이터를 선호한다
4. 구체 수치를 넣는다 — "카드가 거절된다"가 아니라 "3DS 인증 단계에서 실패, Visa 해외결제 차단이 원인"
5. `HowTo` + `FAQPage` + `dateModified` 스키마는 기존 가이드와 동일하게 적용
6. 기존 234페이지와 **키워드 카니발 체크** — 중복되면 둘 다 순위를 잃는다

### A-5. 내부 링크 허브

신규 3개 페이지를 `/guides` 인덱스와 관련 기존 가이드에서 **양방향으로** 링크한다.
신생 페이지는 내부 링크가 유일한 초기 권위 공급원이다.

### A-6. 하지 말 것

- 기존 234페이지를 건드리는 대규모 리팩터링. 이미 잘 되어 있다
- 글 수를 늘리는 것 자체를 목표로 삼는 것. **얇은 페이지가 늘면 전체 품질 평가가 내려간다**
- 9일 된 데이터로 구조를 다시 뒤집는 것

---

## B. 사람이 해야 할 것 (전체의 약 90%)

**사이트 툴로는 해결되지 않는다.** AI가 인용하는 건 "잘 만든 페이지"가 아니라 **"다른 곳에서 언급되는 페이지"**다.

### B-1. Reddit — 가장 빠른 경로

측정 결과 AI가 인용한 도메인 **1위가 reddit.com(14회)**이다. 2위 haniseoul(11회)보다 많다.

- 대상: r/kpophelp, r/kpop, 아티스트별 서브레딧
- 방식: 위 질문들에 **실제로 도움이 되는 답을 전부 적고**, 근거로 해당 가이드를 링크
- 금지: 링크만 던지는 홍보. 삭제·밴 당하고 도메인 평판까지 깎인다
- 빈도: 주 2~3개. 계정 하나로 꾸준히

### B-2. 같은 체급 사이트와의 상호 인용

경쟁 상대는 Interpark나 Weverse가 아니라 **1인 가이드 사이트들**이다.
haniseoul.com, kpoptrips.com, whatsonkr.com, gofarther.blog, namanecard.com, teuida.net

게스트 기고, 상호 링크, 자료 인용 요청 — 이들과는 제로섬이 아니다. 같이 인용되는 구조가 가능하다.

### B-3. 시간

9일 → 4주 → 8주. **이 변수만큼은 돈으로도 코드로도 못 줄인다.**

---

## C. 측정 루프

주 1회, **같은 질문 31개**로 재측정한다. 질문을 바꾸면 비교가 깨진다.

| 지표 | 출처 | 2026-10-23 기준 |
|---|---|---|
| AI Assistant 세션수 | GA4 채널 그룹 | 1 |
| 31개 질문 중 KPOPGO 노출 | 스캔 재실행 | 3 |
| kpopgo.app 인용 횟수 | 스캔 재실행 | 3 |
| reddit.com 인용 횟수 (경쟁 기준선) | 스캔 재실행 | 14 |

**GA4의 "AI Assistant" 채널이 이 사업의 핵심 자산이다.**
GEO 업계 최대 약점이 효과 증명 불가인데, 고객 본인 GA4에 찍히는 숫자는 반박이 불가능하다.
팔아야 할 상품은 "AI 노출을 올려드립니다"가 아니라 **"AI 유입을 측정 가능하게 만들고 그 숫자를 올립니다"**다.

---

## D. 한계

- **Gemini 단일 엔진** 측정이다. ChatGPT·Perplexity는 다를 수 있다
- 주간 활성 사용자 24명, AI Assistant 1세션은 통계적으로 의미 있는 표본이 아니다.
  파이프가 뚫려 있다는 증거이지 돈이 된다는 증거가 아니다
- 영어 질의는 검색 발동 31/31이었으나 한국어 질의는 0/36이었다.
  이 전략은 **영문 사이트에만** 그대로 적용된다 (계산모아·받을돈에는 적용되지 않는다)
