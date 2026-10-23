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
    fontSize: "clamp(24px, 2.3vw, 32px)"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "0.02em"
  headline:
    fontFamily: "Cinzel, Times New Roman, serif"
    fontSize: "23px"
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
    fontSize: "21px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.04em"
  body:
    fontFamily: "Hanken Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  body-nota:
    fontFamily: "Hanken Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
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
  coluna-lista: "440px"
  gap-palco: "24px"
  gap-detalhe: "16px"
  gap-duelo: "10px"
  gap-carga: "16px 24px"
  gap-setup-completo: "20px 32px"
  anel: "18px 20px 22px"
  painel: "16px 20px"
  nota: "12px 16px"
  resumo: "16px 20px"
components:
  botao-travar:
    backgroundColor: "{colors.botao-2}"
    textColor: "{colors.tinta-arte}"
    typography: "{typography.button}"
    rounded: "{rounded.circulo}"
    size: "66px"
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
    height: "240px"
  painel:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.painel}"
    padding: "16px 20px"
  painel-lista:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.painel}"
    padding: "18px 20px 22px"
    width: "440px"
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
  botao-som:
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
  lembrete:
    backgroundColor: "{colors.painel}"
    textColor: "{colors.texto}"
    typography: "{typography.body-nota}"
    rounded: "{rounded.card}"
    padding: "12px 16px"
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

A página é a tela de seleção de campeões vestida com as cores das Sentinelas da Luz, a facção do Akshan. À esquerda fica o painel com a mira da Punição, o R do Akshan, em volta da lista de campeões; à direita, o duelo: você (a arte do Akshan, com selo amarelo) e o inimigo (selo branco) lado a lado, com o círculo dourado "VS" entre os dois. Tocar no VS trava o pick, e logo abaixo estão o setup e os lembretes.

O material é preto quente com ouro, amarelo e branco no tema escuro, que é o padrão; no tema claro vira marfim com ouro escuro. A profundidade vem de molduras finas douradas, painéis em degraus de tom e uma luz dourada difusa que desce do topo da tela. A densidade é de consulta: no desktop o matchup inteiro (duelo, setup, lembretes e rodapé) cabe na tela sem rolar no Akshan a 1440×900, e no celular a lista vira uma faixa de rostos para o duelo subir para a primeira dobra. O som acompanha a mão: cliques e falas do cliente do LoL, só quando o leitor age, e com um botão para calar.

A geometria vem do jogo: losangos, círculos e setas apontando para dentro, tirados da mira da Punição no vídeo oficial da habilidade. Não há raios de sol saindo do centro, e o verde do guia de referência não entra na paleta do Akshan.

O site é multi-guia. A mesma tela de seleção serve a cada guia (hoje Akshan, das notas do Peteruso, e Mordekaiser, das notas do Meowdekaiser); o que muda de um para outro é a paleta, alguns marcadores e o formato do setup e das notas. A seleção das Sentinelas é a expressão do Akshan; o Mordekaiser veste a mesma estrutura de ferro escuro com o verde do Reino da Morte. A troca de guia mora no topo, o site abre no último guia usado, e o crédito do autor fica no rodapé.

**Key Characteristics:**
- Duas colunas no desktop: a lista fixa de 440px à esquerda e o detalhe (duelo, setup, notas, rodapé) à direita; uma coluna no celular, com a lista em faixa horizontal.
- Duelo em paisagem: os dois cards lado a lado com a arte centralizada e o círculo VS de travar entre eles.
- Dois temas com os mesmos nomes de token; o escuro mora em `:root`, o claro em `:root[data-tema="claro"]`.
- Uma paleta por guia com os mesmos nomes de token, em `:root[data-guia="<id>"]` e `:root[data-guia="<id>"][data-tema="claro"]`.
- Cinzel em caixa-alta espaçada para títulos e rótulos de cerimônia; Hanken Grotesk para tudo o que se lê.
- A mira da Punição como assinatura do Akshan: losango, círculo inscrito e setas laterais para dentro. O losango pequeno é da casa toda.
- Movimento só em dois momentos: a mira travando no alvo (Akshan) e o travar do pick (todos os guias). Som só por ação do leitor, com o botão de som no topo.

## Colors

Cada guia tem um escuro de fundo com um acento metálico e um destaque vivo; o destaque é reservado para o que é seu ou está ativo, e o branco fica para o inimigo. No Akshan: preto quente, ouro e amarelo. No Mordekaiser: ferro esverdeado, verde metálico e o verde aceso do Reino da Morte.

Os nomes abaixo são os tokens do CSS (`--acento`, `--destaque`...). No frontmatter, o prefixo `claro-` marca o valor do tema claro, `morde-` o do guia do Mordekaiser e `morde-claro-` o do Mordekaiser no claro; os componentes nunca usam os prefixos, só o nome do token.

### Primary
- **Ouro Sentinela** (`acento`, antes `--ouro`): molduras da mira, setas entre os passos da build, ícones de busca e soquetes vazios, contagem da busca, losangos do título da lista, chevron e anel do retrato no botão de troca, barra de rolagem da lista. No claro vira o ouro escuro de `claro-acento`. No Mordekaiser é o **Verde de Ferro** (`morde-acento`).
- **Ouro Aceso** (`acento-vivo`, antes `--ouro-vivo`): títulos em Cinzel, nome do guia no topo, condições da build, foco de teclado, borda em hover, links, ícones dos botões de tema e de som. No claro vira `claro-acento-vivo`, mais escuro ainda, para manter contraste de título sobre marfim. No Mordekaiser é o **Verde Pálido** (`morde-acento-vivo`).

### Secondary
- **Amarelo da Luz** (`destaque`, antes `--amarelo`): o chip ativo, a bolinha "no guia", os números dos lembretes, o sublinhado dos termos-chave, os marcadores em losango das seções, os pips ligados, a marca do campeão escolhido na lista e a seleção de texto. No Mordekaiser é o **Verde do Reino da Morte** (`morde-destaque`).

### Tertiary (sobre a arte)
Tokens que ficam sobre a arte do campeão ou no botão de travar. Mudam por guia, mas não por tema: o claro de cada guia herda os do escuro.
- **Nome na Arte** (`sobre-arte`): o nome do campeão nos cards e nas artes do overlay de travar.
- **Destaque na Arte** (`destaque-arte`): o selo "Você", a marca "Já está no guia" e os pips ligados dentro do card.
- **Metal do Botão** (gradiente de `botao-1` a `botao-2`): só o círculo VS de travar; o `botao-2` também emoldura as artes no overlay.
- **Clarão** (`brilho` para `brilho-2`): o clarão radial no centro do overlay de travar.
- **Branco da Arte** (`branco-arte`) e **Tinta da Arte** (`tinta-arte`): fixos em todos os guias e temas; o selo "Inimigo", o texto dos selos e o "VS" do botão de travar.

### Neutral
- **Preto Quente** (`fundo`): fundo da página, do campo de busca, da barra (90% com blur) e a borda de 3px que recorta o círculo VS sobre os cards. No claro, `claro-fundo` (marfim); no Mordekaiser, `morde-fundo` (ferro).
- **Painel** (`painel`) e **Painel Alto** (`painel-alto`): superfícies da lista, do setup, dos cards, das notas e do menu de guias; o alto entra atrás dos ícones, nos pips apagados, no item aberto do menu e no hover dos botões de tema e de som.
- **Linha** (`linha`) e **Linha Forte** (`linha-forte`): metal translúcido para molduras; a fraca contorna painéis grandes, separa linhas da tabela de cooldowns, passos da build, a barra e as linhas do setup no celular; a forte contorna cards, chips, campos, ícones, botões redondos e o menu.
- **Texto** (`texto`) e **Texto Baixo** (`texto-baixo`): corpo e texto de apoio (rótulos de slot, títulos dos campeões, rota do guia, motivos da build, valores da tabela, "Tanto faz" e "Sem anotação", rodapé).
- **Tinta do Botão** (`tinta-botao`): texto escuro sobre o destaque.
- **Luz** (`luz`): a luz radial que desce do topo, numa camada fixa atrás de tudo, na cor do guia.

### Named Rules
**A Regra dos Dois Temas.** Todo componente usa os tokens por nome; o tema claro só troca os valores em `:root[data-tema="claro"]`. Cor fixa só é permitida sobre a arte do campeão (nomes, selos, escurecimento do card, o número de dificuldade sobre o ícone, o "VS" do botão de travar, o overlay de travar), onde o fundo é a imagem e não o tema.

**A Regra da Paleta por Guia.** Um guia novo entra redefinindo os mesmos tokens em `:root[data-guia="<id>"]` (base e sobre a arte) e `:root[data-guia="<id>"][data-tema="claro"]` (só os de base). Nenhum componente pergunta qual é o guia para escolher cor; só os marcadores próprios de um campeão (a mira da Punição) dependem de `data-guia`.

**A Regra do Destaque é Seu.** O destaque (amarelo no Akshan, verde no Mordekaiser) marca o que é seu, o que está ativo ou o que importa no texto: selo Você, filtro ligado, campeão escolhido, número do lembrete, termo-chave, pip ligado. Não vira cor de decoração.

## Typography

**Display Font:** Cinzel (com Times New Roman, serif)
**Body Font:** Hanken Grotesk (com system-ui, Segoe UI, sans-serif)

**Character:** Cinzel traz as capitulares gravadas da cerimônia de seleção; Hanken Grotesk é limpa e legível para as notas na voz original da planilha. As duas fontes vão embutidas no `index.html` como data: URI.

### Hierarchy
- **Display** (800, clamp(24px, 2.3vw, 32px), 1.05; 20px no celular): o nome do campeão sobre a arte, em caixa versalete do Cinzel. Nomes longos (mais de 9 letras) descem para clamp(19px, 1.8vw, 25px), 16px no celular.
- **Headline** (700, 23px, 1.2, 0.06em; 20px no celular): "Lembrete" (Akshan) e "Como jogar" (Mordekaiser), ao lado dos botões de anterior e próximo.
- **Title** (700, 22px, 0.14em, caixa-alta): "Escolhe o inimigo", ladeado por dois losangos; 17px (0.1em) abaixo de 1100px e 16px no celular. O "Seu setup pro confronto" usa o mesmo desenho a 16px.
- **Seção** (700, 21px, 1.25, 0.04em): os títulos das seções do formato completo, em português, em `acento-vivo`.
- **Marca** (700, 20px, 0.04em; 18px abaixo de 520px): o nome do guia no botão de troca, com a rota embaixo em Hanken 13px. Os itens do menu usam o mesmo desenho a 17px.
- **Botão** (800, 21px, 0.04em, caixa-alta): o "VS" do círculo de travar; 17px no celular.
- **Body** (400, 16px, 1.6): texto geral. Os lembretes sobem para 17px/1.6 (16px no celular) e as seções do formato completo para 17px/1.7 (16.5px no celular).
- **Label** (600, 12px, 0.14em, caixa-alta, Hanken): rótulos Runa, Secundária, Feitiço, Bota, Build e os títulos dos blocos Runas, Itens e Dificuldade. O "Resumo" usa o mesmo desenho a 700 13px.
- **Selo** (Cinzel 700, 12px, 0.12em, caixa-alta): "Você" e "Inimigo" nos cards; a tag "rush" usa o mesmo desenho a 11px.

### Named Rules
**A Regra da Cerimônia.** Cinzel é para nomes, títulos, selos e o VS de travar. O que se lê de verdade (notas, rótulos de slot, chips, busca, tabela, rodapé) é Hanken Grotesk.

**A Regra da Voz Original.** A interface fala português; o texto do autor fica na língua da planilha. No formato completo, o bloco de notas, a build e as condições vão marcados com `lang="en"`, e os títulos das seções são traduzidos e marcados de volta com `lang="pt-BR"`, em Cinzel sobre o corpo em inglês.

## Layout

O palco é uma grade de 1320px no máximo, com margem lateral `borda` (16px ou a área segura) e 24px entre as colunas. No desktop são duas colunas: o painel da lista, com 440px, fica fixo (sticky) à esquerda logo abaixo da barra, e a coluna de detalhe à direita empilha o duelo, o setup, as notas e o rodapé com 16px entre eles. O alvo de densidade é o Akshan a 1440×900: o matchup inteiro visível sem rolar. Abaixo de 1100px a lista cai para 340px (padding de 16px por 14px) e o setup simples passa para três colunas.

O duelo são os dois cards lado a lado (10px entre eles), em paisagem com 240px de altura, e o círculo VS centrado sobre a junção. Dentro da lista, a mira é um quadrado de até 400px com a grade de rostos (52px ou mais, 12px de espaço) rolando por dentro, com a borda de baixo esmaecendo. Os filtros ficam limitados a 360px de largura e centralizados, o que os distribui em 3 + 2 no Akshan.

O setup tem dois formatos. O simples (Akshan) é uma fila de cinco slots (16px por 24px). O completo (Mordekaiser) são duas colunas, Runas e Dificuldade à esquerda e Itens à direita ocupando as duas linhas (1fr | 1.5fr, espaço de 20px por 32px); abaixo de 1100px os três blocos empilham.

Abaixo de 900px a página vira uma coluna (14px entre blocos, barra de 60px). A lista deixa de ser fixa, a mira grande some e a lista vira uma faixa horizontal de rostos de 56px com encaixe na rolagem; os filtros também viram uma faixa que rola dentro do painel, sem a página rolar para o lado. Os cards descem para 168px de altura e o VS para 54px. O setup simples vira uma linha por slot: rótulo de 92px à esquerda e ícones de 32px à direita, separados por `linha`.

A barra é fixa no topo (64px, 60px no celular) com blur e leva o botão de troca de guia à esquerda e, à direita, o grupo de ações com os botões de som e de tema (8px entre eles). Ritmo de espaço: 16px entre blocos do detalhe, 10px entre lembretes, 34px entre seções, 32px depois do Resumo, 16px antes do rodapé. Todo alvo de toque tem pelo menos 44px.

## Elevation & Depth

Híbrido: a maior parte da profundidade é tonal (fundo, painel, painel alto) com molduras finas na cor do acento, e só os cards de campeão, o menu de guias e o círculo VS ganham sombra. A luz radial do topo dá a sensação de cena iluminada.

### Shadow Vocabulary
- **Sombra** (token `--sombra`: `0 10px 30px rgba(0, 0, 0, .45)` no Akshan escuro, `rgba(90, 64, 10, .14)` no claro; `rgba(0, 0, 0, .5)` no Mordekaiser escuro, `rgba(10, 60, 30, .14)` no claro): cards Você e Inimigo e o menu de guias.
- **Relevo do botão** (`box-shadow: inset 0 1px 0 rgba(255, 255, 255, .6), 0 6px 18px rgba(0, 0, 0, .45)`): só o círculo VS, com o brilho de borda em cima.
- **Brilho da mira** (`filter: drop-shadow(0 0 4px rgba(255, 214, 120, .75)) drop-shadow(0 1px 3px rgba(0, 0, 0, .6))`): o losango que trava no card do inimigo, só no Akshan.
- **Anel do retrato** (`box-shadow: 0 0 0 2px var(--acento)`): o retrato do campeão do guia no botão de troca.
- **Anel duplo do escolhido** (`box-shadow: 0 0 0 2px var(--painel), 0 0 0 4px var(--acento)`, mais a borda de 2px em `destaque`): o campeão escolhido na lista em todo guia que não é o Akshan.

### Named Rules
**A Regra da Luz de Cima.** A luz vem do topo da tela, numa camada fixa atrás de tudo. Não há brilhos radiais saindo do centro dos componentes, exceto o clarão do overlay de travar.

## Shapes

Cantos discretos e uma geometria de mira. Pips de dificuldade usam 2px, selos, tags e o número de dificuldade 4px, ícones de campeão e de item 6px, campos, botões de navegação e itens do menu 8px, cards, lembretes e Resumo 10px, a lista, o setup e o menu de guias 12px. Chips e o botão de troca de guia são pílulas; o VS, os botões de som e de tema, runas, números dos lembretes, retratos e avatares são círculos. O VS leva uma borda de 3px na cor do fundo, que o recorta sobre a junção dos dois cards.

A forma assinatura do Akshan é a da Punição: losango com círculo inscrito e setas triangulares laterais apontando para dentro. Ela aparece em três escalas: a mira grande em volta da lista (círculo duplo, um a 1.5px e outro fino a 1px com 45% de opacidade, mais as setas), a mira no card do inimigo (losango de 3.5px, círculo de 1px e setas, com 58% da altura do card a partir de 5% do topo, para não cobrir o nome; 32% a partir de 13% no celular) e o losango pequeno girado 45° em volta do campeão escolhido. Nos outros guias a mira fica só com o círculo duplo, sem setas e sem alvo no card. No celular a mira grande some com a faixa de rostos; o alvo no card fica.

O losango pequeno é da casa toda: os dois losangos de 14px ao lado de "Escolhe o inimigo" e o marcador de 7px girado 45° nas listas das seções aparecem em todos os guias.

## Components

### Botão de travar (VS)
O fecho metálico da escolha, no centro do duelo.
- **Shape:** círculo de 66px (54px no celular), borda de 3px em `fundo`, centrado entre os dois cards.
- **Cor:** gradiente vertical de `botao-1` para `botao-2` (ouro no Akshan, verde no Mordekaiser), "VS" em Cinzel 800 21px (17px no celular) em `tinta-arte`; igual nos dois temas.
- **Hover / Active:** brilho +8% no hover, encolhe para 95% ao apertar.
- **Acessibilidade:** o "VS" é escondido do leitor de tela; o nome acessível é "Travar o pick contra X", atualizado a cada inimigo.

### Chips de filtro
- **Style:** pílula de 44px, fundo transparente, borda `linha-forte`, Hanken 600 14px, com ícone do feitiço ou runa a 20px quando houver. O grupo fica em até 360px, centralizado.
- **State:** ligado vira o destaque cheio com tinta escura; hover acende a borda em `acento-vivo`.
- **Por guia:** cada formato traz seus filtros (Akshan: Só com guia, Ignite, TP, Exhaust, Electro; Mordekaiser: Fácil, Médio, Difícil).

### Cards de campeão
- **Corner Style:** 10px, em paisagem com 240px de altura (168px no celular), metade da largura do duelo.
- **Background:** a arte centralizada do campeão (`img/champion/centered`) cobre o card, enquadrada a 22% do topo; um escurecimento de baixo para cima segura o nome.
- **Shadow Strategy:** sombra (ver Elevation).
- **Border:** 1px `linha-forte`.
- **Conteúdo:** selo no canto de cima (Você à esquerda em `destaque-arte`, Inimigo à direita em `branco-arte`), nome em Cinzel e título do campeão embaixo (alinhados à direita no inimigo) e, no inimigo, a linha do guia: no Akshan a marca "no guia" com bolinha; no formato completo cinco pips em `destaque-arte` e "Dificuldade N/5".

### Busca
- **Style:** 46px, fundo `fundo`, borda `linha-forte`, cantos de 8px, lupa em SVG e a contagem "47/47" em `acento` com números tabulares.
- **Focus:** a borda e o ícone acendem em `acento-vivo`.

### Painéis
A lista, o setup, o Resumo e cada lembrete são painéis com fundo `painel` e borda `linha`. Os lembretes têm 12px por 16px de padding, o número num círculo de 30px no destaque e os termos-chave sublinhados no destaque (2px, afastado 5px). No setup simples, "Tanto faz" e "Sem anotação" vão em itálico `texto-baixo`, centralizados na vertical com 36px de altura mínima, a altura de um ícone.

### Navegação
- **Troca de guia:** pílula de 48px com o retrato do campeão do guia (38px, anel de 2px em `acento`), o nome em Cinzel `acento-vivo` e a rota (por exemplo "Mid") em texto baixo 13px, quando houver, mais um chevron em `acento` que gira 180° ao abrir (0.2s). Em repouso não tem borda nem fundo; no hover ou aberto ganha `painel` e borda `linha-forte`.
- **Menu de guias:** painel de até 340px, cantos de 12px, borda `linha-forte` e sombra, com o título "Guias de matchup" em rótulo, um item de 60px por guia (retrato de 42px, nome em Cinzel 17px, rota, autor e número de matchups) e a nota "O site sempre abre no último guia que você usou". O guia aberto fica em `painel-alto` com "Aberto" em `acento-vivo`. O guia escolhido fica em `localStorage` na chave `guia`, e o endereço vira `#<guia>/<campeão>` (os links antigos `#<campeão>` abrem no Akshan).
- **Som e tema:** dois botões redondos de 44px à direita da barra, com borda `linha-forte` e ícone em `acento-vivo`. O de som mostra o alto-falante ligado ou mudo, usa `aria-pressed` e grava a escolha em `localStorage` na chave `som`; o de tema mostra a lua no escuro e o sol no claro e grava na chave `tema`.
- **Anterior / próximo:** botões de 44px com ícone do campeão e seta ao lado do título das notas; as setas do teclado fazem o mesmo. Abaixo de 520px fica só o ícone.
- **Rodapé:** a fonte das notas com o link "Ver a planilha original" (e os outros links do autor), e o crédito da Riot, em texto baixo 14px.

### Campeão na lista
Ícone de 52px ou mais (56px na faixa do celular) com borda `linha-forte` e cantos de 6px. O escolhido ganha borda de 2px no destaque: no Akshan com o losango pequeno girado em volta, nos outros guias com o anel duplo. No Akshan, os campeões "no guia" levam uma bolinha no destaque no canto de cima; no formato completo, cada rosto leva o número de dificuldade num selinho escuro de 17px no canto de baixo (Hanken 700 11px).

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
Desenhada a partir do vídeo oficial do R do Akshan. Em volta da lista: círculo duplo e duas setas laterais apontando para o centro. No card do inimigo: losango dourado com círculo inscrito e setas laterais para dentro, com brilho, acima do nome; a cada troca de inimigo ele refaz a animação `trava-alvo` (0.5s, `cubic-bezier(.16, 1, .3, 1)`, entra de 135% de escala e opacidade zero). Só existe com `data-guia="akshan"`; nos outros guias ficam apenas os dois círculos em volta da lista.

### Travar o pick (animação)
Ao tocar no VS, um overlay escuro abre com as duas artes de carregamento (molduras de 2px em `botao-2`) deslizando dos lados até o meio (0.7s), um clarão radial de `brilho` para `brilho-2` no centro e "VS" em Cinzel (0.9s, com 0.25s de atraso). Fecha sozinho em 1.5s, ou com clique, Enter ou Esc, e a página só desce até o setup se ele não estiver à vista. Com "reduzir movimento", a animação é pulada e só a descida acontece, sem rolagem suave.

### Sons do cliente
Os sons vêm do cliente do LoL, na pasta `sons/` (`sons/ui/` para a interface, `sons/vo/` para as falas), e os volumes moram no objeto `VOLUME` do script.
- **Escolher campeão:** o clique do grid (também pelo Enter na busca).
- **Mouse sobre um rosto:** o hover do grid, só com mouse e no máximo um a cada 70ms.
- **VS:** o clique de travar e, 180ms depois, a fala de escolha do campeão do guia, em português.
- **Anterior e próximo:** os cliques de seta, também pelas setas do teclado.
- **Filtros:** o clique de chip.
- **Menu de guias:** um som para abrir e outro para fechar.
- **Tema e o próprio botão de som:** o clique pequeno.

**A Regra do Som por Ação.** Todo som nasce de um gesto do leitor (clique, tecla ou mouse sobre um rosto); nada toca sozinho ao carregar ou em animação. Todo som passa pelo botão de som, e o hover nunca toca no toque.

## Do's and Don'ts

### Do:
- **Do** usar os tokens pelo nome (`--acento`, `--destaque`, `--painel`, `--linha-forte`...) para que o tema claro e a paleta de cada guia funcionem sozinhos.
- **Do** criar um guia novo redefinindo os mesmos tokens em `:root[data-guia="<id>"]` e na variante `[data-tema="claro"]`, incluindo os de sobre a arte e do botão.
- **Do** reservar o destaque para o que é seu ou está ativo: selo Você, filtro ligado, campeão escolhido, número do lembrete, termo-chave, pip ligado.
- **Do** desenhar marcadores novos com a geometria da casa (losango, círculo, setas apontando para dentro); a mira completa da Punição fica só no Akshan.
- **Do** manter alvos de toque de pelo menos 44px e o foco em contorno `acento-vivo` de 2px afastado 3px.
- **Do** respeitar "reduzir movimento" em qualquer animação nova, como a mira, o travar do pick e o chevron da troca de guia já fazem.
- **Do** manter o matchup do Akshan inteiro na tela a 1440×900; o que entrar no detalhe precisa caber nesse orçamento ou sair dele.
- **Do** tocar sons novos pela mesma função, com volume no objeto `VOLUME`, só por ação do leitor e respeitando o botão de som.

### Don't:
- **Don't** desenhar raios de sol saindo do centro da mira ou dos cards.
- **Don't** trazer o verde do guia de referência para a paleta do Akshan; o verde do Mordekaiser é dele, do Reino da Morte.
- **Don't** usar cor fixa fora da arte do campeão; fora dela, tudo passa pelos tokens dos temas e dos guias.
- **Don't** pôr a mira da Punição (alvo no card, setas, losango em volta do escolhido) em guia que não seja o do Akshan.
- **Don't** usar Cinzel em parágrafos, rótulos de slot, chips ou tabelas.
- **Don't** deixar a página rolar para o lado; faixas largas (como a lista e os filtros no celular) rolam dentro do próprio painel.
- **Don't** deixar o alvo da mira cobrir o nome do inimigo no card.
