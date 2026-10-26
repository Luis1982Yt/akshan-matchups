# App da seleção de campeões (Windows)

Programa de bandeja que acompanha a seleção de campeões do LoL. Quando você está de Akshan (escolhido ou só marcado), ele mostra o guia numa janela própria, direto na matchup contra o mid inimigo mais provável.

**Janela própria (v2):** o site roda dentro do app pelo WebView2 do Windows (pywebview), numa janela lateral estreita (460×900, encostada na direita na primeira vez; tamanho e posição ficam salvos). Trocar de matchup muda só o `#` do endereço, sem recarregar. Fechar no X esconde a janela; "Sair" no menu fecha o app. "Sempre por cima" no menu fixa a janela na frente do cliente. Skin, tema e língua do site ficam salvos em `%APPDATA%\AkshanMatchups\janela`. "Abrir no navegador" continua no menu. `AkshanMatchups.exe --testar-janela` abre a janela numa matchup, troca e fecha sozinho (anota no `log.txt`).

## Como funciona

- Lê o `lockfile` do cliente (`C:\Riot Games\League of Legends\lockfile`; se não achar, procura a pasta do `LeagueClientUx.exe` aberto) e consulta `GET /lol-champ-select/v1/session` a cada 1,5 s. **Só leitura**: o app nunca escolhe, bane nem aceita fila.
- Inimigos escolhidos (`theirTeam > championId`) viram nomes pelo Data Dragon e só contam os que estão no guia (`src/guias/akshan/rows.js`, baixado do GitHub ao abrir; sem internet, usa a cópia embutida no .exe).
- Entre eles, fica com quem mais joga mid: fração das partidas do campeão que são no mid, de `cdn.merakianalytics.com/.../championrates.json`. Se essa fonte falhar, vale a ordem do guia.
- Abre o navegador (`https://akshan-matchups.vercel.app/#akshan/<slug>`, mesma regra do `slug()` do site) só quando o alvo muda, com pelo menos 5 s entre aberturas. Se aparecer um inimigo com mais cara de mid, troca; se o escolhido sair do time inimigo, vai para o próximo.
- Menu da bandeja: estado (aguardando o cliente / fora da seleção / na seleção), "Abrir o site", "Inimigos agora" (para abrir outro na mão), "Iniciar com o Windows" e "Sair". Inglês se o Windows estiver em inglês.
- "Iniciar com o Windows" vem ligado: o .exe grava `AkshanMatchups` em `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` do próprio usuário. Desmarcar apaga. Rodando como script (`python app/akshan_app.py`) ele não mexe no registro.
- Configuração, cache dos dados e `log.txt` ficam em `%APPDATA%\AkshanMatchups`.

## Desenvolvimento

```
pip install -r app/requirements.txt
python -m unittest app/test_akshan_app.py
python app/akshan_app.py
```

Os testes usam sessões de exemplo (fora da seleção, sem Akshan, um inimigo, vários, inimigo trocado, intervalo mínimo) e não precisam do cliente.

## Gerar o .exe

```
python app/gerar_exe.py
```

Sai em `app/dist/AkshanMatchups.exe` (PyInstaller, um arquivo só, sem console, com o ícone de `src/icone/`). `AkshanMatchups.exe --testar` confere o pacote sem bandeja e sem registro: lê os dados e uma sessão e anota no `log.txt`.

Para publicar uma versão nova: `gh release create app-v2 app/dist/AkshanMatchups.exe --title "..." --notes "..."` e troque o link `APP_URL` no `src/template.html` se mudar de tag (o link atual aponta para `releases/latest`, então em geral não precisa).
