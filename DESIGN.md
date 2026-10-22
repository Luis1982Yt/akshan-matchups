---
name: Guias de Matchup
description: Notas de matchup de jogadores montadas como a seleção de campeões, um guia por campeão e uma paleta por guia; o Akshan é Sentinelas da Luz, o Mordekaiser é ferro com o verde do Reino da Morte.
colors:
  fundo: "#0c0b09"
  painel: "#15130f"
  painel-alto: "#1e1a13"
  linha: "rgba(214, 178, 98, .26)"
  linha-forte: "rgba(214, 178, 98, .55)"
  acento: "#d6b262"
  acento-vivo: "#f2d488"
  destaque: "#ffd96b"
  texto: "#e9e1cd"
  texto-baixo: "#a99f88"
  tinta-botao: "#17130a"
  luz: "rgba(255, 228, 150, .16)"
  sobre-arte: "#ffe6a3"
  destaque-arte: "#ffd96b"
  botao-1: "#ffe7a1"
  botao-2: "#e2b24a"
  brilho: "rgba(255, 240, 200, .55)"
  brilho-2: "rgba(255, 210, 110, .18)"
  claro-fundo: "#f6f0e1"
  claro-painel: "#fffcf4"
  claro-painel-alto: "#efe5cd"
  claro-linha: "rgba(150, 112, 30, .28)"
  claro-linha-forte: "rgba(150, 112, 30, .6)"
  claro-acento: "#8a6416"
  claro-acento-vivo: "#6f4e0c"
  claro-destaque: "#e3b23c"
  claro-texto: "#2a2316"
  claro-texto-baixo: "#66593f"
  claro-tinta-botao: "#1d1608"
  claro-luz: "rgba(227, 178, 60, .18)"
  morde-fundo: "#0a0d0c"
  morde-painel: "#121715"
  morde-painel-alto: "#19201c"
  morde-linha: "rgba(110, 214, 156, .22)"
  morde-linha-forte: "rgba(110, 214, 156, .48)"
  morde-acento: "#63c98f"
  morde-acento-vivo: "#97ecbb"
  morde-destaque: "#5be39a"
  morde-texto: "#dde7e1"
  morde-texto-baixo: "#92a39a"
  morde-tinta-botao: "#05110a"
  morde-luz: "rgba(80, 220, 140, .12)"
  morde-sobre-arte: "#c8ffdf"
  morde-destaque-arte: "#6cf0a8"
  morde-botao-1: "#b5f7cf"
  morde-botao-2: "#3fbd78"
  morde-brilho: "rgba(200, 255, 225, .5)"
  morde-brilho-2: "rgba(80, 220, 140, .18)"
  morde-claro-fundo: "#edf2ee"
  morde-claro-painel: "#fbfdfb"
  morde-claro-painel-alto: "#dde7e0"
  morde-claro-linha: "rgba(25, 110, 65, .26)"
  morde-claro-linha-forte: "rgba(25, 110, 65, .56)"
  morde-claro-acento: "#1d7448"
  morde-claro-acento-vivo: "#135a37"
  morde-claro-destaque: "#2fa865"
  morde-claro-texto: "#17201b"
  morde-claro-texto-baixo: "#4c5d53"
  morde-claro-tinta-botao: "#04120a"
  morde-claro-luz: "rgba(47, 168, 101, .14)"
  branco-arte: "#f6f3ea"
  tinta-arte: "#111111"
typography:
  display:
    fontFamily: "Cinzel, Times New Roman, serif"
    fontSize: "clamp(26px, 2.6vw, 34px)"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "0.02em"
  headline:
    fontFamily: "Cinzel, Times New Roman, serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.06em"
  title:
    fontFamily: "Cinzel, Times New Roman, serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.14em"
  secao:
    fontFamily: "Cinzel, Times New Roman, serif"
    fontSize: "21px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "0.04em"
  marca:
    fontFamily: "Cinzel, Times New Roman, serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "0.04em"
  button:
    fontFamily: "Cinzel, Times New Roman, serif"
    fontSize: "19px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.1em"
  body:
    fontFamily: "Hanken Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  body-nota:
    fontFamily: "Hanken Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "17.5px"
    fontWeight: 400
    lineHeight: 1.65
  body-secao:
    fontFamily: "Hanken Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Hanken Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    letterSpacing: "0.14em"
  selo:
    fontFamily: "Cinzel, Times New Roman, serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "0.12em"
rounded:
  pip: "2px"
  selo: "4px"
  icone: "6px"
  campo: "8px"
  card: "10px"
  painel: "12px"
  pilula: "999px"
  circulo: "50%"
spacing:
  borda: "max(16px, env(safe-area-inset-left, 0px))"
  barra: "64px"
  gap-palco: "20px"
  gap-carga: "16px 24px"
  gap-setup-completo: "20px 36px"
  painel: "18px 22px"
  nota: "16px 18px"
  resumo: "16px 20px"
components:
  botao-travar:
    backgroundColor: "{colors.botao-2}"
    textColor: "{colors.tinta-arte}"
    typography: "{typography.button}"
    rounded: "{rounded.card}"
    padding: "8px 16px"
    height: "56px"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.texto}"
    rounded: "{rounded.pilula}"
    padding: "0 14px"
    height: "44px"
  chip-ativo:
    backgroundColor: "{colors.destaque}"
    textColor: "{colors.tinta-botao}"
    rounded: "{rounded.pilula}"
  busca:
    backgroundColor: "{colors.fundo}"
    textColor: "{colors.texto}"
    rounded: "{rounded.campo}"
    padding: "0 14px"
    height: "46px"
  card-campeao:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.sobre-arte}"
    rounded: "{rounded.card}"
  painel:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.painel}"
    padding: "18px 22px"
  selo-voce:
    backgroundColor: "{colors.destaque-arte}"
    textColor: "{colors.tinta-arte}"
    typography: "{typography.selo}"
    rounded: "{rounded.selo}"
    padding: "3px 10px"
  selo-inimigo:
    backgroundColor: "{colors.branco-arte}"
    textColor: "{colors.tinta-arte}"
    typography: "{typography.selo}"
    rounded: "{rounded.selo}"
    padding: "3px 10px"
  botao-navega:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.campo}"
    padding: "0 14px"
    height: "44px"
  botao-tema:
    backgroundColor: "transparent"
    textColor: "{colors.acento-vivo}"
    rounded: "{rounded.circulo}"
    size: "44px"
  trocar-guia:
    backgroundColor: "transparent"
    textColor: "{colors.acento-vivo}"
    typography: "{typography.marca}"
    rounded: "{rounded.pilula}"
    padding: "4px 12px 4px 4px"
    height: "48px"
  trocar-guia-aberto:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.acento-vivo}"
    rounded: "{rounded.pilula}"
  menu-guias:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.painel}"
    padding: "8px"
    width: "min(340px, calc(100vw - 32px))"
  menu-guias-item:
    backgroundColor: "transparent"
    textColor: "{colors.texto}"
    rounded: "{rounded.campo}"
    padding: "8px 10px"
    height: "60px"
  menu-guias-item-atual:
    backgroundColor: "{colors.painel-alto}"
    textColor: "{colors.texto}"
    rounded: "{rounded.campo}"
  resumo:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.card}"
    padding: "16px 20px"
  pip:
    backgroundColor: "{colors.painel-alto}"
    rounded: "{rounded.pip}"
    size: "10px"
  pip-ligado:
    backgroundColor: "{colors.destaque}"
    rounded: "{rounded.pip}"
    size: "10px"
---

# Design System: Guias de Matchup

## Overview

**Creative North Star: "A Seleção das Sentinelas"**

A página é a tela de seleção de campeões vestida com as cores das Sentinelas da Luz, a facção do Akshan. De um lado fica você (a arte em pé do Akshan, com selo amarelo), do outro o inimigo (selo branco), e no meio um painel com a mira da Punição, o R do Akshan, em volta da lista de campeões. O botão dourado de travar o pick fecha a escolha e leva ao setup e aos lembretes.

O material é preto quente com ouro, amarelo e branco no tema escuro, que é o padrão; no tema claro vira marfim com ouro escuro. A profundidade vem de molduras finas douradas, painéis em degraus de tom e uma luz dourada difusa que desce do topo da tela. A densidade é de consulta: tudo o que se lê na seleção de campeões cabe na primeira dobra do celular, e os lembretes embaixo têm ritmo de leitura calma.

A geometria vem do jogo: losangos, círculos e setas apontando para dentro, tirados da mira da Punição no vídeo oficial da habilidade. Não há raios de sol saindo do centro, e o verde do guia de referência não entra na paleta do Akshan.

O site agora é multi-guia. A mesma tela de seleção serve a cada guia (hoje Akshan, das notas do Peteruso, e Mordekaiser, das notas do Meowdekaiser); o que muda de um para outro é a paleta, alguns marcadores e o formato do setup e das notas. A seleção das Sentinelas é a expressão do Akshan; o Mordekaiser veste a mesma estrutura de ferro escuro com o verde do Reino da Morte. A troca de guia mora no topo e o site abre no último guia usado.

**Key Characteristics:**
- Três colunas no desktop (Você | mira com a lista | Inimigo e Travar), anel no topo no celular.
- Dois temas com os mesmos nomes de token; o escuro mora em `:root`, o claro em `:root[data-tema="claro"]`.
- Uma paleta por guia com os mesmos nomes de token, em `:root[data-guia="<id>"]` e `:root[data-guia="<id>"][data-tema="claro"]`.
- Cinzel em caixa-alta espaçada para títulos e rótulos de cerimônia; Hanken Grotesk para tudo o que se lê.
- A mira da Punição como assinatura do Akshan: losango, círculo inscrito e setas laterais para dentro. O losango pequeno é da casa toda.
- Movimento só em dois momentos: a mira travando no alvo (Akshan) e o "Travar o pick" (todos os guias).

## Colors

Cada guia tem um escuro de fundo com um acento metálico e um destaque vivo; o destaque é reservado para o que é seu ou está ativo, e o branco fica para o inimigo. No Akshan: preto quente, ouro e amarelo. No Mordekaiser: ferro esverdeado, verde metálico e o verde aceso do Reino da Morte.

Os nomes abaixo são os tokens do CSS (`--acento`, `--destaque`...). No frontmatter, o prefixo `claro-` marca o valor do tema claro, `morde-` o do guia do Mordekaiser e `morde-claro-` o do Mordekaiser no claro; os componentes nunca usam os prefixos, só o nome do token.

### Primary
- **Ouro Sentinela** (`acento`, antes `--ouro`): molduras da mira, setas entre os passos da build, ícones de busca e soquetes vazios, contagem da busca, chevron e anel do retrato no botão de troca, barra de rolagem da lista. No claro vira o ouro escuro de `claro-acento`. No Mordekaiser é o **Verde de Ferro** (`morde-acento`).
- **Ouro Aceso** (`acento-vivo`, antes `--ouro-vivo`): títulos em Cinzel, nome do guia no topo, condições da build, foco de teclado, borda em hover, links, ícone do botão de tema. No claro vira `claro-acento-vivo`, mais escuro ainda, para manter contraste de título sobre marfim. No Mordekaiser é o **Verde Pálido** (`morde-acento-vivo`).

### Secondary
- **Amarelo da Luz** (`destaque`, antes `--amarelo`): o chip ativo, a bolinha "no guia", os números dos lembretes, o sublinhado dos termos-chave, os marcadores em losango das seções, os pips ligados, a marca do campeão escolhido na lista e a seleção de texto. No Mordekaiser é o **Verde do Reino da Morte** (`morde-destaque`).

### Tertiary (sobre a arte)
Tokens que ficam sobre a arte do campeão ou no botão de travar. Mudam por guia, mas não por tema: o claro de cada guia herda os do escuro.
- **Nome na Arte** (`sobre-arte`): o nome do campeão nos cards e nas artes do Travar o pick.
- **Destaque na Arte** (`destaque-arte`): o selo "Você", a marca "Já está no guia" e os pips ligados dentro do card.
- **Metal do Botão** (gradiente de `botao-1` a `botao-2`): só o Travar o pick; o `botao-2` também emoldura as artes no overlay.
- **Clarão** (`brilho` para `brilho-2`): o clarão radial no centro do Travar o pick.
- **Branco da Arte** (`branco-arte`) e **Tinta da Arte** (`tinta-arte`): fixos em todos os guias e temas; o selo "Inimigo", o texto dos selos e do Travar o pick.

### Neutral
- **Preto Quente** (`fundo`): fundo da página, do campo de busca e da barra (90% com blur). No claro, `claro-fundo` (marfim); no Mordekaiser, `morde-fundo` (ferro).
- **Painel** (`painel`) e **Painel Alto** (`painel-alto`): superfícies dos painéis, cards, notas e do menu de guias; o alto entra atrás dos ícones, nos pips apagados, no item aberto do menu e no hover do botão de tema.
- **Linha** (`linha`) e **Linha Forte** (`linha-forte`): metal translúcido para molduras; a fraca contorna painéis grandes, separa linhas da tabela de cooldowns e passos da build; a forte contorna cards, chips, campos, ícones e o menu.
- **Texto** (`texto`) e **Texto Baixo** (`texto-baixo`): corpo e texto de apoio (rótulos de slot, títulos dos campeões, subtítulo do guia, motivos da build, valores da tabela, rodapé).
- **Tinta do Botão** (`tinta-botao`): texto escuro sobre o destaque.
- **Luz** (`luz`): a luz radial que desce do topo, numa camada fixa atrás de tudo, na cor do guia.

### Named Rules
**A Regra dos Dois Temas.** Todo componente usa os tokens por nome; o tema claro só troca os valores em `:root[data-tema="claro"]`. Cor fixa só é permitida sobre a arte do campeão (nomes, selos, escurecimento do card, o número de dificuldade sobre o ícone, o overlay do Travar o pick), onde o fundo é a imagem e não o tema.

**A Regra da Paleta por Guia.** Um guia novo entra redefinindo os mesmos tokens em `:root[data-guia="<id>"]` (base e sobre a arte) e `:root[data-guia="<id>"][data-tema="claro"]` (só os de base). Nenhum componente pergunta qual é o guia para escolher cor; só os marcadores próprios de um campeão (a mira da Punição) dependem de `data-guia`.

**A Regra do Destaque é Seu.** O destaque (amarelo no Akshan, verde no Mordekaiser) marca o que é seu, o que está ativo ou o que importa no texto: selo Você, filtro ligado, campeão escolhido, número do lembrete, termo-chave, pip ligado. Não vira cor de decoração.

## Typography

**Display Font:** Cinzel (com Times New Roman, serif)
**Body Font:** Hanken Grotesk (com system-ui, Segoe UI, sans-serif)

**Character:** Cinzel traz as capitulares gravadas da cerimônia de seleção; Hanken Grotesk é limpa e legível para as notas na voz original da planilha. As duas fontes vão embutidas no `index.html` como data: URI.

### Hierarchy
- **Display** (800, clamp(26px, 2.6vw, 34px), 1.05; 22px no celular): o nome do campeão sobre a arte, em caixa versalete do Cinzel. Nomes longos (mais de 9 letras) descem para clamp(20px, 2vw, 27px), 17px no celular.
- **Headline** (700, 28px, 1.2, 0.06em; 23px no celular): "Lembrete" (Akshan), "Como jogar" (Mordekaiser) e "Como ler a planilha".
- **Title** (700, 22px, 0.14em, caixa-alta; 18px no celular): "Escolhe o inimigo", ladeado por dois losangos. O "Seu setup pro confronto" usa o mesmo desenho a 16px.
- **Seção** (700, 21px, 1.25, 0.04em): os títulos das seções do formato completo, em português, em `acento-vivo`.
- **Marca** (700, 20px, 0.04em; 18px abaixo de 520px): o nome do guia no botão de troca. Os itens do menu usam o mesmo desenho a 17px.
- **Botão** (800, 19px, 0.1em, caixa-alta): Travar o pick; a linha "contra X" embaixo vai em Hanken 600 13px.
- **Body** (400, 16px, 1.6): texto geral. Os lembretes sobem para 17.5px/1.65 e as seções do formato completo para 17px/1.7 (ambos 16.5px no celular); a coluna de notas fica em 820px.
- **Label** (600, 12px, 0.14em, caixa-alta, Hanken): rótulos Runa, Secundária, Feitiço, Bota, Build e os títulos dos blocos Runas, Itens e Dificuldade. O "Resumo" usa o mesmo desenho a 700 13px.
- **Selo** (Cinzel 700, 12px, 0.12em, caixa-alta): "Você" e "Inimigo" nos cards; a tag "rush" usa o mesmo desenho a 11px.

### Named Rules
**A Regra da Cerimônia.** Cinzel é para nomes, títulos, selos e o botão de travar. O que se lê de verdade (notas, rótulos de slot, chips, busca, tabela) é Hanken Grotesk.

**A Regra da Voz Original.** A interface fala português; o texto do autor fica na língua da planilha. No formato completo, o bloco de notas, a build e as condições vão marcados com `lang="en"`, e os títulos das seções são traduzidos e marcados de volta com `lang="pt-BR"`, em Cinzel sobre o corpo em inglês.

## Layout

O palco é uma grade de 1320px no máximo, com margem lateral `borda` (16px ou a área segura). No desktop são três colunas (280px | flexível | 280px): o card Você ocupa duas linhas à esquerda, a mira fica no meio, o card Inimigo e o botão de travar ficam à direita, e o setup atravessa as três colunas embaixo. Abaixo de 1100px as colunas laterais caem para 220px e o setup simples passa para três colunas.

O setup tem dois formatos. O simples (Akshan) é uma fila de cinco slots. O completo (Mordekaiser) são três blocos lado a lado, Runas | Itens | Dificuldade (1fr | 1.7fr | 0.8fr, espaço de 20px por 36px); abaixo de 1100px a Dificuldade desce para a linha inteira, e abaixo de 900px os três empilham.

Abaixo de 900px a grade vira duas colunas: a mira no topo, os dois cards lado a lado, o botão de travar em largura total e o setup em duas colunas (a build ocupa a linha inteira). Os filtros viram uma faixa com rolagem horizontal dentro do painel, sem a página rolar para o lado. A lista de campeões fica em quatro colunas.

A barra é fixa no topo (64px, 60px no celular) com blur e leva só o botão de troca de guia à esquerda e o botão de tema à direita. Os lembretes, as seções e o dicionário ficam numa coluna de 820px abaixo do palco. Ritmo de espaço: 20px entre blocos do palco, 14px entre lembretes, 34px entre seções, 32px depois do Resumo, 16px a 24px dentro do setup simples, 64px antes do dicionário. Todo alvo de toque tem pelo menos 44px.

## Elevation & Depth

Híbrido: a maior parte da profundidade é tonal (fundo, painel, painel alto) com molduras finas na cor do acento, e só os cards de campeão, o menu de guias e o botão de travar ganham sombra. A luz radial do topo dá a sensação de cena iluminada.

### Shadow Vocabulary
- **Sombra** (token `--sombra`: `0 10px 30px rgba(0, 0, 0, .45)` no Akshan escuro, `rgba(90, 64, 10, .14)` no claro; `rgba(0, 0, 0, .5)` no Mordekaiser escuro, `rgba(10, 60, 30, .14)` no claro): cards Você e Inimigo e o menu de guias.
- **Relevo do botão** (`box-shadow: inset 0 1px 0 rgba(255, 255, 255, .6), 0 6px 18px rgba(0, 0, 0, .35)`): só o Travar o pick, com o brilho de borda em cima.
- **Brilho da mira** (`filter: drop-shadow(0 0 4px rgba(255, 214, 120, .75)) drop-shadow(0 1px 3px rgba(0, 0, 0, .6))`): o losango que trava no card do inimigo, só no Akshan.
- **Anel do retrato** (`box-shadow: 0 0 0 2px var(--acento)`): o retrato do campeão do guia no botão de troca.
- **Anel duplo do escolhido** (`box-shadow: 0 0 0 2px var(--painel), 0 0 0 4px var(--acento)`, mais a borda de 2px em `destaque`): o campeão escolhido na lista em todo guia que não é o Akshan.

### Named Rules
**A Regra da Luz de Cima.** A luz vem do topo da tela, numa camada fixa atrás de tudo. Não há brilhos radiais saindo do centro dos componentes, exceto o clarão do Travar o pick.

## Shapes

Cantos discretos e uma geometria de mira. Pips de dificuldade usam 2px, selos, tags e o número de dificuldade 4px, ícones de campeão e de item 6px, campos, botões de navegação e itens do menu 8px, cards, lembretes, Resumo e botão de travar 10px, painéis e menu de guias 12px. Chips e o botão de troca de guia são pílulas; botão de tema, runas, números dos lembretes, retratos e avatares são círculos.

A forma assinatura do Akshan é a da Punição: losango com círculo inscrito e setas triangulares laterais apontando para dentro. Ela aparece em três escalas: a mira grande em volta da lista (círculo duplo, um a 1.5px e outro fino a 1px com 45% de opacidade, mais as setas), a mira no card do inimigo (losango de 3.5px, círculo de 1px e setas) e o losango pequeno girado 45° em volta do campeão escolhido. Nos outros guias a mira fica só com o círculo duplo, sem setas e sem alvo no card.

O losango pequeno é da casa toda: os dois losangos de 14px ao lado de "Escolhe o inimigo" e o marcador de 7px girado 45° nas listas das seções aparecem em todos os guias.

## Components

### Botão Travar o pick
O fecho metálico da escolha.
- **Shape:** cantos de 10px, altura mínima de 56px, largura total da coluna.
- **Cor:** gradiente vertical de `botao-1` para `botao-2` (ouro no Akshan, verde no Mordekaiser), texto em `tinta-arte`; igual nos dois temas.
- **Hover / Active:** brilho +6% no hover, desce 1px ao apertar.
- **Conteúdo:** "Travar o pick" em Cinzel caixa-alta e "contra X" em Hanken embaixo.

### Chips de filtro
- **Style:** pílula de 44px, fundo transparente, borda `linha-forte`, Hanken 600 14px, com ícone do feitiço ou runa a 20px quando houver.
- **State:** ligado vira o destaque cheio com tinta escura; hover acende a borda em `acento-vivo`.
- **Por guia:** cada formato traz seus filtros (Akshan: Só com guia, Ignite, TP, Exhaust, Electro; Mordekaiser: Fácil, Médio, Difícil).

### Cards de campeão
- **Corner Style:** 10px, proporção da arte de carregamento (308 / 560).
- **Background:** a arte cobre o card; um escurecimento de baixo para cima segura o nome.
- **Shadow Strategy:** sombra (ver Elevation).
- **Border:** 1px `linha-forte`.
- **Conteúdo:** selo no canto (Você à esquerda em `destaque-arte`, Inimigo à direita em `branco-arte`), nome em Cinzel, título do campeão e, no inimigo, a linha do guia: no Akshan a marca "no guia" com bolinha; no formato completo cinco pips em `destaque-arte` e "Dificuldade N/5".

### Busca
- **Style:** 46px, fundo `fundo`, borda `linha-forte`, cantos de 8px, lupa em SVG e a contagem "47/47" em `acento` com números tabulares.
- **Focus:** a borda e o ícone acendem em `acento-vivo`.

### Painéis
Mira, setup, Resumo e cada lembrete são painéis com fundo `painel` e borda `linha`; os lembretes levam o número num círculo de 30px no destaque e os termos-chave sublinhados no destaque (2px, afastado 5px).

### Navegação
- **Troca de guia:** pílula de 48px com o retrato do campeão do guia (38px, anel de 2px em `acento`), o nome em Cinzel `acento-vivo` e "notas do <autor>" (com a rota antes, quando houver) em texto baixo 13px, mais um chevron em `acento` que gira 180° ao abrir (0.2s). Em repouso não tem borda nem fundo; no hover ou aberto ganha `painel` e borda `linha-forte`.
- **Menu de guias:** painel de até 340px, cantos de 12px, borda `linha-forte` e sombra, com o título "Guias de matchup" em rótulo, um item de 60px por guia (retrato de 42px, nome em Cinzel 17px, autor e número de matchups) e a nota "O site sempre abre no último guia que você usou". O guia aberto fica em `painel-alto` com "Aberto" em `acento-vivo`. O guia escolhido fica em `localStorage` na chave `guia`, e o endereço vira `#<guia>/<campeão>` (os links antigos `#<campeão>` abrem no Akshan).
- **Tema:** o botão redondo de 44px à direita (lua no escuro, sol no claro), que grava a escolha em `localStorage` com a chave `tema`.
- **Anterior / próximo:** botões de 44px com ícone do campeão e seta; abaixo de 520px fica só o ícone.

### Campeão na lista
Ícone de 52px ou mais com borda `linha-forte` e cantos de 6px. O escolhido ganha borda de 2px no destaque: no Akshan com o losango pequeno girado em volta, nos outros guias com o anel duplo. No Akshan, os campeões "no guia" levam uma bolinha no destaque no canto de cima; no formato completo, cada rosto leva o número de dificuldade num selinho escuro de 17px no canto de baixo (Hanken 700 11px).

### Setup completo
Três blocos com o título em rótulo:
- **Runas:** linhas rotuladas com ícones redondos de 32px; variações separadas por "ou" em itálico; os fragmentos em texto corrido separados por "·".
- **Itens:** grupos com a condição em `acento-vivo` 700 15px, e cada build como uma fila de ícones de 32px com setas em `acento` entre os passos e "ou" entre alternativas; o motivo vai embaixo em texto baixo 14px, e separadores são uma linha de 1px.
- **Dificuldade:** Early, Mid, Late e Geral, cada um com cinco pips de 10px (cantos de 2px; apagados em `painel-alto` com contorno `linha-forte`, ligados no destaque) e a nota "N/5" em números tabulares.

### Notas do formato completo
- **Resumo:** painel de cantos de 10px e padding de 16px por 20px, com "Resumo" em rótulo 700 13px e o TL;DR em lista.
- **Seções:** título em português em Cinzel `acento-vivo` sobre o texto original em inglês a 17px/1.7; listas com marcador em losango de 7px no destaque.
- **Cooldowns:** tabela de até 560px, Hanken 15px, linhas separadas por `linha`, habilidade em texto 700 e valores em texto baixo com números tabulares.

### Mira da Punição (assinatura do Akshan)
Desenhada a partir do vídeo oficial do R do Akshan. Em volta da lista: círculo duplo e duas setas laterais apontando para o centro. No card do inimigo: losango dourado com círculo inscrito e setas laterais para dentro, com brilho; a cada troca de inimigo ele refaz a animação `trava-alvo` (0.5s, `cubic-bezier(.16, 1, .3, 1)`, entra de 135% de escala e opacidade zero). Só existe com `data-guia="akshan"`; nos outros guias ficam apenas os dois círculos em volta da lista.

### Travar o pick (animação)
Ao travar, um overlay escuro abre com as duas artes de carregamento (molduras de 2px em `botao-2`) deslizando dos lados até o meio (0.7s), um clarão radial de `brilho` para `brilho-2` no centro e "VS" em Cinzel (0.9s, com 0.25s de atraso). Fecha sozinho em 1.5s, ou com clique, Enter ou Esc, e a página desce até o setup. Com "reduzir movimento", a animação é pulada e só a descida acontece, sem rolagem suave.

## Do's and Don'ts

### Do:
- **Do** usar os tokens pelo nome (`--acento`, `--destaque`, `--painel`, `--linha-forte`...) para que o tema claro e a paleta de cada guia funcionem sozinhos.
- **Do** criar um guia novo redefinindo os mesmos tokens em `:root[data-guia="<id>"]` e na variante `[data-tema="claro"]`, incluindo os de sobre a arte e do botão.
- **Do** reservar o destaque para o que é seu ou está ativo: selo Você, filtro ligado, campeão escolhido, número do lembrete, termo-chave, pip ligado.
- **Do** desenhar marcadores novos com a geometria da casa (losango, círculo, setas apontando para dentro); a mira completa da Punição fica só no Akshan.
- **Do** manter alvos de toque de pelo menos 44px e o foco em contorno `acento-vivo` de 2px afastado 3px.
- **Do** respeitar "reduzir movimento" em qualquer animação nova, como a mira, o Travar o pick e o chevron da troca de guia já fazem.

### Don't:
- **Don't** desenhar raios de sol saindo do centro da mira ou dos cards.
- **Don't** trazer o verde do guia de referência para a paleta do Akshan; o verde do Mordekaiser é dele, do Reino da Morte.
- **Don't** usar cor fixa fora da arte do campeão; fora dela, tudo passa pelos tokens dos temas e dos guias.
- **Don't** pôr a mira da Punição (alvo no card, setas, losango em volta do escolhido) em guia que não seja o do Akshan.
- **Don't** usar Cinzel em parágrafos, rótulos de slot, chips ou tabelas.
- **Don't** deixar a página rolar para o lado; faixas largas (como os filtros no celular) rolam dentro do próprio painel.
