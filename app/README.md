# App da seleção de campeões (Windows)

Programa de bandeja que acompanha a seleção de campeões do LoL. Quando você **trava** um campeão que tem guia no site (Akshan, Mordekaiser, Illaoi...), ele mostra o guia dele numa janela própria, direto na matchup contra o inimigo mais provável da mesma rota. Passar o mouse ou só marcar o campeão não conta.

**Nunca durante a partida:** o app lê a fase do cliente (`/lol-gameflow/v1/gameflow-phase`); quando a partida começa (GameStart/InProgress) a janela some e nada abre até a próxima seleção. Escondida, o navegador da janela fica em modo de pouca memória (`MemoryUsageTargetLevel = Low`).

**Sem travar:** tudo o que mexe na janela vai para a fila da thread dela (`BeginInvoke`) sem esperar resposta; as chamadas do pywebview que esperam (`evaluate_js`, `show`...) às vezes se cruzavam e congelavam o app na troca de guia.

**Todos os guias (v3):** a lista de guias vem de `https://akshan-matchups.vercel.app/guias-app.json`, que o `scripts/build.py` gera junto com o site (campeão de cada guia, rota e matchups com o slug do site). Guia novo no site já funciona no app sem gerar outro .exe.

**Janela própria (v2):** o site roda dentro do app pelo WebView2 do Windows (pywebview), numa janela lateral estreita (460×900, encostada na direita na primeira vez; tamanho e posição ficam salvos). Trocar de matchup muda só o `#` do endereço, sem recarregar. Fechar no X esconde a janela; "Sair" no menu fecha o app. "Sempre por cima" no menu fixa a janela na frente do cliente. Skin, tema e língua do site ficam salvos em `%APPDATA%\AkshanMatchups\janela`. "Abrir no navegador" continua no menu. `AkshanMatchups.exe --testar-janela` abre a janela numa matchup, troca e fecha sozinho (anota no `log.txt`).

## Como funciona

- Lê o `lockfile` do cliente (`C:\Riot Games\League of Legends\lockfile`; se não achar, procura a pasta do `LeagueClientUx.exe` aberto) e consulta `GET /lol-champ-select/v1/session` a cada 1,5 s. **Só leitura**: o app nunca escolhe, bane nem aceita fila.
- O seu campeão (`championId` ou `championPickIntent`) escolhe o guia pela chave numérica do campeão em `guias-app.json`. Inimigos escolhidos (`theirTeam > championId`) viram nomes pelo Data Dragon e só contam os que estão nesse guia (lista baixada do site ao abrir; sem internet, usa o cache ou a cópia embutida no .exe).
- Entre eles, fica com quem mais joga na rota do guia (Top, Mid...): fração das partidas do campeão nessa rota, de `cdn.merakianalytics.com/.../championrates.json`. Se essa fonte falhar, vale a ordem do guia.
- Abre a matchup (`https://akshan-matchups.vercel.app/#<guia>/<slug>`, mesma regra do `slug()` do site) só quando o alvo muda, com pelo menos 5 s entre aberturas. Se aparecer um inimigo com mais cara de mid, troca; se o escolhido sair do time inimigo, vai para o próximo.
- Menu da bandeja: estado (aguardando o cliente / fora da seleção / na seleção), "Abrir o site", "Inimigos agora" (para abrir outro na mão), "Iniciar com o Windows" e "Sair". Inglês se o Windows estiver em inglês.
- "Iniciar com o Windows" vem ligado: o .exe grava `AkshanMatchups` em `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` do próprio usuário. Desmarcar apaga. Rodando como script (`python app/akshan_app.py`) ele não mexe no registro.
- Configuração, cache dos dados e `log.txt` ficam em `%APPDATA%\AkshanMatchups`.

## Desenvolvimento

```
pip install -r app/requirements.txt
python -m unittest app/test_akshan_app.py
python app/akshan_app.py
```

Os testes usam sessões de exemplo (fora da seleção, campeão sem guia, Akshan no mid, Mordekaiser e Illaoi no top, troca de campeão, inimigo trocado, intervalo mínimo) e não precisam do cliente.

## Gerar o .exe

```
python app/gerar_exe.py
```

Sai em `app/dist/AkshanMatchups.exe` (PyInstaller, um arquivo só, sem console, com o ícone de `src/icone/`). `AkshanMatchups.exe --testar` confere o pacote sem bandeja e sem registro: lê os dados e uma sessão e anota no `log.txt`.

Para publicar uma versão nova: `gh release create app-v3 app/dist/AkshanMatchups.exe --title "..." --notes "..."` e troque o link `APP_URL` no `src/template.html` se mudar de tag (o link atual aponta para `releases/latest`, então em geral não precisa).
