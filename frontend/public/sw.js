/*
 * CareerPath offline support. Pages a student has opened keep working with weak or no internet.
 * Fresh data always wins when the network works; the saved copy is only a fallback.
 * Nothing private is saved: sign-in, account, admin and assistant requests are never stored.
 */
const VERSION = 'careerpath-v1'
const SHELL = ['/', '/manifest.webmanifest', '/favicon.svg', '/icon-192.png', '/icon-512.png']
const PRIVATE = ['/api/v1/auth', '/api/v1/me', '/api/v1/admin', '/api/v1/assistant']

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(VERSION).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()))
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== VERSION).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  )
})

async function networkFirst(request, fallbackUrl) {
  const cache = await caches.open(VERSION)
  try {
    const response = await fetch(request)
    if (response.ok) cache.put(fallbackUrl ?? request, response.clone())
    return response
  } catch {
    const saved = await cache.match(fallbackUrl ?? request)
    if (saved) return saved
    throw new Error('Offline and not saved yet')
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(VERSION)
  const saved = await cache.match(request)
  if (saved) return saved
  const response = await fetch(request)
  if (response.ok) cache.put(request, response.clone())
  return response
}

self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  if (request.method !== 'GET' || url.origin !== self.location.origin) return
  if (PRIVATE.some((path) => url.pathname.startsWith(path))) return

  if (request.mode === 'navigate') {
    // Every page is the same app, so one saved copy of it opens any page offline
    event.respondWith(networkFirst(request, '/'))
  } else if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request))
  } else if (url.pathname.startsWith('/assets/') || /\.(png|svg|webmanifest|woff2?)$/.test(url.pathname)) {
    event.respondWith(cacheFirst(request))
  }
})
