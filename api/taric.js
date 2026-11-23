// Modo editor do guia do Taric: o mono Taric escreve as dicas direto no site.
// Roda na Vercel (função sem dependência nenhuma). Só sabe mexer num arquivo: src/guias/taric/notas.json.
// Nenhum outro guia pode ser alterado por aqui, nem com a senha.
// Precisa de duas variáveis na Vercel (Settings > Environment Variables):
//   EDITOR_SENHA  a senha que o dono passa para o mono Taric
//   GITHUB_TOKEN  token do GitHub com permissão só de escrever neste repositório (Contents: Read and write)
// Cada "Salvar" vira um commit na main; o workflow taric-editor.yml remonta o guia e a Vercel publica.
const crypto = require("crypto");

const REPO = "Luis1982Yt/akshan-matchups";
const NOTAS = "src/guias/taric/notas.json";
const MATCHUPS = "src/guias/taric/matchups.json";
const MAX_LINHAS = 30, MAX_LETRAS = 600;

const igual = (a, b) => {
  const x = crypto.createHash("sha256").update(String(a)).digest();
  const y = crypto.createHash("sha256").update(String(b)).digest();
  return crypto.timingSafeEqual(x, y);
};

async function github(caminho, opcoes = {}) {
  const r = await fetch(`https://api.github.com/repos/${REPO}/contents/${caminho}`, {
    ...opcoes,
    headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN}`, Accept: "application/vnd.github+json", "User-Agent": "battlematch-editor", ...(opcoes.headers || {}) },
  });
  return r;
}
async function le(caminho) {
  const r = await github(caminho + "?ref=main");
  if (!r.ok) throw new Error("GitHub " + r.status);
  const j = await r.json();
  return { sha: j.sha, dados: JSON.parse(Buffer.from(j.content, "base64").toString("utf8")) };
}

// Fragmentos que o site sabe mostrar (os nomes batem com scripts/atualizar_mordekaiser.py FRAGMENTOS).
const FRAGMENTOS = [["Adaptive Force", "Attack Speed", "Ability Haste"], ["Adaptive Force", "Move Speed", "Health Scaling"], ["Health", "Tenacity", "Health Scaling"]];
// Runas e feitiços oficiais da versão atual do jogo (Data Dragon), para nunca gravar nome que o guia não reconhece.
async function dadosDoJogo() {
  const ver = (await (await fetch("https://ddragon.leagueoflegends.com/api/versions.json")).json())[0];
  const base = `https://ddragon.leagueoflegends.com/cdn/${ver}/data/en_US/`;
  const arvores = await (await fetch(base + "runesReforged.json")).json();
  const feiticos = (await (await fetch(base + "summoner.json")).json()).data;
  return { arvores, feiticos: new Set(Object.values(feiticos).filter(f => (f.modes || []).includes("CLASSIC")).map(f => f.id)) };
}
// Página de runas no formato do notas.json: principal (4, da mesma árvore, uma por linha), secundária (2, de outra
// árvore, linhas diferentes, sem a pedra angular) e 3 fragmentos. Devolve null se algo não bater.
function validaRunas(r, arvores) {
  if (!r || !Array.isArray(r.principal) || !Array.isArray(r.secundaria) || !Array.isArray(r.fragmentos)) return null;
  const linha = (arv, nome) => arv.slots.findIndex(s => s.runes.some(x => x.name === nome));
  const pri = arvores.find(a => r.principal.length === 4 && r.principal.every((n, i) => linha(a, n) === i));
  const sec = arvores.find(a => a !== pri && r.secundaria.length === 2 && r.secundaria.every(n => linha(a, n) > 0));
  if (!pri || !sec || linha(sec, r.secundaria[0]) === linha(sec, r.secundaria[1])) return null;
  if (r.fragmentos.length !== 3 || !r.fragmentos.every((f, i) => FRAGMENTOS[i].includes(f))) return null;
  return { principal: r.principal, secundaria: r.secundaria, fragmentos: r.fragmentos };
}

// Uma dica por linha, sem linha vazia, com limite de tamanho.
const linhas = t => String(t || "").split(/\r?\n/).map(l => l.trim().replace(/\s+/g, " ")).filter(Boolean)
  .slice(0, MAX_LINHAS).map(l => l.slice(0, MAX_LETRAS));

module.exports = async (req, res) => {
  if (req.method !== "POST") return res.status(405).json({ erro: "use POST" });
  if (!process.env.EDITOR_SENHA || !process.env.GITHUB_TOKEN) return res.status(503).json({ erro: "editor ainda não configurado na Vercel" });
  const b = req.body || {};
  if (!igual(b.senha || "", process.env.EDITOR_SENHA)) {
    await new Promise(r => setTimeout(r, 800));  // freia quem tenta adivinhar a senha
    return res.status(401).json({ erro: "senha errada" });
  }
  if (b.acao === "entrar") return res.json({ ok: true });

  const { campeao, campo } = b;
  if (!["dicas", "sinergia", "setup"].includes(campo)) return res.status(400).json({ erro: "campo inválido" });
  const difCampo = campo === "dicas" && b.tipo === "adc" ? "dificuldade_adc" : campo === "dicas" ? "dificuldade" : null;
  const dif = b.dificuldade === null || b.dificuldade === "" || b.dificuldade === undefined ? null : Number(b.dificuldade);
  if (dif !== null && !(Number.isInteger(dif) && dif >= 1 && dif <= 5)) return res.status(400).json({ erro: "dificuldade de 1 a 5" });

  try {
    const ids = new Set((await le(MATCHUPS)).dados.matchups.map(m => m.id));
    if (!ids.has(campeao)) return res.status(400).json({ erro: "campeão desconhecido" });
    let setup = null;
    if (campo === "setup") {
      // Setup do confronto: runas, feitiços e anotações (itens, plano de jogo). Tudo opcional.
      const e = b.setup || {}, jogo = await dadosDoJogo();
      setup = {};
      if (e.runas) {
        const r = validaRunas(e.runas, jogo.arvores);
        if (!r) return res.status(400).json({ erro: "página de runas incompleta ou inválida" });
        setup.runas = r;
      }
      if (e.feiticos && e.feiticos.length) {
        if (e.feiticos.length !== 2 || e.feiticos[0] === e.feiticos[1] || !e.feiticos.every(f => jogo.feiticos.has(f)))
          return res.status(400).json({ erro: "escolha dois feitiços diferentes" });
        setup.feiticos = e.feiticos;
      }
      const notas = linhas(e.anotacoes);
      if (notas.length) setup.anotacoes = notas;
    }
    // Duas tentativas: se alguém salvou ao mesmo tempo, lê de novo e grava por cima da versão nova.
    for (let tentativa = 0; tentativa < 2; tentativa++) {
      const { sha, dados } = await le(NOTAS);
      const texto = campo === "setup" ? [] : linhas(b.texto);
      dados[campo] = dados[campo] || {};
      if (campo === "setup") { if (Object.keys(setup).length) dados.setup[campeao] = setup; else delete dados.setup[campeao]; }
      else if (texto.length) dados[campo][campeao] = texto; else delete dados[campo][campeao];
      if (difCampo && b.dificuldade !== undefined) {
        dados[difCampo] = dados[difCampo] || {};
        if (dif) dados[difCampo][campeao] = dif; else delete dados[difCampo][campeao];
      }
      const conteudo = JSON.stringify(dados, null, 1) + "\n";
      const r = await github(NOTAS, {
        method: "PUT",
        body: JSON.stringify({
          message: `Taric (editor): ${campo === "setup" ? "setup contra" : campo === "sinergia" ? "com" : "contra"} ${campeao}`,
          content: Buffer.from(conteudo, "utf8").toString("base64"), sha, branch: "main",
        }),
      });
      if (r.ok) return res.json({ ok: true, texto, dificuldade: dif, setup });
      if (r.status !== 409) throw new Error("GitHub " + r.status);
    }
    return res.status(409).json({ erro: "conflito, tente de novo" });
  } catch (e) {
    return res.status(502).json({ erro: String(e.message || e) });
  }
};
