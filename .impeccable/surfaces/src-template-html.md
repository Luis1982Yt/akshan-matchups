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

STORY: O leitor procura ou toca no inimigo na lista à esquerda (com o clique do cliente do LoL), vê a arte dele no card do inimigo, lado a lado com a do Akshan, toca no VS entre os dois para travar o pick (as duas artes se encontram e o Akshan fala a frase de escolha em português), lê o setup com ícones e os lembretes numerados com termos sublinhados ali mesmo, sem rolar no desktop, e passa para o próximo matchup pelas setas, na tela ou no teclado. O crédito do autor e o link da planilha original ficam no rodapé.

FIRST VIEWPORT: Desktop (1440×900): duas colunas. À esquerda, o painel "Escolhe o inimigo" fixo, de 440px, com busca, filtros em 3 + 2 e a lista dentro da mira da Punição. À direita, o duelo em paisagem (card Você | círculo VS | card Inimigo, 240px de altura, arte centralizada), o setup, os lembretes com anterior e próximo e o rodapé, tudo sem rolar no Akshan. No topo, só o guia com a rota, e os botões de som e de tema. Celular: a lista vira uma faixa horizontal de rostos sem a mira grande, os dois cards de 168px lado a lado com o VS de 54px no meio, e o setup logo abaixo, um slot por linha.

FORM: Direção fixada pelo usuário (referência arthurlanches.com.br + Sentinelas da Luz, com a mira do R do Akshan no lugar do anel), sem sorteio. seed: none (direção fixada pelo usuário, sem sorteio)

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Sinal e movimento

Interação assinatura: o círculo VS entre os dois cards trava o pick. Abre as duas artes de carregamento deslizando dos lados até o meio com um clarão na cor do guia e "VS"; fecha sozinho em 1,5 s (ou clique, Enter, Esc) e só desce até o setup se ele não estiver à vista, como no celular. A mira da Punição refaz a trava no card do inimigo a cada troca, acima do nome. Reduzir movimento: pula as duas animações e só desce.

Som: os sons do cliente do LoL (pasta sons/) tocam só por ação do leitor e passam pelo botão de som (aria-pressed, localStorage "som"). Clique do grid ao escolher, hover do grid só com mouse e no máximo um a cada 70 ms, clique de travar seguido da fala de escolha do campeão do guia ao tocar no VS, cliques de seta em anterior e próximo (também pelas setas do teclado), clique de chip nos filtros, abrir e fechar no menu de guias e um clique pequeno no tema e no próprio botão de som. Volumes no objeto VOLUME do script.

Sem glossário: o bloco "Como ler a planilha" saiu; a página não explica a planilha, mostra o matchup.

## Decisões em aberto

Ícones de "Vamps", "Scaling", "Crit"; significado de "no guia"; filtros por classe e troca de skin (exigiriam dados novos da Riot).
