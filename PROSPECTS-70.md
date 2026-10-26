# 발송 명단 70곳 — 리포트 생성 완료

측정 2026-10-26 · 카테고리당 20문항 × 2회 반복 · 전 카테고리 검색 발동률 **100%**
리포트 위치: `geo-baseline/prospects-2026-10-26/`

---

## 한 줄 요약

**70곳 측정, 47곳이 노출률 5% 이하.** 각 기업별 진단 리포트 HTML이 이미 만들어져 있다.
브라우저로 열어 인쇄 → PDF로 저장하면 그대로 첨부 파일이 된다.

---

## 발송 우선순위 — 5주 안에 돈이 되는 순서

판단 기준은 노출률이 아니라 **예산 × 의사결정 속도**다.

### 1순위 — 치과 의료관광 (12곳, 전원 5% 이하)

| 노출률 | 기업 |
|---|---|
| 0% | W Style Dental · Good Life Dental Party · E-Line Orthodontic · Yonsei U-Line Dental · Apple Tree Dental Hospital · Su-Dental Clinic |
| 2% | Oaks Dental · MINISH Dental Hospital · Bright Dental · Seoul Guide Medical |
| 5% | S-PLANT Dental Hospital · Hus-hu Dental Clinic |

**이 카테고리가 가장 비어 있다.** 12곳 전부 5% 이하이고 1위가 5%다.
즉 **아무도 자리를 잡지 않았다.** 평균 인용출처 11.6.

왜 1순위인가: 외국인 임플란트·교정 환자는 객단가가 높고, **원장이 바로 결재한다.**
병원은 조직이 작아 의사결정이 빠르다. 5주 안에 계약까지 갈 수 있는 거의 유일한 집단이다.

### 1순위 — 성형외과 (4곳)

Dream Plastic Surgery 0% · Eunogo 2% · Docfinderkorea 2% · Wonjin Plastic Surgery 5%
(2026-10-24 측정, 리포트는 `prospects-2026-10-24/`에도 있음)

### 2순위 — 한국 여행·투어 (9곳)

| 노출률 | 기업 |
|---|---|
| 0% | Funtastic Korea · HanaTour ITC · Global Interpark · Wondertrip · Indie-way · This is Korea |
| 2% | Seoul Pass · KoreaTravelEasy |
| 5% | Creatrip |

영문 사이트가 **본업**인데 0%다. 설득이 쉽다. 다만 예산이 병원보다 작다.
1위 Klook이 48%로 이미 자리를 잡아, "뺏긴다"는 메시지가 강하게 먹힌다.

### 2순위 — K-푸드 해외직구 (7곳) / K-뷰티 (6곳)

K-푸드 0%: Cokoyam · Okvit · NikanKitchen · Kooding
K-뷰티 0%: TesterKorea · KoreaDepart · Gmarket Global

해외 판매가 본업이라 영문 필요성이 명확하다. 규모가 작은 곳이 섞여 있어 단가가 내려갈 수 있다.

### 장기 — 대학 한국어학당 (9곳, 전원 0%)

연세대 · 서강대 · 서울대 · 고려대 · 이화여대 · 경희대 어학당, Go! Go! Hanguk,
가나다 한국어학원, Best Friend Korean Language School — **전부 0%다.**

측정값만 보면 가장 충격적이다. 1위 Lexis Korea가 28%인데 주요 대학 어학당이 전멸이다.
외국인 유학생 유치가 KPI인 기관들이 영문 AI 답변에 한 번도 안 나온다.

**다만 5주 안에는 돈이 안 된다.** 대학은 공공 조달 절차를 탄다.
수의계약 한도, 품의, 입찰이 걸려 두세 달이 기본이다.
**임팩트는 가장 크지만 지금 목표에는 맞지 않는다.** 11월에 씨만 뿌려두고 내년에 거둔다.

---

## 발송 방법

1. `geo-baseline/prospects-2026-10-26/<카테고리>/<기업명>.html` 을 브라우저로 연다
2. 인쇄 → PDF로 저장
3. `SALES-500.md`의 콜드메일 문안에 수치를 채워 넣고 PDF를 첨부해 보낸다

수치는 리포트 상단 숫자를 그대로 쓰면 된다.

---

## 보내기 전 확인

- [ ] **측정일이 2주 이상 지나면 다시 돌린다.** 재생성은 아래 한 줄
- [ ] 노출률 0%는 **20개 질문 기준**이다. "전혀 안 나온다"로 확대하지 않는다
- [ ] 대학·공공기관은 5주 목표에서 제외한다
- [ ] 50~80곳은 보내야 계약 1~2건이 나온다. 70곳이 준비되어 있으니 **전부 보낸다**

```bash
cd geo-baseline/scripts
python3 -I massscan.py && python3 -I massreport.py ../prospects-$(date +%F)
```

---

## 카테고리별 측정 요약

| 카테고리 | 검색 발동 | 평균 인용출처 | 1위 | 1위 노출률 |
|---|---|---|---|---|
| 치과 의료관광 | 100% | 11.6 | S-PLANT Dental | **5%** |
| 성형·피부과 | 100% | 12.6 | JK Plastic Surgery | 30% |
| 한국어 어학연수 | 100% | 14.4 | Lexis Korea | 28% |
| 한국 여행·투어 | 100% | 9.2 | Klook | 48% |
| K-뷰티 | 100% | 14.9 | YesStyle | 35% |
| K-푸드 | 100% | 8.7 | Seoulbox | 35% |

**여섯 카테고리 전부 검색 발동률 100%다.** 영어권은 AI가 매번 웹을 검색한다.
한국어 질의가 0%였던 것과 정반대이며, 이것이 영어권 타깃만 고른 이유다.
