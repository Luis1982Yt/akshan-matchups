"""Atualiza a cópia embutida do guia do Akshan a partir da planilha do Peteruso.

O site já lê a planilha ao vivo quando abre; esta cópia é o que aparece sem internet
ou antes da planilha responder. Grava src/guias/akshan/rows.js, os ícones de cada célula
(icones_planilha.json, lidos das imagens da planilha), acrescenta campeões novos em meta.json
e lista as linhas que ainda não têm tradução em traducao_en.json
(no modo EN elas aparecem em português). Depois rode `python scripts/build.py`.
"""
import csv
import io
import json
import pathlib
import re
import urllib.request

from icones_planilha import icones_da_planilha

ROOT = pathlib.Path(__file__).resolve().parent.parent
PASTA = ROOT / "src" / "guias" / "akshan"
GUIA = next(g for g in json.loads((ROOT / "src" / "guias.json").read_text(encoding="utf-8")) if g["id"] == "akshan")
from versao_dd import VER  # noqa: E402  (src/versao_dd.txt)


def baixar(url, binario=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    dados = urllib.request.urlopen(req).read()
    return dados if binario else dados.decode("utf-8")


def chave(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


planilha = GUIA["planilha"]
texto = baixar(f"https://docs.google.com/spreadsheets/d/{planilha['id']}/export?format=csv&gid={planilha['gid']}")
linhas = list(csv.reader(io.StringIO(texto)))
cabecalho = linhas.pop(0)
if not re.match(r"campe", cabecalho[0], re.I):
    raise SystemExit(f"Cabeçalho inesperado na planilha: {cabecalho}")

rows = []
for r in linhas:
    r = (r + [""] * 8)[:8]
    if not r[0].strip():
        continue
    rows.append([r[0].strip(), *(c.strip() for c in r[1:7]), 1 if r[7].strip().lower().startswith("s") else 0])

meta_path = PASTA / "meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
novos = [r[0] for r in rows if r[0] not in meta["champs"]]
if novos:
    dd = json.loads(baixar(f"https://ddragon.leagueoflegends.com/cdn/{VER}/data/pt_BR/champion.json"))["data"]
    en = json.loads(baixar(f"https://ddragon.leagueoflegends.com/cdn/{VER}/data/en_US/champion.json"))["data"]
    por_nome = {chave(c["name"]): c for c in dd.values()} | {chave(c["id"]): c for c in dd.values()}
    for nome in novos:
        c = por_nome.get(chave(nome))
        if c:
            meta["champs"][nome] = {"id": c["id"], "title": c["title"], "title_en": en[c["id"]]["title"]}
        else:
            print(f"Não achei '{nome}' no Data Dragon; esse matchup fica de fora até o nome bater.")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
rows = [r for r in rows if r[0] in meta["champs"]]

antigo_txt = (PASTA / "rows.js").read_text(encoding="utf-8").strip().rstrip(";")
antigo = {r[0]: r for r in json.loads(re.sub(r",\s*\]$", "]", antigo_txt))}
mudou = [r[0] for r in rows if antigo.get(r[0]) != r]
saiu = [n for n in antigo if n not in {r[0] for r in rows}]

corpo = ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows)
(PASTA / "rows.js").write_text("[\n" + corpo + ",\n]\n", encoding="utf-8", newline="\n")
print(f"{len(rows)} matchups gravados.")
print("Mudaram:", mudou or "nenhum")
if saiu:
    print("Saíram da planilha:", saiu)

traducao_path = PASTA / "traducao_en.json"
if traducao_path.exists():
    traducao = json.loads(traducao_path.read_text(encoding="utf-8"))
    faltam = [(r[0], l) for r in rows for l in (re.sub(r"\s{2,}", " ", x.strip()) for x in r[6].split("\n")) if l and l not in traducao["linhas"]]
    if faltam:
        print(f"Sem tradução em inglês ({len(faltam)}); acrescente em traducao_en.json > linhas:")
        for nome, l in faltam:
            print(f"  {nome}: {l}")

# Ícones de cada célula: só vêm no xlsx (o CSV traz apenas o texto).
xlsx = baixar(f"https://docs.google.com/spreadsheets/d/{planilha['id']}/export?format=xlsx", binario=True)
icones, desconhecidas = icones_da_planilha(xlsx, meta.get("imagens", {}))
(PASTA / "icones_planilha.json").write_text(json.dumps(icones, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(f"Ícones lidos de {len(icones)} campeões.")
if desconhecidas:
    print("Imagens novas na planilha que ainda não estão em meta.json > imagens (md5 -> peça):")
    for nome, campo, md5 in desconhecidas:
        print(f"  {nome} ({campo}): {md5}")
