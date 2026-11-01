// Lê a planilha de Akali do SupremeG0at como um navegador (o download e a cópia estão bloqueados pelo autor).
// Uso: node scripts/akali_baixar.js <pasta>   e depois   python scripts/atualizar_akali.py --de <pasta>
// Precisa do Playwright com Chromium. Grava na pasta:
//   aba1.html / aba2.html  a página de cada aba (traz a tabela das primeiras 100 linhas, com texto e cores)
//   linhas_extras.txt     as linhas que o Google carrega ao rolar (as matchups de top depois da linha 100)
//   cores_extras.json     a cor da célula do campeão dessas linhas, lida do print da coluna A
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ID = '1QSmbqRpG-caL8flzDFVQw546CSp5VBvLB96ymQd2uzQ';
const ABA2 = '854920634';

(async () => {
  const pasta = process.argv[2];
  if (!pasta) throw new Error('uso: node scripts/akali_baixar.js <pasta>');
  fs.mkdirSync(pasta, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 3800 } });
  let extras = '';
  p.on('response', async r => {
    try { if (r.url().includes('/streamrows')) { const t = await r.text(); if (t.length > extras.length) extras = t; } } catch (e) {}
  });
  for (const [nome, url] of [['aba1.html', `https://docs.google.com/spreadsheets/d/${ID}/edit`], ['aba2.html', `https://docs.google.com/spreadsheets/d/${ID}/edit?gid=${ABA2}`]]) {
    // O HTML cru da resposta (não o da tela): é ele que traz a tabela com o texto e as cores.
    const r = await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    fs.writeFileSync(path.join(pasta, nome), await r.text());
  }
  // Abrir a planilha a partir da linha 100 faz o Google carregar o resto e mostra a coluna A com as cores.
  await p.goto(`https://docs.google.com/spreadsheets/d/${ID}/edit#gid=0&range=A100`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await p.waitForTimeout(9000);
  fs.writeFileSync(path.join(pasta, 'linhas_extras.txt'), extras);
  const png = await p.screenshot();
  fs.writeFileSync(path.join(pasta, 'coluna_a.png'), png);
  await b.close();
  console.log('ok: rode python scripts/atualizar_akali.py --de ' + pasta);
})();
