/* Order Together — service worker
 *
 * GitHub Pages 하위 경로(/order-board/) 배포이므로 모든 경로는 상대경로로 작성한다.
 * 절대경로("/...")를 쓰면 도메인 루트를 가리켜 404가 난다.
 *
 * 내용을 수정해 배포할 때는 아래 VERSION을 반드시 올릴 것.
 * 같은 오리진이 캐시 우선이라, 버전을 올리지 않으면 사용자에게 옛 화면이 계속 보인다.
 */
const VERSION = 'v3';
const CACHE = `order-together-${VERSION}`;

// 같은 오리진 — 반드시 캐싱되어야 하는 앱 셸
const CORE = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

// 폰트 CDN — 실패해도 설치를 막지 않도록 best-effort
const CDN = [
  'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css',
  'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Instrument+Serif&display=swap',
];

// 폰트 CDN 호스트 (css가 참조하는 woff2도 런타임에 캐싱된다)
const FONT_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net'];

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await cache.addAll(CORE);                       // 하나라도 실패하면 설치 실패 (의도적)
    await Promise.all(CDN.map((url) =>
      cache.add(new Request(url, { mode: 'cors' })).catch(() => {})
    ));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(
      keys.filter((k) => k.startsWith('order-together-') && k !== CACHE)
          .map((k) => caches.delete(k))             // 이전 버전 캐시 삭제
    );
    await self.clients.claim();
  })());
});

// 캐시 우선, 없으면 네트워크 (받아온 응답은 캐시에 저장)
async function cacheFirst(req) {
  const cached = await caches.match(req);
  if (cached) return cached;
  try {
    const res = await fetch(req);
    if (res && (res.ok || res.type === 'opaque')) {
      const cache = await caches.open(CACHE);
      cache.put(req, res.clone());
    }
    return res;
  } catch (err) {
    // 오프라인이고 캐시에도 없을 때: 문서 요청이면 앱 셸로 폴백
    if (req.mode === 'navigate' || req.destination === 'document') {
      const shell = await caches.match('./index.html');
      if (shell) return shell;
    }
    return Response.error();
  }
}

self.addEventListener('fetch', (e) => {
  const req = e.request;

  // GET이 아니면 가로채지 않는다.
  // Web Speech API는 브라우저 내장 음성 스트림이라 fetch를 거치지 않지만,
  // 혹시 모를 비-GET 요청까지 확실히 통과시킨다.
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  if (url.origin === self.location.origin) {   // 같은 오리진 → 캐시 우선
    e.respondWith(cacheFirst(req));
    return;
  }
  if (FONT_HOSTS.includes(url.hostname)) {     // 폰트 CDN → 캐시 우선
    e.respondWith(cacheFirst(req));
    return;
  }
  // 그 외 외부 요청 → 가로채지 않고 네트워크로 그대로 (respondWith 호출 안 함)
});
