# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Site estático sem dependências: `src/template.html` (HTML, CSS e JS num arquivo só) + `src/guias.json` + os dados de cada guia em `src/guias/<campeão>/`, juntados por `python scripts/build.py` em `index.html`. Precisa abrir com dois cliques (file://). Sem npm, sem framework.

## Users

Jogadores de League of Legends em português do Brasil que jogam com o campeão de um dos guias (hoje Akshan mid, a prioridade, Mordekaiser top e Illaoi top). O site também tem versão em inglês. Usam em dois momentos que importam igual:
- na seleção de campeões, no celular, nos segundos antes do jogo: bater o olho em runa, secundária, feitiço, bota, build e no lembrete do matchup;
- fora da partida, estudando com calma: ler os lembretes inteiros e comparar matchups.

## Product Purpose

Transformar planilhas de matchup de jogadores numa consulta rápida e agradável de ler, uma por campeão: "Akshan Matchups - Peteruso" (48 matchups), a planilha de matchups do Meowdekaiser para Mordekaiser (139 matchups) e a do Hachiragi para Illaoi (57 matchups). Novos campeões entram como novos guias, sem perder o acesso rápido ao guia de sempre. Sucesso: achar o adversário em segundos e sair sabendo o que levar e como jogar a lane.

## Positioning

Não é um agregador de estatísticas: é a leitura das notas de um jogador de cada campeão, com a voz original da planilha (gírias e erros de digitação incluídos), organizada por matchup.

## Operating Context

- Projeto de fã do dono do site, usando as notas públicas das planilhas do Peteruso e do Meowdekaiser. Cada autor aparece como fonte (com os links públicos dele), sem o site parecer oficial deles.
- Interface em português ou inglês (botão PT/EN). As notas do Akshan em inglês são uma tradução mantida à parte; o texto original da planilha nunca muda, e linha sem tradução aparece em português.
- As planilhas do Meowdekaiser e do Hachiragi são em inglês: o modo EN mostra o original e o modo PT mostra uma tradução mantida à parte (`traducao_pt.json`), com itens e runas pelo nome do cliente em português. As outras abas dessas planilhas entram como páginas do guia.
- Imagens de campeões, runas, feitiços e itens vêm do Data Dragon da Riot.
- Akshan: cada matchup tem runa principal, secundária, feitiço, bota, build (com os ícones exatos colados na planilha), lembrete (itens separados por quebra de linha) e a dificuldade, que é a cor da célula do campeão na planilha (classificação do Peteruso: vermelho escuro muito difícil, vermelho claro difícil, amarelo médio, verde fácil, ciano muito fácil). A marca "no guia" saiu do site a pedido do dono.
- Mordekaiser: cada matchup tem runas, itens (com builds condicionais), dificuldade early/mid/late/geral de 1 a 5, às vezes um TL;DR, e as seções Enemy Cooldowns, Early Game, How to trade, What to watch out for e Tips.

## Capabilities and Constraints

- Busca por campeão ou palavra das notas; filtros por guia (Akshan: as cinco dificuldades, Ignite, TP, Exhaust, Electro; Mordekaiser: Fácil, Médio, Difícil); navegação anterior/próximo; tier list por dificuldade.
- Troca de guia no topo; o site abre no último guia usado; links `#guia/campeão` (e os antigos `#campeão` do Akshan).
- O texto das notas não pode ser alterado; só a forma de mostrar.
- Celular primeiro (390 px) e desktop (1440 px); a página nunca rola para o lado.
- Dois temas: escuro por padrão e claro num botão; a escolha fica salva no navegador.

## Brand Commitments

- Tudo em português do Brasil.
- Cada guia tem a vibe do seu campeão. Akshan: Sentinelas da Luz (amarelo, branco, dourado e preto). Pedido explícito do dono em 2026-10-22, com a estrutura de seleção de campeões do arthurlanches.com.br como referência (você, anel de inimigos, inimigo, travar o pick).
- Aviso obrigatório: site de fã, sem ligação com a Riot Games.
- Elementos de conteúdo que permanecem: o duelo Akshan contra o adversário com as duas splash arts, a lista de campeões com ícones e a marca de "no guia", a linha Runa / Secundária / Feitiço / Bota / Build com ícones do jogo e os termos-chave destacados nos lembretes. O "Como ler a planilha" (glossário) foi removido a pedido do dono em 2026-10-22.

## Evidence on Hand

- `src/guias/akshan/`: os 47 matchups do Akshan e o meta do Data Dragon.
- `src/guias/mordekaiser/`: a planilha do Meowdekaiser (`planilha.csv`) e os 139 matchups separados (`matchups.json`), gerados por `scripts/atualizar_mordekaiser.py`.
- Não há depoimentos, números de uso ou endosso do Peteruso nem do Meowdekaiser; não inventar.

## Product Principles

1. A nota do jogador é o conteúdo: mostrar sem reescrever.
2. Consulta em segundos na seleção de campeões, leitura confortável fora dela.
3. Fã, não oficial: créditos claros para a planilha e para a Riot.
4. Funciona em qualquer lugar: dois cliques, sem instalar nada.

## Accessibility & Inclusion

WCAG AA: contraste, foco de teclado visível, alvos de toque de 44 px no celular, respeito a "reduzir movimento".
