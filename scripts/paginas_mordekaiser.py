"""Páginas extras do guia do Mordekaiser: as outras abas da planilha do Meowdekaiser
(introdução, guia de itens, guia de runas, setups alternativos e criadores).

O texto e os links vêm da versão publicada de cada aba; os ícones de item e runa, que na planilha
são imagens, vêm do xlsx e são reconhecidos pelo md5 (src/guias/mordekaiser/imagens.json).
O texto das notas não é alterado: só é separado em partes para mostrar melhor.
"""
import json
import pathlib
import re
import urllib.request

from planilha_xlsx import Planilha, publicado

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "src" / "guias" / "mordekaiser"
PLANILHA = "1BVH44IPxZNBQshDf90XZRJbfKvavVCUIIo_boyBVF8o"
ABAS = {"sobre": 848078357, "itens": 1054535084, "runas": 779082056, "setups": 2121273139, "criadores": 225968364}
DDI = "https://ddragon.leagueoflegends.com/cdn/img/"
from versao_dd import VER  # noqa: E402  (src/versao_dd.txt)


def baixar(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()


def aba(gid):
    return publicado(baixar(f"https://docs.google.com/spreadsheets/d/{PLANILHA}/htmlview/sheet?headers=false&gid={gid}").decode("utf-8"))


def cel(c, r, k):
    """Célula como {texto, links}, ou None."""
    v = c.get((r, k))
    return {"texto": v["texto"], "links": v["links"]} if v and (v["texto"] or v["links"]) else None


def txt(c, r, k):
    v = c.get((r, k))
    return v["texto"] if v else ""


def pagina_sobre(c):
    blocos = [{"tipo": "texto", "titulo": txt(c, 0, 0), **cel(c, 1, 0)}]
    if txt(c, 2, 8):
        blocos.append({"tipo": "aviso", "texto": txt(c, 2, 8) + ("\n\n" + txt(c, 3, 8) if txt(c, 3, 8) else "")})
    # Última mudança do campeão: versão na coluna A, habilidade ("- Nome") e mudanças embaixo.
    linha_patch = next((r for (r, k), v in sorted(c.items()) if k == 0 and v["texto"].startswith("Latest")), None)
    if linha_patch is not None:
        versao, mudancas = "", []
        for r in range(linha_patch + 1, linha_patch + 60):
            a, b = txt(c, r, 0), txt(c, r, 1)
            if re.fullmatch(r"V?\d+\.\d+\w*", a):
                versao = a
            elif a.startswith("-"):
                mudancas.append({"nome": a.lstrip("- ").strip(), "linhas": []})
            elif b and mudancas:
                mudancas[-1]["linhas"].append(b)
        blocos.append({"tipo": "patch", **cel(c, linha_patch, 0), "versao": versao, "mudancas": mudancas})
        # Lista de bugs (coluna I), ao lado.
        bugs = cel(c, linha_patch, 8)
        if bugs:
            itens = [cel(c, r, 8) for r in range(linha_patch + 1, linha_patch + 60) if cel(c, r, 8)]
            blocos.append({"tipo": "lista", **bugs, "itens": itens})
    return blocos


def pagina_itens(c, imgs, mapa):
    estagios = [txt(c, 1, k) for k in (0, 2, 4, 6)]
    por_celula = {}
    for r, k, _off, md5, _b in imgs:
        if md5 in mapa and mapa[md5]["tipo"] == "item":
            por_celula.setdefault((r, k), mapa[md5])
    linhas_img = {r for r, _ in por_celula}
    grupos = []
    for r in range(3, max(r for r, _ in c) + 1):
        if r not in linhas_img:
            # Linha só com texto na A ou B e nada nas colunas de estágio = título de grupo.
            titulo = txt(c, r, 0) or txt(c, r, 1)
            if titulo and not any(txt(c, r, k) for k in (3, 5, 7)) and not titulo.lower().startswith("itemization") and "priority" not in titulo.lower():
                grupos.append({"titulo": titulo, "itens": []})
            continue
        estagio = []
        for i, k in enumerate((0, 2, 4, 6)):
            item = por_celula.get((r, k))
            texto = txt(c, r, k + 1)
            estagio.append({"id": item["id"], "nome": item["nome"], "texto": texto} if item else ({"texto": texto} if texto else None))
        com_item = [e for e in estagio if e and e.get("id")]
        principal = max(com_item, key=lambda e: sum(1 for x in com_item if x["id"] == e["id"]))
        if not grupos:
            grupos.append({"titulo": "", "itens": []})
        grupos[-1]["itens"].append({"id": principal["id"], "nome": principal["nome"], "estagios": estagio})
    return [{"tipo": "itens", "estagios": estagios, "grupos": [g for g in grupos if g["itens"]]}]


def pagina_runas(c, imgs, mapa, arvore_de):
    """Cada bloco de linhas entre os cabeçalhos "Rune / Explanation" é uma árvore; cada linha, um nível dela."""
    arvores, atual, linha_atual = [], None, None
    for r, k, _off, md5, _b in imgs:
        info = mapa.get(md5)
        if not info or info["tipo"] != "runa":
            continue
        arvore = arvore_de[info["chave"]]  # pelo Data Dragon: o caminho do ícone nem sempre é o da árvore
        if not atual or atual["chave"] != arvore:
            atual = {"chave": arvore, "linhas": []}
            arvores.append(atual)
            linha_atual = None
        if r != linha_atual:
            atual["linhas"].append([])
            linha_atual = r
        atual["linhas"][-1].append({"chave": info["chave"], "nome": info["nome"], "icone": DDI + info["icone"], "texto": txt(c, r, k + 1)})
    return [{"tipo": "runas", "arvores": arvores}]


def pagina_setups(c):
    cab = next(r for (r, k), v in sorted(c.items()) if k == 0 and v["texto"] == "Build Concept")
    colunas = {k: v["texto"] for (r, k), v in c.items() if r == cab}
    grupos = []
    for r in range(cab - 1, max(r for r, _ in c) + 1):
        a = txt(c, r, 0)
        if r != cab and a.endswith(":") and not txt(c, r, 2):
            grupos.append({"titulo": a.rstrip(":"), "setups": []})
            continue
        if r <= cab or not txt(c, r, 2):
            continue
        if not grupos:
            grupos.append({"titulo": "", "setups": []})
        grupos[-1]["setups"].append({
            "nome": a.strip(),
            "runas": cel(c, r, 2), "itens": cel(c, r, 3), "exemplo": cel(c, r, 4), "comentario": cel(c, r, 6),
        })
    return [{"tipo": "setups", "colunas": {"runas": colunas.get(2, ""), "itens": colunas.get(3, ""), "exemplo": colunas.get(4, ""), "comentario": colunas.get(6, "")}, "grupos": grupos}]


def pagina_criadores(c):
    """Tabelas (cabeçalho "Region, Name, ..."), seções que reaproveitam o último cabeçalho, textos e listas de links."""
    vazio = lambda v: v is None or v["texto"] in ("", "---") and not v["links"]
    blocos, colunas, tabela = [], None, None
    ultima = max(r for r, _ in c)
    r = 0
    while r <= ultima:
        a, b = txt(c, r, 0), txt(c, r, 1)
        if a == "Region":
            colunas = [(k, c[(r, k)]["texto"]) for k in range(0, 9) if txt(c, r, k)]
            if tabela is not None and not tabela["colunas"]:
                tabela["colunas"] = [n for _, n in colunas]
            # Créditos ficam ao lado da primeira tabela (colunas J e K).
            if txt(c, r, 9) and txt(c, r - 1, 9):
                cred, k = [], r + 1
                while txt(c, k, 9):
                    cred.append([cel(c, k, 9), cel(c, k, 10)])
                    k += 1
                blocos.append({"tipo": "tabela", "titulo": txt(c, r - 1, 9), "colunas": [txt(c, r, 9), txt(c, r, 10)], "linhas": cred, "lado": True})
        elif a and b and colunas:
            if tabela is None:
                tabela = {"tipo": "tabela", "titulo": "", "colunas": [n for _, n in colunas], "linhas": []}
                blocos.append(tabela)
            tabela["linhas"].append([None if vazio(cel(c, r, k)) else cel(c, r, k) for k, _ in colunas])
        elif a and not b:
            seguinte_a, seguinte_b = txt(c, r + 1, 0), txt(c, r + 1, 1)
            if seguinte_a == "Region" or (seguinte_a and seguinte_b and a.endswith(":")):
                tabela = {"tipo": "tabela", "titulo": a.rstrip(":"), "colunas": [n for _, n in colunas] if colunas and seguinte_a != "Region" else [], "linhas": []}
                blocos.append(tabela)
            elif a.endswith(":") and seguinte_a and not seguinte_b:
                itens, k = [], r + 1
                while txt(c, k, 0) and not txt(c, k, 1):
                    itens.append(cel(c, k, 0))
                    k += 1
                blocos.append({"tipo": "lista", **cel(c, r, 0), "itens": itens})
                tabela = None
                r = k
                continue
            else:
                blocos.append({"tipo": "texto", **cel(c, r, 0)})
                tabela = None
        r += 1
    # Créditos depois das tabelas de criadores.
    cred = [b for b in blocos if b.get("lado")]
    return [b for b in blocos if not b.get("lado")] + cred


def gerar(xlsx=None):
    mapa = json.loads((DEST / "imagens.json").read_text(encoding="utf-8"))
    if xlsx is None:
        xlsx = baixar(f"https://docs.google.com/spreadsheets/d/{PLANILHA}/export?format=xlsx")
    p = Planilha(xlsx)
    c = {k: aba(g) for k, g in ABAS.items()}
    aba_itens = next(n for n in p.abas if n.startswith("Itemization"))
    aba_runas = next(n for n in p.abas if n.startswith("Rune"))
    imgs_itens, imgs_runas = p.imagens(aba_itens), p.imagens(aba_runas)
    arvore_de = {r["key"]: arv["key"] for arv in json.loads(baixar(f"https://ddragon.leagueoflegends.com/cdn/{VER}/data/en_US/runesReforged.json"))
                 for slot in arv["slots"] for r in slot["runes"]}
    desconhecidas = sorted({m for _, k, _, m, _ in imgs_itens + imgs_runas if m not in mapa and k in (0, 2, 4, 6)})
    paginas = [
        {"id": "sobre", "blocos": pagina_sobre(c["sobre"])},
        {"id": "itens", "blocos": pagina_itens(c["itens"], imgs_itens, mapa)},
        {"id": "runas", "blocos": pagina_runas(c["runas"], imgs_runas, mapa, arvore_de)},
        {"id": "setups", "blocos": pagina_setups(c["setups"])},
        {"id": "criadores", "blocos": pagina_criadores(c["criadores"])},
    ]
    return paginas, desconhecidas


if __name__ == "__main__":
    import sys
    xlsx = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else None
    paginas, desconhecidas = gerar(xlsx)
    (DEST / "paginas.json").write_text(json.dumps(paginas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("Páginas:", ", ".join(f"{p['id']} ({len(p['blocos'])} blocos)" for p in paginas))
    if desconhecidas:
        print("Imagens sem identificação (acrescente em imagens.json):", desconhecidas)
