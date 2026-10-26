"""Baixa a planilha de matchups do Hachiragi (Illaoi) e gera src/guias/illaoi/matchups.json e paginas.json.

Precisa de internet. Rode `python scripts/atualizar_illaoi.py` e depois `python scripts/build.py`.
O texto vem da versão publicada de cada aba (no xlsx a dificuldade "2/3" vira data); as runas
principais de cada matchup e as capturas das runas gerais vêm das imagens do xlsx.
O texto das notas não é alterado: só é separado em partes (runas, itens, dicas) para mostrar melhor.
"""
import io
import json
import pathlib
import re
import urllib.request

from atualizar_mordekaiser import chave, icone_fragmento, montar_icones
from planilha_xlsx import Planilha, publicado

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "src" / "guias" / "illaoi"
IMAGENS = ROOT / "imagens" / "illaoi"  # publicadas junto com o site (ver .vercelignore)
PLANILHA = "1EuXpzDMShjT4s3NSScWqnzUxiqccPv-3kHufHNCEkTA"
ABAS = {"geral": 1789019044, "matchups": 0, "itens": 1905273951, "runas": 88247813, "dicas": 200779566}
VER = "16.20.1"
DD = f"https://ddragon.leagueoflegends.com/cdn/{VER}"

# Como o Hachiragi escreve os itens e runas -> nome no Data Dragon.
APELIDO_ITEM = {
    "dorans shield": "Doran's Shield", "tier 1 boots": "Boots", "boots": "Boots", "shojin": "Spear of Shojin",
    "executioners": "Executioner's Calling", "steraks": "Sterak's Gage", "iceborn": "Iceborn Gauntlet", "iceborne": "Iceborn Gauntlet",
    "jaksho": "Jak'Sho, The Protean", "plated steel caps": "Plated Steelcaps", "plated steelcaps": "Plated Steelcaps",
    "mercs": "Mercury's Treads", "mercury treads": "Mercury's Treads", "tear of goddess": "Tear of the Goddess",
    "deaths dance": "Death's Dance", "maw of malmortious": "Maw of Malmortius", "randuins omen": "Randuin's Omen", "randuins": "Randuin's Omen",
    "anathemas chains": "Anathema's Chains", "black clever": "Black Cleaver", "cleaver": "Black Cleaver", "kaenic": "Kaenic Rookern",
    "thornmail": "Thornmail", "bramble": "Bramble Vest", "titanic": "Titanic Hydra", "hydra": "Titanic Hydra", "dead mans": "Dead Man's Plate",
    "frozen heart": "Frozen Heart", "spirit visage": "Spirit Visage", "sundered": "Sundered Sky", "steelcaps": "Plated Steelcaps",
    "qss": "Quicksilver Sash", "swifties": "Boots of Swiftness",
}
APELIDO_RUNA = {"mannaflow band": "Manaflow Band", "grasp": "Grasp of the Undying", "comet": "Arcane Comet", "pom": "Presence of Mind", "fleet": "Fleet Footwork",
                "phase rush": "Stormraider's Surge", "nullifying orb": "Axiom Arcanist", "tempo": "Lethal Tempo", "pta": "Press the Attack"}
APELIDO_CAMPEAO = {"drmundo": "DrMundo", "chogath": "Chogath", "ksante": "KSante", "kled": "Kled", "wukong": "MonkeyKing", "nunu": "Nunu"}
KEYSTONE = {  # md5 da imagem pequena da coluna Runes -> runa (Conquistador, Garra, Cometa, Agilidade)
    "f7b1f7c143964496e2f2bea66dd8f50a": "Conqueror", "b5d96359ca631269351c6d6fcdad6ea9": "GraspOfTheUndying",
    "dbaff56b6c06916418bb5d1503134e1f": "ArcaneComet", "2cc270b9cba3ec734e55fb94e3504a9a": "FleetFootwork",
}


def baixar(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()


def aba(gid):
    return publicado(baixar(f"https://docs.google.com/spreadsheets/d/{PLANILHA}/htmlview/sheet?headers=false&gid={gid}").decode("utf-8"))


def txt(c, r, k):
    v = c.get((r, k))
    return v["texto"] if v else ""


def cel(c, r, k):
    v = c.get((r, k))
    return {"texto": v["texto"], "links": v["links"]} if v and (v["texto"] or v["links"]) else None


def icone_item(nome, por_item):
    base = nome.strip().lower().replace("’", "'")
    alvo = APELIDO_ITEM.get(base) or APELIDO_ITEM.get(chave(base)) or nome
    k = chave(alvo)
    if k in por_item:
        return por_item[k][1]
    achados = [v for kk, v in por_item.items() if kk.startswith(k) and len(k) >= 4]
    return achados[0][1] if len(achados) == 1 else None


def build(linha, por_item):
    """'Dorans Shield > Boots > Shojin/Sundered Sky' vira passos com alternativas."""
    passos = []
    for passo in re.split(r"\s*>\s*", linha.strip()):
        # "/" e "," separam alternativas ("Iceborn / Jaksho, Kaenic Rookern.").
        alts = [a.strip(" .") for a in re.split(r"\s*[/,]\s*", passo) if a.strip(" .")]
        if alts:
            passos.append([{"nome": a, "icone": icone_item(a, por_item)} for a in alts])
    return passos


ARVORES = r"^(Precision|Resolve|Sorcery|Domination|Inspiration)\s*-\s*"
FRAGMENTO = re.compile(r"adp|adaptive|health|shard|attack speed|ability haste|movement speed|tenacity and|armor|magic res", re.I)


def runa_conhecida(nome, por_runa):
    return por_runa.get(chave(APELIDO_RUNA.get(nome.lower(), nome)))


def separa_runas(peca, por_runa):
    """'Demolish Second Wind' (faltou a vírgula) vira as duas runas, se cada metade for uma runa."""
    if runa_conhecida(peca, por_runa):
        return [peca]
    ps = peca.split()
    for i in range(1, len(ps)):
        a, b = " ".join(ps[:i]), " ".join(ps[i:])
        if runa_conhecida(a, por_runa) and runa_conhecida(b, por_runa):
            return [a, b]
    return [peca]


def runas(texto, por_runa):
    """'Precision- Conqueror, PoM, ...' / 'Resolve-Demolish, Second Wind' / 'Adp force, ...' -> principal, secundária, fragmentos.
    Cada linha que começa com o nome da árvore abre um grupo; a linha de fragmentos é reconhecida pelo conteúdo."""
    grupos = []
    for linha in [l.strip() for l in texto.split("\n") if l.strip()]:
        if re.match(ARVORES, linha):
            grupos.append({"tipo": "arvore", "texto": re.sub(ARVORES, "", linha)})
        elif FRAGMENTO.search(linha):
            if grupos and grupos[-1]["tipo"] == "frag":
                grupos[-1]["texto"] += ", " + linha
            else:
                grupos.append({"tipo": "frag", "texto": linha})
        elif grupos:
            grupos[-1]["texto"] += ", " + linha
    out, n = [], 0
    for g in grupos:
        rotulo = "Fragmentos" if g["tipo"] == "frag" else ["Principal", "Secundária"][min(n, 1)]
        n += g["tipo"] == "arvore"
        pecas = []
        for p in [x.strip(" .") for x in g["texto"].split(",") if x.strip(" .")]:
            for alt in [a.strip() for a in p.split("/") if a.strip()]:
                for nome in ([alt] if rotulo == "Fragmentos" else separa_runas(alt, por_runa)):
                    pecas.append({"nome": nome, "icone": icone_fragmento(nome) if rotulo == "Fragmentos" else runa_conhecida(nome, por_runa)})
        out.append({"rotulo": rotulo, "pecas": pecas})
    return out


def dificuldade(t):
    """'2/3' é entre 2 e 3: a nota vai para cima, o texto fica como o autor escreveu."""
    ns = [int(n) for n in re.findall(r"\d", t or "")]
    return (max(ns) if ns else None), (t or "").strip()


def gerar_matchups(c, cr, xl, por_item, por_runa, campeoes):
    cab = next(r for (r, k), v in sorted(c.items()) if k == 0 and v["texto"] == "Champs")
    # Runas específicas por campeão (outra aba): duas opções, colunas E e I.
    especificas = {}
    for (r, k), v in cr.items():
        if k == 0 and r > 4 and v["texto"] not in ("Champs",):
            especificas[chave(v["texto"])] = [t for t in (txt(cr, r, 4), txt(cr, r, 8)) if t]
    keystones = {}
    for r, k, _o, md5, _b in xl.imagens(next(n for n in xl.abas if n.startswith("Matchup"))):
        if k in (3, 4) and md5 in KEYSTONE:
            keystones.setdefault(r, []).append(KEYSTONE[md5])
    runas_dd = {}
    for arv in json.loads(baixar(f"{DD}/data/en_US/runesReforged.json")):
        for s in arv["slots"]:
            for ru in s["runes"]:
                runas_dd[ru["key"]] = ru
    matchups, sem_id = [], []
    for r in range(cab + 1, max(r for r, _ in c) + 1):
        nome = txt(c, r, 0)
        if not nome:
            continue
        k = chave(nome)
        ch = campeoes.get(APELIDO_CAMPEAO.get(k, k).lower()) or campeoes.get(k)
        if not ch:
            sem_id.append(nome)
            continue
        nota, nota_txt = dificuldade(txt(c, r, 2))
        opcoes = especificas.get(k) or []
        if opcoes:
            rs = [runas(o, por_runa) for o in opcoes]
        else:  # sem runas específicas: só a principal, pela imagem
            rs = [[{"rotulo": "Principal", "pecas": [{"nome": runas_dd[x]["name"], "icone": "https://ddragon.leagueoflegends.com/cdn/img/" + runas_dd[x]["icon"]}]}] for x in keystones.get(r, [])]
        itens_txt = txt(c, r, 5)
        dicas = txt(c, r, 6)
        matchups.append({
            "nome": ch["name"], "planilha": nome, "id": ch["id"], "titulo": ch["title"],
            "dificuldade": {"overall": nota, "texto": nota_txt},
            "tldr": [],
            "runas": rs,
            "itens": [{"rotulo": "Items vs.", "linhas": [{"tipo": "item", "texto": itens_txt, "passos": build(itens_txt, por_item)}]}] if itens_txt else [],
            "secoes": [{"titulo": "Tips", "blocos": [{"tipo": "p", "texto": p.strip()} for p in re.split(r"\n\s*\n", dicas) if p.strip()]}] if dicas else [],
        })
    return matchups, sem_id


def gerar_paginas(cg, c, ci, cd, xl, por_item):
    # Geral: apresentação, redes do autor e criadores de conteúdo.
    intro = next(v for (r, k), v in sorted(cg.items()) if k == 0 and len(v["texto"]) > 200)
    redes = [{"texto": f"{txt(cg, r, 8)}: {txt(cg, r, 9)}" if txt(cg, r, 9) else txt(cg, r, 8), "links": cg[(r, 8)]["links"]}
             for r in range(5, 15) if txt(cg, r, 8) and txt(cg, r, 8) != "Socials"]
    tit_cri = max(r for (r, k), v in cg.items() if k == 0 and v["texto"].endswith("Content Creators"))
    criadores = []
    for r in range(tit_cri + 1, max(r for r, _ in cg) + 1):
        if txt(cg, r, 0) and txt(cg, r, 1):
            links = [l for rr in (r, r + 1) for l in (cg.get((rr, 8)) or {}).get("links", [])]
            criadores.append([{"texto": txt(cg, r, 0), "links": []}, {"texto": txt(cg, r, 1), "links": []},
                              *[{"texto": l["texto"], "links": [l]} for l in links]])
    explica = [(txt(c, r, 0), txt(c, r, 1)) for r in range(0, 12) if txt(c, r, 0) and len(txt(c, r, 1)) > 100]
    geral = [{"tipo": "texto", "titulo": txt(cg, 0, 0), "texto": intro["texto"], "links": []},
             {"tipo": "lista", "texto": "Socials", "links": [], "itens": redes}]
    geral += [{"tipo": "texto", "titulo": t, "texto": x, "links": []} for t, x in explica if t.startswith("Matchup")]
    geral.append({"tipo": "pessoas", "titulo": txt(cg, tit_cri, 0), "pessoas": [
        {"nome": p[0]["texto"], "texto": p[1]["texto"], "links": [l for x in p[2:] for l in x["links"]]} for p in criadores]})

    # Itens: texto geral, iniciais/bons/situacionais/divertidos (aba Matchups) e a explicação de cada um (aba Items).
    blocos_itens = [{"tipo": "texto", "titulo": t, "texto": x, "links": []} for t, x in explica if t.startswith("Items")]
    blocos_itens += [{"tipo": "texto", "titulo": txt(ci, r, 0), "texto": txt(ci, r, 1), "links": []} for r in range(0, 6) if len(txt(ci, r, 1)) > 100]
    listas = []
    for r in range(10, 24):
        rot = txt(c, r, 0) or (listas and listas[-1]["titulo"])
        if not rot or rot.startswith("Check"):
            continue
        nomes = [n.strip() for n in re.split(r"-{3,}", txt(c, r, 1)) if n.strip()]
        if not nomes:
            continue
        if not listas or listas[-1]["titulo"] != rot:
            listas.append({"titulo": rot, "itens": []})
        listas[-1]["itens"] += [{"nome": n, "icone": icone_item(n, por_item), "texto": txt(c, r, 2) if len(nomes) == 1 else ""} for n in nomes]
    blocos_itens.append({"tipo": "pecas", "grupos": listas})
    grupos, atual = [], None
    for r in range(4, max(r for r, _ in ci) + 1):
        a, b = txt(ci, r, 0), txt(ci, r, 1)
        if a and not b:
            atual = {"titulo": a, "itens": []}
            grupos.append(atual)
        elif a and b and atual is not None:
            atual["itens"].append({"nome": a, "icone": icone_item(a.split("/")[0], por_item), "texto": b})
    blocos_itens.append({"tipo": "pecas", "grupos": grupos})

    # Runas: explicação e as capturas das páginas de runas gerais (imagens grandes da aba Matchups).
    IMAGENS.mkdir(parents=True, exist_ok=True)
    capturas = []
    from PIL import Image
    for n, (r, k, _o, md5, b) in enumerate([i for i in xl.imagens(next(n for n in xl.abas if n.startswith("Matchup"))) if i[1] == 7]):
        # O nome leva o md5 da imagem original: só grava de novo quando o autor troca a captura.
        arq = IMAGENS / f"runas-gerais-{n + 1}-{md5[:8]}.jpg"
        im = Image.open(io.BytesIO(b)).convert("RGB")
        im.thumbnail((1000, 1000))
        if not arq.exists():
            for velho in IMAGENS.glob(f"runas-gerais-{n + 1}-*.jpg"):
                velho.unlink()
            im.save(arq, "JPEG", quality=82, optimize=True)
        capturas.append({"src": f"imagens/illaoi/{arq.name}", "largura": im.width, "altura": im.height})
    blocos_runas = [{"tipo": "texto", "titulo": t, "texto": x, "links": []} for t, x in explica if t.startswith("Runes")]
    blocos_runas.append({"tipo": "imagens", "titulo": txt(c, 0, 8) or "General Runes", "imagens": capturas})

    # Dicas e mecânicas: título (com o vídeo, quando tem) e explicação.
    dicas = []
    for r in range(1, max(r for r, _ in cd) + 1):
        a, b = cel(cd, r, 0), cel(cd, r, 1)
        if a and b:
            dicas.append({"titulo": a, "texto": b})
    blocos_dicas = [{"tipo": "texto", "titulo": txt(cd, 0, 0), "texto": txt(cd, 1, 0), "links": []}, {"tipo": "dicas", "itens": dicas}]
    return [
        {"id": "geral", "blocos": geral},
        {"id": "itens", "blocos": blocos_itens},
        {"id": "runas", "blocos": blocos_runas},
        {"id": "dicas", "blocos": blocos_dicas},
    ]


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    abas = {k: aba(g) for k, g in ABAS.items()}
    xl = Planilha(baixar(f"https://docs.google.com/spreadsheets/d/{PLANILHA}/export?format=xlsx"))
    itens = json.loads(baixar(f"{DD}/data/en_US/item.json"))["data"]
    runas_dd = json.loads(baixar(f"{DD}/data/en_US/runesReforged.json"))
    por_item, por_runa = montar_icones(itens, runas_dd)
    campeoes = {}
    for ch in json.loads(baixar(f"{DD}/data/pt_BR/champion.json"))["data"].values():
        campeoes[ch["id"].lower()] = ch
        campeoes[chave(ch["name"])] = ch
    matchups, sem_id = gerar_matchups(abas["matchups"], abas["runas"], xl, por_item, por_runa, campeoes)
    saida = {"versao": VER, "fonte": {"planilha": f"https://docs.google.com/spreadsheets/d/{PLANILHA}/edit?gid=0"}, "matchups": matchups}
    (DEST / "matchups.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    paginas = gerar_paginas(abas["geral"], abas["matchups"], abas["itens"], abas["dicas"], xl, por_item)
    (DEST / "paginas.json").write_text(json.dumps(paginas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    sem_icone = sorted({p["nome"] for m in matchups for g in m["itens"] for l in g["linhas"] for passo in l["passos"] for p in passo if not p["icone"]})
    sem_runa = sorted({p["nome"] for m in matchups for o in m["runas"] for g in o if g["rotulo"] != "Fragmentos" for p in g["pecas"] if not p["icone"]})
    sem_runa = [x for x in sem_runa if x != "Legend Tenacity"]  # runa que saiu do jogo: fica só o nome
    print(f"{len(matchups)} matchups gravados em {DEST / 'matchups.json'}; páginas: {', '.join(p['id'] for p in paginas)}")
    if sem_id:
        print("Sem campeão no Data Dragon:", sem_id)
    print("Itens sem ícone:", sem_icone)
    print("Runas sem ícone:", sem_runa)


if __name__ == "__main__":
    main()
