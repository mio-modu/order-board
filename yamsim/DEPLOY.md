# 베르셀 배포 — 폰에서 5분

이 폴더(`yamsim/`)가 그대로 사이트입니다. 빌드 과정이 없습니다.

---

## ⚠ 순서를 꼭 지키세요

**Supabase를 먼저 붙이고 나서 링크를 퍼뜨리세요.**

Supabase 없이 배포하면 응답이 **각자의 브라우저에만** 저장됩니다.
링크를 먼저 돌리면 그 사람들의 기록은 어디에도 안 남고, 나중에 복구할 방법이 없습니다.
초기 응답자 수백 명이 통째로 사라집니다.

올바른 순서: **① Supabase → ② 코드 3줄 수정 → ③ 배포 → ④ 공유**

---

## ① Supabase (3분)

1. supabase.com 접속 → 로그인 → **New project** (무료 플랜)
2. 프로젝트가 만들어지면 왼쪽 메뉴 **SQL Editor** → 아래를 그대로 붙여넣고 **Run**

```sql
create table conscience_logs (
  id   bigint generated always as identity primary key,
  path text not null,
  hcq  int,
  type text,
  at   timestamptz default now()
);

alter table conscience_logs enable row level security;

create policy "anyone can insert"
  on conscience_logs for insert to anon with check (true);

create policy "anyone can read"
  on conscience_logs for select to anon using (true);
```

3. 왼쪽 메뉴 **Settings → API** 에서 두 가지를 복사
   - **Project URL** (`https://xxxx.supabase.co`)
   - **anon public** 키 (`eyJ...` 로 시작하는 긴 문자열)

> anon 키는 공개돼도 되는 키입니다. 위 RLS가 insert·select만 열어두기 때문에
> 누구도 남의 기록을 지우거나 고칠 수 없습니다.

---

## ② 코드 3줄 수정

`yamsim/index.html` 안에서 `const SUPABASE` 를 찾아 세 줄을 채웁니다.
(깃허브 웹에서 연필 아이콘 눌러 폰으로도 수정됩니다)

```js
const SUPABASE = {
  url:   'https://xxxx.supabase.co',
  key:   'eyJ...',
  table: 'conscience_logs'
};
```

---

## ③ 배포

1. vercel.com → **Add New → Project**
2. **Import Git Repository** 에서 `mio-modu/order-board` 선택
3. 설정 화면에서 **두 개만** 바꿉니다
   - **Project Name** → `yamsim`  ← 이 이름이 주소가 됩니다
   - **Root Directory** → `yamsim`  (Edit 눌러서 폴더 선택)
4. **Deploy**

끝나면 `https://yamsim.vercel.app` 으로 열립니다.

> **Project Name을 `yamsim`으로 해야** 이 폴더에 들어 있는 OG 이미지 주소가
> 그대로 맞습니다. 다른 이름이 배정되면 `index.html` 상단 주석에 표시된
> 세 줄의 주소만 바꾸면 됩니다.

---

## ④ 확인 (공유 전에)

- [ ] 사이트가 열리고 질문이 나온다
- [ ] 다섯 문항을 끝까지 풀면 결과가 나온다
- [ ] Supabase → **Table Editor → conscience_logs** 에 **행이 1개 생겼다** ← 가장 중요
- [ ] 다른 기기(또는 시크릿창)에서 열었을 때 상단 숫자가 올라가 있다
- [ ] 카카오톡 나에게 링크 보내기 → 미리보기 이미지가 뜬다

**3번이 안 되면 공유하지 마세요.** 데이터가 안 쌓이고 있다는 뜻입니다.

---

## 나중에 도메인 옮길 때

1. 도메인 구입
2. Vercel → 프로젝트 → **Settings → Domains → Add**
3. `index.html`, `robots.txt`, `sitemap.xml` 안의
   `yamsim.vercel.app` 을 새 도메인으로 바꾸기

`yamsim.vercel.app` 주소는 계속 살아 있으니 **이미 퍼진 링크도 안 깨집니다.**
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
