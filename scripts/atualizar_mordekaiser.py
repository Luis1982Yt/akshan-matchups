"""Baixa a planilha de matchups do Meowdekaiser e os dados do Data Dragon e gera src/guias/mordekaiser/matchups.json.

Precisa de internet. Rode `python scripts/atualizar_mordekaiser.py` e depois `python scripts/build.py`.
As outras abas da planilha viram páginas do guia (scripts/paginas_mordekaiser.py -> paginas.json).
O texto das notas não é alterado: só é separado em partes (runas, itens, seções) para mostrar melhor.
"""
import csv
import io
import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "src" / "guias" / "mordekaiser"
PLANILHA = "1BVH44IPxZNBQshDf90XZRJbfKvavVCUIIo_boyBVF8o"
ABA_MATCHUPS = "1560260169"
VER = "16.20.1"
DD = f"https://ddragon.leagueoflegends.com/cdn/{VER}"

# Nomes da planilha que não batem direto com o Data Dragon.
APELIDO_CAMPEAO = {"ganglank": "Gangplank"}
APELIDO_ITEM = {
    "rocketbelt": "Hextech Rocketbelt",
    "mercury treads": "Mercury's Treads",
    "spirit's visage": "Spirit Visage",
    "rylai's": "Rylai's Crystal Scepter",
    "liandry's": "Liandry's Torment",
    "zhonya's": "Zhonya's Hourglass",
    "nashor's": "Nashor's Tooth",
    "mecury's treads": "Mercury's Treads",
}
SECOES = {"Enemy Cooldowns", "Early Game", "How to trade", "What to watch out for", "Tips", "Mini Rant"}


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req).read().decode("utf-8")


def chave(s):
    return re.sub(r"[^a-z0-9]", "", s.lower().replace("&", "and"))


IMG_RUNA = "https://ddragon.leagueoflegends.com/cdn/img/perk-images/"
# Runas que saíram do jogo mas ainda aparecem nas planilhas (o Data Dragon guarda a imagem).
RUNAS_ANTIGAS = {"legendtenacity": IMG_RUNA + "Styles/Precision/LegendTenacity/LegendTenacity.png",
                 "phaserush": IMG_RUNA + "Styles/Sorcery/PhaseRush/PhaseRush.png"}
# Fragmentos (não vêm no runesReforged): o primeiro padrão que bater no nome escrito na planilha.
FRAGMENTOS = [(r"adap|adp", "StatModsAdaptiveForceIcon"), (r"attack\s*speed", "StatModsAttackSpeedIcon"),
              (r"ability\s*haste|cdr", "StatModsCDRScalingIcon"), (r"move(ment)?\s*speed|\bms\b", "StatModsMovementSpeedIcon"),
              (r"scaling\s*health|health\s*scaling", "StatModsHealthScalingIcon"), (r"tenacity|slow\s*resist", "StatModsTenacityIcon"),
              (r"health|\bhp\b", "StatModsHealthPlusIcon")]


def icone_fragmento(nome):
    return next((f"{IMG_RUNA}StatMods/{arq}.png" for padrao, arq in FRAGMENTOS if re.search(padrao, nome, re.I)), None)


def montar_icones(itens, runas):
    por_item = {}
    for k, v in itens.items():
        if v.get("gold", {}).get("purchasable"):
            por_item.setdefault(chave(v["name"]), (v["name"], f"{DD}/img/item/{k}.png"))
    por_runa = dict(RUNAS_ANTIGAS)
    for arvore in runas:
        for slot in arvore["slots"]:
            for r in slot["runes"]:
                icone = "https://ddragon.leagueoflegends.com/cdn/img/" + r["icon"]
                por_runa[chave(r["name"])] = icone
                por_runa[chave(r["name"].split(":")[-1])] = icone
    return por_item, por_runa


def icone_item(nome, por_item):
    base = re.sub(r"\s+rush$", "", nome.strip(), flags=re.I)
    alvo = APELIDO_ITEM.get(base.lower(), base)
    k = chave(alvo)
    if k in por_item:
        return por_item[k][1]
    achados = [v for kk, v in por_item.items() if kk.startswith(k) and len(k) >= 5]
    return achados[0][1] if len(achados) == 1 else None


def partes_item(linha, por_item):
    """'Bramble Vest Rush -> Boots' vira [[{Bramble Vest Rush}], [{Boots}]]; '/' separa alternativas."""
    passos = []
    for passo in re.split(r"\s*->\s*", linha):
        alts = [a.strip() for a in re.split(r"\s+/\s+", passo) if a.strip()]
        if alts:
            passos.append([{"nome": a, "icone": icone_item(a, por_item)} for a in alts])
    return passos


def ler_build(texto, por_item):
    linhas, buf, fecha = [], [], None
    for bruta in texto.split("\n"):
        l = bruta.strip()
        if fecha:
            buf.append(l)
            if l.endswith(fecha):
                tipo = "motivo" if fecha == ")" else "nota"
                txt = " ".join(x for x in buf if x)
                if tipo == "motivo" and linhas and linhas[-1]["tipo"] == "item" and not linhas[-1].get("motivo"):
                    linhas[-1]["motivo"] = txt
                else:
                    linhas.append({"tipo": "nota", "texto": txt})
                buf, fecha = [], None
            continue
        if not l:
            continue
        if re.fullmatch(r"-{2,}", l):
            linhas.append({"tipo": "sep"})
        elif l[0] in "([":
            fecha = ")" if l[0] == "(" else "]"
            buf = [l]
            if l.endswith(fecha) and len(l) > 1:
                fecha = None
                if l[0] == "(" and linhas and linhas[-1]["tipo"] == "item" and not linhas[-1].get("motivo"):
                    linhas[-1]["motivo"] = l
                else:
                    linhas.append({"tipo": "nota", "texto": l})
                buf = []
        elif l.endswith(":"):
            linhas.append({"tipo": "rotulo", "texto": l})
        else:
            linhas.append({"tipo": "item", "texto": l, "passos": partes_item(l, por_item)})
    if buf:
        linhas.append({"tipo": "nota", "texto": " ".join(buf)})
    return linhas


def ler_runas(texto, por_runa):
    grupos = [g for g in re.split(r"\n\s*\n", texto.strip()) if g.strip()]
    nomes = ["Principal", "Secundária", "Fragmentos"]
    out = []
    for i, g in enumerate(grupos):
        sep = r"\s*\+\s*|\n" if i >= 2 else r"\s*->\s*|\n"
        pecas = [p.strip(" ->+") for p in re.split(sep, g) if p.strip(" ->+")]
        if i == 1:
            pecas = [q.strip() for p in pecas for q in re.split(r"\s*\+\s*", p) if q.strip()]
        out.append({
            "rotulo": nomes[i] if i < len(nomes) else "",
            "pecas": [{"nome": p, "icone": icone_fragmento(p) if i == 2 else por_runa.get(chave(p))} for p in pecas],
        })
    return out


def ler_secoes(texto):
    secoes, atual = [], None
    for l in texto.split("\n"):
        t = l.strip()
        # "Early Game:" sozinho na linha (no espelho do Mordekaiser vem sem os dois pontos) ou "Early Game - texto".
        cab = re.match(r"^(" + "|".join(map(re.escape, SECOES)) + r")(?::?\s*$|\s+-\s+(.+)$)", t)
        if cab:
            atual = {"titulo": cab.group(1), "linhas": [cab.group(2)] if cab.group(2) else []}
            secoes.append(atual)
        elif atual is None:
            atual = {"titulo": "", "linhas": [l]}
            secoes.append(atual)
        else:
            atual["linhas"].append(l)
    return [{"titulo": s["titulo"], "blocos": blocos(s["linhas"], s["titulo"] == "Enemy Cooldowns")} for s in secoes]


def blocos(linhas, tabela):
    if tabela:
        # Na ordem da planilha: uma linha solta entre as habilidades ("- Spiderling form") fica onde está.
        out = []

        def tabela_atual():
            if not out or out[-1]["tipo"] != "tabela":
                out.append({"tipo": "tabela", "linhas": []})
            return out[-1]["linhas"]
        for l in linhas:
            t = l.strip()
            if not t:
                continue
            m = re.match(r"^(.+?):\s*(.+)$", t)
            if m:
                tabela_atual().append([m.group(1).strip(), m.group(2).strip()])
            elif t.endswith(":"):
                tabela_atual().append([t[:-1], ""])
            elif out and out[-1]["tipo"] == "tabela" and not out[-1]["linhas"][-1][1]:
                out[-1]["linhas"][-1][1] = t
            elif out and out[-1]["tipo"] == "p":
                out[-1]["texto"] += " " + t
            else:
                out.append({"tipo": "p", "texto": t})
        return out
    out, grupo = [], []

    def fecha_grupo():
        if not grupo:
            return
        itens, cur = [], None
        for t in grupo:
            if t.startswith("-"):
                cur = [t.lstrip("- ").strip()]
                itens.append(cur)
            elif cur is not None:
                cur.append(t)
            else:
                itens.append([t])
                cur = itens[-1]
        for it in itens:
            texto = " ".join(it).strip()
            if not texto:
                continue
            eh_lista = grupo[0].startswith("-") or any(g.startswith("-") for g in grupo)
            if eh_lista:
                if out and out[-1]["tipo"] == "lista":
                    out[-1]["itens"].append(texto)
                else:
                    out.append({"tipo": "lista", "itens": [texto]})
            else:
                out.append({"tipo": "p", "texto": texto})
        grupo.clear()

    for l in linhas:
        t = l.strip()
        if not t:
            fecha_grupo()
        else:
            grupo.append(t)
    fecha_grupo()
    return out


def dificuldade(txt):
    m = re.search(r"(\d)\s*/\s*5", txt or "")
    return int(m.group(1)) if m else None


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    csv_txt = baixar(f"https://docs.google.com/spreadsheets/d/{PLANILHA}/export?format=csv&gid={ABA_MATCHUPS}")
    (DEST / "planilha.csv").write_text(csv_txt, encoding="utf-8", newline="\n")
    campeoes = json.loads(baixar(f"{DD}/data/pt_BR/champion.json"))["data"]
    itens = json.loads(baixar(f"{DD}/data/en_US/item.json"))["data"]
    runas = json.loads(baixar(f"{DD}/data/en_US/runesReforged.json"))
    por_item, por_runa = montar_icones(itens, runas)
    por_campeao = {}
    for c in campeoes.values():
        por_campeao[chave(c["id"])] = c
        por_campeao[chave(c["name"])] = c

    rows = list(csv.reader(io.StringIO(csv_txt)))
    inicios = [i for i, r in enumerate(rows) if r and r[0].startswith("c:")] + [len(rows)]
    matchups, sem_id = [], []
    for k in range(len(inicios) - 1):
        a, b = inicios[k], inicios[k + 1]

        def col(j):
            return [rows[i][j] for i in range(a, b) if len(rows[i]) > j and rows[i][j].strip()]

        nome_planilha = rows[a][1].strip() or rows[a][0][2:].strip()
        c = por_campeao.get(chave(APELIDO_CAMPEAO.get(chave(nome_planilha), nome_planilha)))
        if not c:
            sem_id.append(nome_planilha)
            continue
        c4 = col(4)
        runas_txt = [c4[i + 1] for i, v in enumerate(c4) if v.strip() == "Rune description:" and i + 1 < len(c4)]
        itens_grupos, rotulo = [], "Items vs."
        for v in col(7):
            if "\n" in v.strip():
                itens_grupos.append({"rotulo": rotulo, "linhas": ler_build(v, por_item)})
            else:
                rotulo = v.strip()
        c13 = col(13)
        tldr = []
        for v in c13:
            if "TL;DR" in v:
                tldr += [x.strip().lstrip("- ").strip() for x in v.split("\n")[1:] if x.strip()]
        gameplay = "\n\n".join(col(17))
        matchups.append({
            "nome": c["name"],
            "planilha": nome_planilha,
            "id": c["id"],
            "titulo": c["title"],
            "dificuldade": {
                "early": dificuldade(rows[a][13] if len(rows[a]) > 13 else ""),
                "mid": dificuldade(rows[a][14] if len(rows[a]) > 14 else ""),
                "late": dificuldade(rows[a][15] if len(rows[a]) > 15 else ""),
                "overall": dificuldade(rows[a][16] if len(rows[a]) > 16 else ""),
            },
            "tldr": tldr,
            "runas": [ler_runas(t, por_runa) for t in runas_txt],
            "itens": itens_grupos,
            "secoes": ler_secoes(gameplay),
        })
    saida = {
        "versao": VER,
        "fonte": {
            "planilha": f"https://docs.google.com/spreadsheets/d/{PLANILHA}/edit?gid={ABA_MATCHUPS}",
            "twitch": "https://www.twitch.tv/meowdekaiser_",
            "x": "https://x.com/Meowdekaiser",
        },
        "matchups": matchups,
    }
    (DEST / "matchups.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    sem_icone = sorted({p["nome"] for m in matchups for g in m["itens"] for l in g["linhas"] if l["tipo"] == "item" for passo in l["passos"] for p in passo if not p["icone"]})
    print(f"{len(matchups)} matchups gravados em {DEST / 'matchups.json'}")
    if sem_id:
        print("Sem campeão no Data Dragon:", sem_id)
    print("Itens sem ícone:", sem_icone)
    # Outras abas da planilha (introdução, itens, runas, setups, criadores) viram páginas do guia.
    import paginas_mordekaiser
    paginas, desconhecidas = paginas_mordekaiser.gerar()
    (DEST / "paginas.json").write_text(json.dumps(paginas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("Páginas:", ", ".join(p["id"] for p in paginas))
    if desconhecidas:
        print("Imagens sem identificação (acrescente em src/guias/mordekaiser/imagens.json):", desconhecidas)


if __name__ == "__main__":
    main()
