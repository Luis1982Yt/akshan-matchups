# Guias de matchup

Site de fã com guias de matchup de vários campeões, cada um feito a partir da planilha de um jogador. Sem servidor e sem dependências: abra o `index.html` com dois cliques.

Guias atuais:
- **Akshan mid**: 48 matchups da planilha "Akshan Matchups - Peteruso", lida ao vivo no site publicado.
- **Mordekaiser** (escondido por enquanto, com `"oculto": true` em `src/guias.json`): 139 matchups da planilha do Meowdekaiser. Os dados continuam no repositório; é só tirar o `oculto` para voltar.

## Português e inglês

- O botão PT/EN no topo troca a língua do site inteiro e fica salvo no navegador. Na primeira visita vale a língua do navegador.
- As notas do Akshan em inglês ficam em `src/guias/akshan/traducao_en.json` (`linhas`: cada linha da planilha → tradução; `celulas`: nomes de runas e itens das colunas de setup).
- Quando o Peteruso muda uma linha, ela aparece em português no modo EN até ganhar tradução. `python scripts/atualizar_akshan.py` lista essas linhas.

## Como navegar

- Com mais de um guia visível, o nome do campeão no topo abre o menu de guias.
- Teclado: `/` vai para a busca; ← → trocam para o matchup anterior/próximo; ↑ ↓ andam uma linha na grade de campeões (no celular, um campeão).
- O site sempre abre no último guia usado (fica salvo no navegador).
- Cada guia e cada matchup tem link próprio: `index.html#mordekaiser`, `index.html#mordekaiser/aatrox`. Links antigos do Akshan (`#ahri`) continuam funcionando.

## Arquivos

- `src/template.html`: HTML, CSS e JS do site. É aqui que se edita. Os marcadores `/*FONTS*/` e `/*GUIAS*/` recebem as fontes e os dados.
- `src/guias.json`: a lista de guias (ordem do menu, autor, créditos, formato e pasta dos dados).
- `src/guias/akshan/`: `rows.js` no formato `[campeão, runa, secundária, feitiço, bota, build, lembrete, noGuia(1/0)]`, `meta.json` com ids, títulos (pt e en), ícones e `mira` (ponto do splash, em % de largura e altura, onde fica o centro da mira do card; escolhido à mão para pegar rosto + corpo. Campeão novo sem `mira` usa 50, 38), e `traducao_en.json`.
- `scripts/atualizar_akshan.py`: baixa a planilha do Peteruso para a cópia embutida (a que aparece sem internet), lê os ícones de cada célula, acrescenta campeões novos e lista linhas sem tradução. Depois rode o build.
- `scripts/icones_planilha.py` e `src/guias/akshan/icones_planilha.json`: os ícones de runa, secundária, bota e build saem das imagens coladas na planilha (só vêm no xlsx; o CSV traz só o texto). Cada imagem é reconhecida pelo md5 em `meta.json > imagens` e vira uma peça de `meta.json > pecas` (nome em pt e en). Se o Peteruso mudar o texto de uma célula, o site usa `texto_pecas` até a próxima leitura; imagem nova aparece na saída do script para cadastrar.
- `src/guias/mordekaiser/`: `planilha.csv` (cópia da planilha) e `matchups.json` (a planilha separada em runas, itens, dificuldade e seções).
- `src/fonts/`: Cinzel e Hanken Grotesk (subconjunto latino), embutidas no HTML pelo build.
- `modelo/akshan.glb`: o Akshan 3D do jogo (malha, esqueleto, texturas e as animações idle, variação, dança, piada e risada). Aparece numa coluna à direita só em tela de 1720 px ou mais, no guia do Akshan e no site publicado; clique nele faz uma emote. O three.js vem do jsDelivr e só é baixado nesse caso.
- `scripts/modelo3d/`: como o `.glb` foi feito. `wad.py` extrai os arquivos do `Akshan.wad.client` da instalação do LoL (`C:\Riot Games\League of Legends\Game\DATA\FINAL\Champions`) e `lol2glb.py` converte esqueleto, malha e animações para glTF (as texturas em PNG vêm do CommunityDragon). Precisa de `pip install zstandard xxhash numpy pillow`.
- `src/icone/`: ícone da aba (`icone-64.png`) e da tela inicial do celular (`apple-180.png`), também embutidos pelo build; `original.webp` é a arte de origem.
- `scripts/build.py`: gera o `index.html`. Rode `python scripts/build.py` depois de qualquer mudança.
- `sons/`: sons do cliente do LoL (seleção de campeões) e a fala de escolha de cada campeão de guia, carregados só quando tocam. `scripts/baixar_sons.py` baixa de novo do CommunityDragon (rode quando entrar um guia novo). O botão de som no topo desliga tudo.
- `scripts/atualizar_mordekaiser.py`: baixa de novo a planilha do Meowdekaiser e os dados do Data Dragon e refaz o `matchups.json` (precisa de internet). Depois rode o build.
- `PRODUCT.md` e `DESIGN.md`: o que o produto é e o sistema visual.

## Adicionar um guia novo

1. Coloque os dados em `src/guias/<campeão>/`. Planilhas no formato do Akshan usam `"formato": "simples"`; planilhas grandes como a do Meowdekaiser usam `"formato": "completo"` com um `matchups.json` (copie o `atualizar_mordekaiser.py` e ajuste as colunas).
2. Acrescente o guia em `src/guias.json`.
3. Se quiser uma paleta própria, crie o bloco `:root[data-guia="<id>"]` (e o do tema claro) no `src/template.html`, como o do Mordekaiser.
4. Rode `python scripts/build.py`.

## Regras

1. Nunca edite o `index.html` direto: ele é gerado.
2. Não mude o texto das notas das planilhas; só a forma de mostrar.
3. Precisa funcionar com dois cliques (file://), sem npm nem framework.
4. Celular primeiro: teste a 390 px e a 1440 px. A página nunca pode rolar para o lado.
5. Mantenha o aviso de site de fã, sem ligação com a Riot, e o crédito de cada planilha.

As imagens de campeões, runas, feitiços e itens vêm do Data Dragon da Riot (precisa de internet). Se uma falhar, o site esconde a imagem e mostra a inicial do campeão na lista. Os sons tocam no Chrome, Edge, Firefox e Android; Safari antigo pode ficar sem som (os arquivos são Ogg Vorbis).
