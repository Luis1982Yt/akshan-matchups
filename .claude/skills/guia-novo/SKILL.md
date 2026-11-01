---
name: guia-novo
description: Passo a passo para transformar uma planilha (ou doc) de matchups de LoL num guia novo do BattleMatch, ou para atualizar/traduzir um guia existente. Usar SEMPRE que o pedido envolver campeão novo, planilha de matchups, fonte nova, tradução de guia ou script atualizar_<campeão>.py, mesmo que o dono não peça a skill.
---

# Guia novo no BattleMatch

Regras do projeto continuam valendo (CLAUDE.md): pt-BR simples, nunca editar `index.html` à mão, nunca mudar o texto
das notas, curadoria do que é sobre o autor, testar 390/1440 claro/escuro, commit + push na main ao terminar.
Guias de referência: `scripts/atualizar_garen.py` (CSV, uma linha por matchup, build em texto) e
`scripts/atualizar_akali.py` (planilha bloqueada, lida pelo navegador).

## 0. Antes de tudo
- Procurar aviso de direitos ("do not republish", "©", "don't copy"). Se houver: parar e perguntar ao dono.
  Autor pediu para não ser citado: `"autor": ""` e `"credito_minimo": true` no `guias.json` (caso do K'Sante).
- Anotar a data/patch da planilha. Se for velha (itens míticos, season ≤ 13, runa que saiu do jogo), avisar o dono.

## 1. Ler a planilha (do mais barato para o mais caro)
1. CSV de cada aba: `guia_comum.csv_aba(id, gid)` (endpoint gviz). Funciona até com o xlsx bloqueado. Não traz imagens nem cores.
2. xlsx: `https://docs.google.com/spreadsheets/d/<id>/export?format=xlsx` (traz imagens e cores; `planilha_xlsx.py`).
3. Bloqueada (401 nos dois): navegador, como em `scripts/akali_baixar.js` (tabela das 100 primeiras linhas no HTML
   cru da página `/edit`, linhas >100 pela resposta `streamrows`, cores por print).
- Descobrir os gids: abrir `/edit` no Playwright e clicar em cada `.docs-sheet-tab` (ver `/tmp`-scripts do Garen no histórico) ou procurar `gid=` no HTML.
- Imagem com runas/itens (print do autor): tirar print da aba no Playwright (viewport largo, 2600 px) e ler.
- Não ler o texto todo para "entender": olhar a estrutura (cabeçalho, 3-4 linhas, contagens com `collections.Counter`
  das colunas curtas) e só depois escrever o parser. O texto inteiro só é lido na tradução.

## 2. Script `scripts/atualizar_<campeão>.py`
- Importar de `scripts/guia_comum.py`: `Ddragon` (campeões pt_BR, itens com ids de Summoner's Rift, runas),
  `csv_aba`, `limpa`, `dificuldade_10`, `FEITICO`, `APELIDO_CAMPEAO`, `APELIDO_ITEM`, `gravar_guia`.
  Apelido novo de item/campeão: pôr em `guia_comum.py` (vale para todos).
- Formato da matchup (ver `src/guias/garen/matchups.json`): `nome, planilha, id, titulo, rota, dificuldade
  {overall 1-5, valor, texto}, tldr [frases curtas], feiticos [peças], feiticos_texto?, feiticos_ou?, runas [[linhas
  {rotulo Principal/Secundária/Fragmentos, pecas, nota?}]], imagens_runas, itens [{rotulo, linhas [{tipo item|nota|rotulo|sep, passos [[peças]], motivo?}]}], secoes [{titulo, blocos [{tipo p|lista, ...}]}]`.
- Campeão não reconhecido deve dar erro (KeyError), nunca chute.
- Item sem ícone: o script imprime a lista; resolver com apelido até a lista ficar vazia.
- Runa que saiu do jogo (Lenda: Tenacidade, Ímpeto Gradual...): o site SEMPRE mostra a que ficou no lugar (ícone e
  nome de hoje, com o nome antigo entre parênteses). Tabela `RUNA_SUBSTITUTA` no `src/template.html` (chave = nome
  da planilha só com letras minúsculas) e `SUBSTITUTA` no `scripts/importar_lol.py` (para o app). Runa nova removida:
  pôr nas duas. Conferir: ícone de runa do guia que não está no `runesReforged.json` atual = runa antiga.
- Quebra de linha dentro da célula: `limpa()` para exibir; para achar item, testar juntar com espaço e sem espaço.
- Páginas extras (`paginas.json`): só o que ensina a jogar. Bio, redes, coaching, doação, Discord pessoal, aviso de
  beta, agradecimentos ficam de fora (no script, ou em `curadoria.json` se for frase no meio de texto útil).
- Rodar até `N matchups, M páginas` sem itens faltando.

## 3. Integrar
- `src/guias.json`: entrada nova (copiar a do Garen). Gravar com `json.dumps(..., ensure_ascii=False, indent=2)`
  (indent 2! outro indent reformata o arquivo inteiro). Dificuldade 0-10: `"escala": 10`. Mais de uma rota: `"rotas"`.
- `src/template.html`: paleta `:root[data-guia="<id>"]` escuro e claro (copiar a do Garen e trocar as cores pela
  arte oficial); mostrar prévia ao dono. Título de seção novo em inglês: pôr em `TITULOS`.
- `scripts/og.py` (`ROSTO`), `scripts/baixar_sons.py` (`CHAVE`, id numérico do campeão) e rodar `python3 scripts/baixar_sons.py`.
- Workflow `.github/workflows/atualizar-planilha.yml`: só se a leitura funcionar sem navegador (CSV/xlsx).
- `python3 scripts/importar_lol.py` e `python3 scripts/build.py`.

## 4. Traduzir (a parte mais cara: não desperdiçar)
1. `python3 scripts/traducao_pt.py` (cria o arquivo e os nomes de itens/runas em PT).
2. `python3 scripts/traducao_pt.py --lotes /tmp/<id>/trad --guia <id>` → lotes `NN.json` de ~14 mil caracteres.
3. Para cada lote: imprimir (`for i,g,t in json.load(...)`) e escrever `NN_pt.json` = `{"<id>": "pt"}` com TODOS os ids
   daquele lote (o id pode ficar em qualquer `_pt` da pasta). Strings iguais (Mid, Top) mapeiam para si mesmas.
4. `python3 scripts/traducao_pt.py --importar /tmp/<id>/trad --guia <id> --faltando` até `0 sem tradução`.
   Sempre com `--guia`: sem ele o lote vale para todos os guias.
- Glossário: nomes oficiais do cliente pt_BR (Data Dragon `pt_BR/item.json`, `runesReforged.json`; runa que saiu do
  jogo: versão 13.24.1). Já usados: Ímpeto Gradual, Caça Suprema, Quebrapassos, Quebracascos, Lembrete Mortal,
  Dançarina Fantasma, Presa da Serpente, Sinal de Sterak, Couraça do Defunto, Rookern Lamúrico, Explocinturão Hextec,
  Pistola Laminar Hextec, Ápice da Tempestade, Manto Anula-Magia, Orbe do Oblívio, Bandana de Mercúrio,
  Incendiar, Fantasma, Exaustão, Purificar, Teleporte. Termos de jogo ficam como o brasileiro fala: matchup, wave,
  all-in, poke, kite, roam, split push, gank, farm, dodge, build, core.
- Primeira pessoa do autor vira neutro na tradução ("a planilha prefere", "já foi ganha contra..."). Não traduzir
  com "eu" falando pelo autor.
- Depois de importar, conferir que os outros guias não mudaram: `git status --short src/guias/` só com a pasta do guia.

## 5. Testar e subir
- Playwright em `file:///.../index.html#<id>/<inimigo>` com `localStorage` `lingua` (pt/en) e `tema` (claro/escuro),
  viewports 390x844 e 1440x900; `document.documentElement.scrollWidth` igual à largura; olhar o print.
- README.md (linha do guia e do script) e GUIAS_FUTUROS.md (fonte, data, pendências: modelo 3D só no PC do dono).
- `git pull --rebase`, `python3 scripts/build.py` de novo, commit, push na main.
