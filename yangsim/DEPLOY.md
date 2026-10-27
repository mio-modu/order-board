# 베르셀 배포 — 폰에서 5분

이 폴더(`yangsim/`)가 그대로 사이트입니다. 빌드 과정이 없습니다.

---

## ⚠ 순서를 꼭 지키세요

**Supabase를 먼저 붙이고 나서 링크를 퍼뜨리세요.**

Supabase 없이 배포하면 응답이 **각자의 브라우저에만** 저장됩니다.
링크를 먼저 돌리면 그 사람들의 기록은 어디에도 안 남고, 나중에 복구할 방법이 없습니다.
초기 응답자 수백 명이 통째로 사라집니다.

올바른 순서: **① Supabase → ② 코드 3줄 수정 → ③ 배포 → ④ 공유**

---

## ① Supabase (5분)

### 1-1. 프로젝트 만들기

**New project** 를 누르면 입력칸이 나옵니다.

| 칸 | 넣을 값 |
|---|---|
| Organization | 그대로 둡니다 |
| Project name | `yangsim` |
| Database Password | **Generate a password** 눌러서 자동 생성 |
| Region | **Northeast Asia (Seoul)** |
| Plan | Free |

> **Region은 꼭 Seoul로.** 기본값이 미국이면 한국에서 접속할 때마다
> 태평양을 왕복합니다. 결과 화면 뜨는 속도가 눈에 띄게 달라집니다.

> **Database Password는 안 쓰실 겁니다.** 이 사이트는 비밀번호가 아니라
> 아래에서 복사할 공개 키로 접속합니다. 그래도 Supabase가 요구하니
> 자동 생성해서 넣고 넘어가세요.

**Create new project** 누르면 1~2분 걸립니다. 커피 한 잔.

### 1-2. 표 만들기 (SQL 붙여넣기)

왼쪽 메뉴에서 **SQL Editor** → **New query** →
아래를 통째로 붙여넣고 오른쪽 아래 **Run**.

```sql
create table if not exists conscience_logs (
  id   bigint generated always as identity primary key,
  path text not null,
  hcq  int,
  type text,
  at   timestamptz default now()
);

alter table conscience_logs enable row level security;

drop policy if exists "anyone can insert" on conscience_logs;
drop policy if exists "anyone can read"   on conscience_logs;

create policy "anyone can insert"
  on conscience_logs for insert to anon with check (true);

create policy "anyone can read"
  on conscience_logs for select to anon using (true);

create index if not exists conscience_logs_path_idx on conscience_logs (path);
```

`Success. No rows returned` 가 뜨면 된 겁니다.

> 이 SQL은 **몇 번을 다시 돌려도 안전합니다.** 중간에 꼬였다 싶으면
> 그냥 처음부터 다시 붙여넣고 Run 하세요.

**무엇을 한 건지:**
- 기록을 담을 표를 만들고
- 보안(RLS)을 켠 다음
- **넣기(insert)** 와 **읽기(select)** 만 열었습니다.
  수정과 삭제는 아무에게도 열지 않았으므로, 남의 기록을 건드릴 수 없습니다.
- 읽기를 연 이유는 **희귀함(RQ) 계산 때문**입니다.
  내 답이 얼마나 드문지 알려면 전체 분포를 봐야 합니다.

### 1-3. 키 두 개 복사

왼쪽 메뉴 맨 아래 **Settings**(톱니바퀴) → **API**

두 가지를 복사해 둡니다.

1. **Project URL** — `https://xxxxxxxx.supabase.co`
2. **공개 키** — 화면에 따라 이름이 다릅니다
   - `anon` `public` 이라고 쓰인 긴 `eyJ...` 문자열, 또는
   - **Publishable key** 라고 쓰인 `sb_publishable_...` 문자열

   **둘 중 보이는 것을 쓰면 됩니다.** 둘 다 보이면 아무거나 상관없습니다.

> ⚠ **`service_role` 또는 `secret` 이라고 쓰인 키는 절대 쓰지 마세요.**
> 그 키는 보안을 전부 통과합니다. 사이트에 넣으면 누구나 전체 데이터를
> 지울 수 있게 됩니다. 반드시 **anon / public / publishable** 쪽입니다.

> 공개 키는 **코드에 그대로 박아도 되는 키**입니다. 위에서 켠 RLS가
> 넣기·읽기만 허용하기 때문에, 가져가도 할 수 있는 게 그 둘뿐입니다.

## ② 코드 3줄 수정

깃허브에서 `yangsim/index.html` 을 열고 **연필 아이콘**을 누릅니다.
(폰에서도 됩니다)

브라우저 찾기로 `const SUPABASE` 를 찾으면 파일 위쪽에 이렇게 생긴 곳이 있습니다.

```js
const SUPABASE = {
  url:   '',
  key:   '',
  table: 'conscience_logs'
};
```

따옴표 **안쪽**에 1-3에서 복사한 것을 넣습니다.

```js
const SUPABASE = {
  url:   'https://xxxxxxxx.supabase.co',
  key:   'eyJhbGciOiJIUzI1NiIsInR5cCI6...',
  table: 'conscience_logs'
};
```

- 따옴표를 지우지 마세요
- 줄 끝 쉼표(`,`)를 지우지 마세요
- `table` 줄은 그대로 둡니다

**Commit changes** 를 누르면 저장됩니다.

> 주소 끝에 `/` 를 붙이지 마세요. `https://xxxx.supabase.co` 까지입니다.

---

## ③ 배포

1. vercel.com → **Add New → Project**
2. **Import Git Repository** 에서 `mio-modu/order-board` 선택
3. 설정 화면에서 **두 개만** 바꿉니다
   - **Project Name** → `yangsim`  ← 이 이름이 주소가 됩니다
   - **Root Directory** → `yangsim`  (Edit 눌러서 폴더 선택)
4. **Deploy**

끝나면 `https://yangsim.vercel.app` 으로 열립니다.

> **Project Name을 `yangsim`으로 해야** 이 폴더에 들어 있는 OG 이미지 주소가
> 그대로 맞습니다. 다른 이름이 배정되면 `index.html` 상단 주석에 표시된
> 세 줄의 주소만 바꾸면 됩니다.

---

## ④ 확인 (공유 전에)

- [ ] 사이트가 열리고 질문이 나온다
- [ ] 다섯 문항을 끝까지 풀면 결과가 나온다
- [ ] Supabase → **Table Editor → conscience_logs** 에 **행이 1개 생겼다** ← 가장 중요
      (`path` 칸에 `01-10-02-21-13` 같은 값이 들어 있어야 합니다)
- [ ] 다른 기기(또는 시크릿창)에서 열었을 때 상단 숫자가 올라가 있다
- [ ] 카카오톡 나에게 링크 보내기 → 미리보기 이미지가 뜬다

**3번이 안 되면 공유하지 마세요.** 데이터가 안 쌓이고 있다는 뜻입니다.

---

## 나중에 도메인 옮길 때

1. 도메인 구입
2. Vercel → 프로젝트 → **Settings → Domains → Add**
3. `index.html`, `robots.txt`, `sitemap.xml` 안의
   `yangsim.vercel.app` 을 새 도메인으로 바꾸기

`yangsim.vercel.app` 주소는 계속 살아 있으니 **이미 퍼진 링크도 안 깨집니다.**
데이터는 Supabase에 있어서 도메인과 무관하게 그대로 이어집니다.

---

## 폴더 안에 있는 것

| 파일 | 역할 |
|---|---|
| `index.html` | 사이트 전부. 배경 이미지까지 이 안에 들어 있습니다 |
| `og.jpg` | 카카오톡·트위터 링크 미리보기 이미지 (1200×630) |
| `llms.txt` | AI가 이 사이트를 읽을 때 보는 설명 |
| `robots.txt` / `sitemap.xml` | 검색엔진용 |
| `vercel.json` | 캐시·보안 헤더 |


---

## 나중에 알려주셔야 할 것

### 응답이 2만 건을 넘으면

지금 구조는 희귀함(RQ)을 계산하려고 **전체 기록을 받아와서** 셉니다.
2만 건까지는 문제없지만, 그 이상이면 방문자마다 받는 양이 커져 느려집니다.

그때 집계 함수로 바꾸면 10만, 100만까지 그대로 갑니다.
**N이 2만 가까워지면 알려주세요.** 10분이면 바꿉니다.

### 무료 플랜 일시정지

무료 프로젝트는 **일주일 내내 아무 접속이 없으면** 잠듭니다.
사람이 들어오고 있으면 안 잠기고, 잠겨도 대시보드에서 한 번 깨우면
데이터는 그대로입니다. 다만 그 사이 방문자는 기록이 안 남으니,
초반에 조용한 시기가 길어지면 한 번씩 들어가 보세요.
