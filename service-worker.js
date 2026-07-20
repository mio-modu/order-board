/* Order Together — service worker
 * GitHub Pages 하위 경로(/order-board/) 배포이므로 모든 경로는 상대경로로 작성한다.
 * 절대경로("/...")를 쓰면 도메인 루트를 가리켜 404가 난다.
 */
const VERSION = 'v1';
const CACHE = `order-together-${VERSION}`;

// 같은 출처 — 반드시 캐싱되어야 하는 핵심 자원
const CORE = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
];

// 폰트 CDN — 실패해도 설치를 막지 않도록 best-effort로 캐싱
const CDN = [
  'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css',
  'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Instrument+Serif&display=swap',
];

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await cache.addAll(CORE);                       // 하나라도 실패하면 설치 실패 (의도적)
    await Promise.all(CDN.map((url) =>              // CDN은 실패를 삼킨다
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

// 폰트 파일 등 런타임에 발견되는 정적 자원
const isCacheableCDN = (url) =>
  url.hostname === 'fonts.googleapis.com' ||
  url.hostname === 'fonts.gstatic.com' ||
  url.hostname === 'cdn.jsdelivr.net';

self.addEventListener('fetch', (e) => {
  const req = e.request;

  // GET이 아니거나 http(s)가 아니면 그대로 통과 (Web Speech API 등 건드리지 않음)
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  const sameOrigin = url.origin === self.location.origin;
  if (!sameOrigin && !isCacheableCDN(url)) return;   // 그 외 외부 요청은 관여하지 않음

  // HTML 문서는 네트워크 우선 — 새 버전이 즉시 반영되도록. 오프라인이면 캐시로 폴백.
  if (req.mode === 'navigate' || (req.destination === 'document')) {
    e.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        const cache = await caches.open(CACHE);
        cache.put('./index.html', fresh.clone());
        return fresh;
      } catch (err) {
        const cached = await caches.match('./index.html', { ignoreSearch: true });
        return cached || Response.error();
      }
    })());
    return;
  }

  // 그 외 정적 자원은 캐시 우선, 없으면 네트워크 후 저장
  e.respondWith((async () => {
    const cached = await caches.match(req, { ignoreSearch: false });
    if (cached) return cached;
    try {
      const res = await fetch(req);
      // opaque(cors 불가) 응답도 폰트에는 유효하므로 함께 저장
      if (res && (res.ok || res.type === 'opaque')) {
        const cache = await caches.open(CACHE);
        cache.put(req, res.clone());
      }
      return res;
    } catch (err) {
      return cached || Response.error();
    }
  })());
});
