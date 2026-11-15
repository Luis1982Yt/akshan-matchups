# Ideias (anotadas, ainda não fazer)

Lista do dono para depois. Cada uma com o que já se sabe para não começar do zero.

## Importar feitiços de invocador (app) — FEITO e publicado (app-v6, 2026-11-15)
- Feito: `importar.json` traz `feiticos`, o app grava na seleção de campeões mantendo a tecla do Flash.
  O dono mandou publicar sem testar no PC. O .exe é gerado e testado no GitHub (`.github/workflows/app-exe.yml`);
  falta só confirmar numa seleção de campeões de verdade.
- Hoje o app importa runas e itens da matchup no cliente. Faltam os feitiços (ex.: Flash + Incendiar).
- Caminho provável: API local do cliente na seleção de campeões, `PATCH /lol-champ-select/v1/session/my-selection`
  com `spell1Id` / `spell2Id` (ids numéricos do `summoner.json` do Data Dragon, campo `key`).
- Os guias já guardam os feitiços em `feiticos` (Garen, Akali, Fiora...). Quando a matchup traz duplas alternativas
  (Garen: `feiticos_texto`), importar a primeira e mostrar as outras como opção.
- Cuidar da ordem D/F do jogador (Flash na mesma tecla de sempre): ler a seleção atual antes e manter o Flash onde estava.

## Overlay no jogo (estilo Porofessor) com build e cooldowns — FEITO e publicado (app-v7, 2026-11-15)
- Feito: janela `Overlay` no app + modo `?overlay` do site (dicas, setup e tabela fixa de recargas; sem contador ao
  vivo, que a Riot proíbe). Falta confirmar numa partida de verdade (posição, foco, modo sem bordas).
- Uma janela por cima do jogo com a matchup da partida: build, dicas curtas, cooldowns do inimigo.
- O app já lê a seleção de campeões; dentro da partida dá para ler a Live Client Data API (`https://127.0.0.1:2999/liveclientdata/allgamedata`):
  campeões, itens, nível.
- **Antes de fazer, ler a política da Riot para apps de terceiros**: overlay é permitido, mas há regras (nada de dar
  vantagem que o jogo não dá, por exemplo timers automáticos de feitiços/ultimate do inimigo; "cooldowns" tem que ser
  informativo, tipo a tabela de recargas por nível que o site já mostra, não um contador ao vivo).
- Precisa de janela sempre-no-topo sem foco, transparente (pywebview tem limites; ver alternativas no Windows).
- Só no PC do dono para testar (precisa do LoL rodando).
