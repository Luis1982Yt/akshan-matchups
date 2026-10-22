---
version: 1
slug: "src-template-html"
primary_target: "src/template.html"
related_targets: ["index.html"]
---

## Escopo

Página única do guia de matchups do Akshan mid (src/template.html → index.html). Modo: Read. Celular primeiro (390 px), desktop 1440 px. Consulta em segundos na seleção de campeões e leitura com calma fora dela.

## Direction contract

THESIS: A página é a seleção de campeões das Sentinelas da Luz: você (Akshan) de um lado, o inimigo do outro, o anel dourado no meio para escolher, e um botão de travar o pick que leva ao setup e aos lembretes. Recusa o site de builds genérico de cartões e o verde do guia de referência.

OWN-WORLD: Preto quente com ouro, amarelo e branco (escuro, padrão) ou marfim com ouro escuro (claro, no botão). Títulos em Cinzel em caixa-alta espaçada, texto em Hanken Grotesk. Molduras finas douradas, selos amarelos (Você) e brancos (Inimigo), anel com marcações na borda, botão dourado de travar. Sem raios de sol saindo do centro.

STORY: O leitor procura ou toca no inimigo no anel, vê a arte dele no card do inimigo, trava o pick (as duas artes se encontram), lê o setup com ícones e os lembretes numerados com termos sublinhados, e passa para o próximo matchup.

FIRST VIEWPORT: Desktop: três colunas, card Você (arte em pé do Akshan) | painel "Escolhe o inimigo" com busca, filtros e anel | card Inimigo com o botão Travar o pick abaixo. Celular: anel no topo, os dois cards lado a lado, botão de travar em largura total, setup logo abaixo.

FORM: Direção fixada pelo usuário (referência arthurlanches.com.br + Sentinelas da Luz, com a mira do R do Akshan no lugar do anel), sem sorteio. seed: none (direção fixada pelo usuário, sem sorteio)

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Sinal e movimento

Interação assinatura: travar o pick abre as duas artes de carregamento deslizando dos lados até o meio com um brilho branco-dourado e "VS"; fecha sozinho em 1,5 s (ou clique, Enter, Esc) e desce até o setup. Reduzir movimento: pula a animação e só desce.

## Decisões em aberto

Ícones de "Vamps", "Scaling", "Crit"; significado de "no guia"; filtros por classe e troca de skin (exigiriam dados novos da Riot).
