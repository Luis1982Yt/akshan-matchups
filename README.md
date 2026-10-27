# Guias de matchup

Site de fã com guias de matchup de vários campeões, cada um feito a partir da planilha de um jogador. Sem servidor e sem dependências: abra o `index.html` com dois cliques.

Guias atuais:
- **Akshan mid**: 48 matchups da planilha "Akshan Matchups - Peteruso", lida ao vivo no site publicado.
- **Mordekaiser top**: 139 matchups da planilha do Meowdekaiser, mais as outras abas dela (sobre, itens, runas, setups, criadores) como páginas do guia.
- **Illaoi top**: 57 matchups da planilha do Hachiragi, mais as páginas geral, itens, runas e dicas.

Um guia pode ser escondido com `"oculto": true` em `src/guias.json` (os dados continuam no repositório).

## Português e inglês

- O botão PT/EN no topo troca a língua do site inteiro e fica salvo no navegador. Na primeira visita vale a língua do navegador.
- As notas do Akshan em inglês ficam em `src/guias/akshan/traducao_en.json` (`linhas`: cada linha da planilha → tradução; `celulas`: nomes de runas e itens das colunas de setup).
- Quando o Peteruso muda uma linha, ela aparece em português no modo EN até ganhar tradução. `python scripts/atualizar_akshan.py` lista essas linhas.
- Os guias escritos em inglês (Mordekaiser, Illaoi) têm o caminho inverso em `src/guias/<guia>/traducao_pt.json`: `textos` (cada frase da planilha → português, inclusive cooldowns e páginas), `nomes` (ícone → nome do item ou runa no cliente em português) e `titulos_en` (título de cada campeão em inglês). `python scripts/traducao_pt.py` atualiza os nomes e os títulos e diz quantas frases estão sem tradução; com `--faltando` lista quais. Frase nova aparece em inglês no modo PT até ganhar tradução.

## Como navegar

- Seleção de guia: na primeira visita (sem guia salvo e sem link de guia) o site abre numa tela de escolha do campeão, agrupada por rota, com a arte de cada guia, o autor e o número de matchups; escolher toca o som e a fala de travar o pick. Depois ela volta tocando no campeão do topo.
- Teclado: `/` vai para a busca; ← → trocam para o matchup anterior/próximo; ↑ ↓ andam uma linha na grade de campeões (no celular, um campeão).
- O site sempre abre no último guia usado (fica salvo no navegador).
- Cada guia e cada matchup tem link próprio: `index.html#mordekaiser`, `index.html#mordekaiser/aatrox`. Links antigos do Akshan (`#ahri`) continuam funcionando.

## Arquivos

- `src/template.html`: HTML, CSS e JS do site. É aqui que se edita. Os marcadores `/*FONTS*/` e `/*GUIAS*/` recebem as fontes e os dados.
- `src/guias.json`: a lista de guias (ordem do menu, autor, créditos, formato e pasta dos dados). `acompanhe` lista os canais do bloco "Acompanhe mono …" embaixo da lista de campeões (nome, link e o texto do canal).
- `src/guias/akshan/`: `rows.js` no formato `[campeão, runa, secundária, feitiço, bota, build, lembrete, noGuia(1/0)]`, `meta.json` com ids, títulos (pt e en), ícones e `mira` (ponto do splash, em % de largura e altura, onde fica o centro da mira do card; escolhido à mão para pegar rosto + corpo. Campeão novo sem `mira` usa 50, 38), e `traducao_en.json`.
- `scripts/atualizar_akshan.py`: baixa a planilha do Peteruso para a cópia embutida (a que aparece sem internet), lê os ícones de cada célula, acrescenta campeões novos e lista linhas sem tradução. Depois rode o build.
- `.github/workflows/atualizar-planilha.yml`: o GitHub roda o `atualizar_akshan.py` e o build todo dia às 6h (horário de Brasília) e faz o commit se a planilha mudou; a Vercel publica sozinha. Dá para rodar na hora pela aba Actions do GitHub. Tradução de linha nova continua sendo à mão (até lá ela aparece em português no modo EN).
- `scripts/icones_planilha.py` e `src/guias/akshan/icones_planilha.json`: a dificuldade de cada matchup é a cor da célula do campeão na planilha (classificação do Peteruso: vermelho escuro muito difícil, vermelho claro difícil, amarelo médio, verde fácil, ciano muito fácil) e aparece na borda do retrato, nos filtros e no card do inimigo. Os ícones de runa, secundária, bota e build saem das imagens coladas na planilha (só vêm no xlsx; o CSV traz só o texto). Cada imagem é reconhecida pelo md5 em `meta.json > imagens` e vira uma peça de `meta.json > pecas` (nome em pt e en). Se o Peteruso mudar o texto de uma célula, o site usa `texto_pecas` até a próxima leitura; imagem nova aparece na saída do script para cadastrar.
- `src/guias/mordekaiser/`: `planilha.csv` (cópia da planilha) e `matchups.json` (a planilha separada em runas, itens, dificuldade e seções).
- `src/fonts/`: Cinzel e Hanken Grotesk (subconjunto latino), embutidas no HTML pelo build.
- `modelo/akshan.glb`: o Akshan 3D do jogo (malha, esqueleto, texturas e as animações de idle, dança, provocação, risada, ataque e recall). Aparece numa coluna à direita só em tela de 1720 px ou mais, no guia do Akshan e no site publicado. Arrastar gira, clique faz uma emote e os botões embaixo tocam cada animação (sequências em `SEQ_3D` no template). O X no canto da caixa esconde a coluna e centraliza tudo; escondido, uma alça na borda direita traz de volta (vem ligado; fica salvo no navegador). O three.js vem do jsDelivr e só é baixado nesse caso.
- Skins do Akshan: o botão no card "Você" troca a skin (fica salva em `localStorage > skin`). Cada skin tem a paleta em `:root[data-guia="akshan"][data-skin="<id>"]` (cores tiradas da splash oficial), a arte do card, o modelo `modelo/akshan-<id>.glb` e os efeitos sonoros em `sons/akshan3d/<id>/` (a voz é a do Akshan). A lista fica em `SKINS` no template. Hoje: Padrão, Ciberpop, Rosa de Cristal, Três Honras e Velho Oeste. As setas nas laterais do card passam de uma skin para outra. Cada troca de skin toca uma fala sorteada do Akshan (38 falas, de `scripts/modelo3d/falas.py`). Todas as falas seguem a língua do site: dublagem pt-BR em `sons/vo/akshan/`, `sons/akshan3d/` e `sons/vo/Akshan.ogg`; voz original em inglês em `sons/vo/akshan-en/`, `sons/akshan3d/en/` e `sons/vo/en/Akshan.ogg` (tirada do `Akshan.en_US.wad.client`, que só existe com o LoL em inglês). Os chromas (Ciberpop, Rosa de Cristal e Velho Oeste) aparecem como bolinhas embaixo da skin no menu: usam o mesmo modelo e só trocam as texturas, que o site carrega direto do CommunityDragon; a tabela `CHROMAS` do template sai de `python scripts/modelo3d/chromas.py <pasta com skinN/config.json>`. Para gerar uma skin nova: `python scripts/modelo3d/skin3d.py <número> <Akshan.wad.client> <pasta> modelo/akshan-<id>.glb` e `python scripts/modelo3d/sons3d.py <bancos da skin> <vgmstream-cli> sons/akshan3d/<id> <número>`.
- `scripts/modelo3d/`: como o `.glb` foi feito. `wad.py` extrai os arquivos do `Akshan.wad.client` da instalação do LoL (`C:\Riot Games\League of Legends\Game\DATA\FINAL\Champions`) e `lol2glb.py` converte esqueleto, malha e animações para glTF (as texturas em PNG vêm do CommunityDragon). Os sons das animações (`sons/akshan3d/`, efeitos e a dublagem em português) saem dos bancos do Wwise do mesmo `.wad` e do `Akshan.pt_BR.wad.client`: `bnk.py` liga cada evento do jogo aos áudios e `sons3d.py` converte para OGG com o vgmstream-cli (baixado à parte, não fica no projeto). Qual som toca em cada clipe está em `SONS_CLIPE_3D` no template. Precisa de `pip install zstandard xxhash numpy pillow soundfile`.
- `manifest.webmanifest`, `sw.js` e `icones/`: o site pode ser instalado como app ("Adicionar à tela inicial") e abre sem internet com a última versão vista; com internet a página vem sempre da rede.
- Tier list: botão embaixo da lista, agrupa os campeões pela dificuldade (cor da planilha). Ao vivo: o card "Acompanhe" consulta o decapi.me a cada 5 min e marca quem está em live na Twitch.
- `meta.json > feitico_extra`: feitiço somado ao da planilha numa matchup, combinado com o dono do site (hoje Zoe: + Cleanse). Some sozinho se a planilha passar a ter esse feitiço.
- `meta.json > pecas_manuais`: ícones escolhidos à mão para célula sem imagem na planilha (hoje a build do Malphite: Terminus + Gume do Infinito); vale enquanto o texto da célula for o mesmo.
- `og.jpg` e `scripts/og.py`: a imagem da prévia quando o link é compartilhado (WhatsApp, Discord, X), com uma faixa da splash de cada guia. Rode `python scripts/og.py` quando entrar ou sair um guia e aumente o `?v=` do `og:image` no template (as redes guardam a prévia antiga pelo endereço).
- `src/icone/`: ícone da aba (`icone-64.png`) e da tela inicial do celular (`apple-180.png`), também embutidos pelo build; `original.webp` é a arte de origem.
- `scripts/build.py`: gera o `index.html`. Rode `python scripts/build.py` depois de qualquer mudança.
- `scripts/importar_lol.py` e `src/guias/<guia>/importar.json`: a página de runas (ids do jogo, uma por opção da planilha) e os blocos do conjunto de itens de cada matchup, que o build põe no `guias-app.json` para o app importar no cliente. No Akshan a planilha só traz a runa principal e as secundárias; o resto da página vem de `meta.json > paginas_padrao` (aprovado pelo dono do site). Runa que saiu do jogo vira a que ficou no lugar (Lenda: Tenacidade → Lenda: Aceleração). Testes: `python -m unittest scripts/test_importar_lol.py`.
- `src/versao_dd.txt` e `scripts/versao_dd.py`: a versão do Data Dragon (patch do LoL) de ícones, nomes e cooldowns, a mesma para o site e para os scripts. O workflow diário troca para o patch mais novo sozinho; à mão, `python scripts/versao_dd.py` e depois os `atualizar_*.py`.
- `sons/`: sons do cliente do LoL (seleção de campeões) e a fala de escolha de cada campeão de guia, carregados só quando tocam. `scripts/baixar_sons.py` baixa de novo do CommunityDragon (rode quando entrar um guia novo). O botão de som no topo desliga tudo.
- `scripts/atualizar_mordekaiser.py` e `scripts/atualizar_illaoi.py`: baixam de novo a planilha de cada guia e os dados do Data Dragon e refazem o `matchups.json` e o `paginas.json` (precisa de internet). Depois rode `scripts/traducao_pt.py` e o build. O workflow diário roda tudo isso.
- `PRODUCT.md` e `DESIGN.md`: o que o produto é e o sistema visual.

## App da seleção de campeões (Windows)

`app/` tem um programa de bandeja para Windows: quando o jogador trava um campeão que tem guia no site (lista em `guias-app.json`), ele adivinha o inimigo da mesma rota (entre os inimigos que estão no guia, o que mais joga nela) e mostra o guia numa janela própria, direto na matchup (`#<guia>/<slug>`). A janela some quando a partida começa. Pela API local do cliente, lê a seleção e grava a página de runas e o conjunto de itens da matchup (como o Porofessor; dá para desligar no menu); nunca escolhe, bane nem aceita fila. Inicia com o Windows (dá para desligar no menu da bandeja).

- Download: [releases do GitHub](https://github.com/Luis1982Yt/akshan-matchups/releases/latest) (`AkshanMatchups.exe`, um arquivo só, não precisa de Python). O botão "App para PC" fica no card "Acompanhe" de todos os guias, só no desktop (`APP_URL` no template aponta para a release mais nova).
- Código, testes e como gerar o .exe: `app/README.md` (`python app/gerar_exe.py`; testes com `python -m unittest app/test_akshan_app.py`).
- A pasta `app/` não vai para a Vercel (`.vercelignore`).

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
