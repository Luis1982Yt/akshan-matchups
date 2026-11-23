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
  if (!["dicas", "sinergia"].includes(campo)) return res.status(400).json({ erro: "campo inválido" });
  const difCampo = campo === "dicas" && b.tipo === "adc" ? "dificuldade_adc" : campo === "dicas" ? "dificuldade" : null;
  const dif = b.dificuldade === null || b.dificuldade === "" || b.dificuldade === undefined ? null : Number(b.dificuldade);
  if (dif !== null && !(Number.isInteger(dif) && dif >= 1 && dif <= 5)) return res.status(400).json({ erro: "dificuldade de 1 a 5" });

  try {
    const ids = new Set((await le(MATCHUPS)).dados.matchups.map(m => m.id));
    if (!ids.has(campeao)) return res.status(400).json({ erro: "campeão desconhecido" });
    // Duas tentativas: se alguém salvou ao mesmo tempo, lê de novo e grava por cima da versão nova.
    for (let tentativa = 0; tentativa < 2; tentativa++) {
      const { sha, dados } = await le(NOTAS);
      const texto = linhas(b.texto);
      dados[campo] = dados[campo] || {};
      if (texto.length) dados[campo][campeao] = texto; else delete dados[campo][campeao];
      if (difCampo && b.dificuldade !== undefined) {
        dados[difCampo] = dados[difCampo] || {};
        if (dif) dados[difCampo][campeao] = dif; else delete dados[difCampo][campeao];
      }
      const conteudo = JSON.stringify(dados, null, 1) + "\n";
      const r = await github(NOTAS, {
        method: "PUT",
        body: JSON.stringify({
          message: `Taric (editor): ${campo === "sinergia" ? "com" : "contra"} ${campeao}`,
          content: Buffer.from(conteudo, "utf8").toString("base64"), sha, branch: "main",
        }),
      });
      if (r.ok) return res.json({ ok: true, texto, dificuldade: dif });
      if (r.status !== 409) throw new Error("GitHub " + r.status);
    }
    return res.status(409).json({ erro: "conflito, tente de novo" });
  } catch (e) {
    return res.status(502).json({ erro: String(e.message || e) });
  }
};
