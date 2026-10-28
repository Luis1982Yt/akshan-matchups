// Service worker: deixa o site abrir sem internet (com a última versão vista) e instalável no celular.
// A página sempre tenta a rede primeiro, então quem tem conexão vê a versão nova na hora.
// A planilha (docs.google.com) não passa por aqui: o site já guarda a última cópia sozinho.
const CACHE = "battlematch-v1";
const BASE = ["/", "/manifest.webmanifest", "/icones/icone-192.png", "/icones/icone-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Guarda a resposta e devolve ela (só respostas boas; imagens de outro site vêm "opacas", e tudo bem).
const guarda = (req, res) => {
  if (res && (res.ok || res.type === "opaque")) {
    const copia = res.clone();
    caches.open(CACHE).then(c => c.put(req, copia));
  }
  return res;
};

self.addEventListener("fetch", e => {
  const req = e.request;
  // Sons e vídeos pedem pedaços do arquivo (Range); esses o cache não aceita, vão direto para a rede.
  if (req.method !== "GET" || req.headers.has("range")) return;
  const url = new URL(req.url);
  if (url.hostname === "docs.google.com" || url.hostname === "decapi.me") return;
  if (url.pathname.startsWith("/_vercel/")) return;  // contador de visitas: sempre direto da rede

  // Página: rede primeiro; sem internet, a última versão guardada.
  if (req.mode === "navigate") {
    // Só a página do site (/ ou /index.html) vira a cópia para abrir sem internet.
    const principal = url.pathname === "/" || url.pathname === "/index.html";
    e.respondWith(fetch(req).then(res => (principal ? guarda("/", res) : res)).catch(() => caches.match("/")));
    return;
  }
  // Imagens do Data Dragon, three.js, sons e o modelo 3D: responde do cache e atualiza por trás.
  const daRiot = url.hostname.endsWith("leagueoflegends.com") || url.hostname.endsWith("communitydragon.org");
  if (daRiot || url.hostname === "cdn.jsdelivr.net" || url.origin === self.location.origin) {
    e.respondWith(caches.match(req).then(salvo => {
      const rede = fetch(req).then(res => guarda(req, res)).catch(() => salvo);
      return salvo || rede;
    }));
  }
});
