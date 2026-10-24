"""Monta a tabela de chromas do Akshan: para cada chroma, a cor, o nome e as texturas que trocam
no modelo 3D da skin-mãe (material do .glb -> PNG no CommunityDragon).

Uso: python chromas.py <pasta de trabalho com skinN/config.json de cada skin-mãe> > chromas.json

Chroma usa o mesmo modelo e as mesmas animações da skin-mãe; só as texturas mudam. O site
carrega os PNGs direto do CommunityDragon (liberado para outros sites).
"""
import json
import pathlib
import sys
import urllib.request

CD = "https://raw.communitydragon.org/latest/"
PASTA = pathlib.Path(sys.argv[1])
MAES = {1: "ciberpop", 10: "rosa-de-cristal", 21: "velho-oeste"}


def baixa(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read())


def texturas(num):
    """Textura padrão e por submalha de uma skin (ou chroma), como caminhos .tex."""
    d = baixa(f"{CD}game/data/characters/akshan/skins/skin{num}.bin.json")
    props = next(v["skinMeshProperties"] for v in d.values() if isinstance(v, dict) and "skinMeshProperties" in v)
    mats = {k: v for k, v in d.items() if isinstance(v, dict) and v.get("__type") == "StaticMaterialDef"}
    por_sub = {}
    for o in props.get("materialOverride", []):
        tex = o.get("texture")
        if not tex:
            m = mats.get(o.get("material") or o.get("Material") or "", {})
            cor = [s.get("texturePath", "") for s in m.get("samplerValues", []) if "_tx_cm" in s.get("texturePath", "").lower()]
            tex = cor[0] if cor else None
        if tex:
            por_sub[o["submesh"]] = tex
    return props["texture"], por_sub


def png(tex):
    return CD + "game/" + tex.lower().replace(".tex", ".png")


campeao = baixa(f"{CD}plugins/rcp-be-lol-game-data/global/pt_br/v1/champions/166.json")
campeao_en = {s["id"]: s for s in baixa(f"{CD}plugins/rcp-be-lol-game-data/global/default/v1/champions/166.json")["skins"]}
saida = {}
for skin in campeao["skins"]:
    mae = skin["id"] % 1000
    if mae not in MAES:
        continue
    cfg = json.loads((PASTA / f"skin{mae}" / "config.json").read_text(encoding="utf-8"))
    lista = []
    for ch in skin.get("chromas") or []:
        num = ch["id"] % 1000
        padrao, por_sub = texturas(num)
        troca = {"main": png(padrao)}
        for sub, chave in cfg["submesh_textura"].items():
            if sub in cfg["esconder"] or chave == "main" or sub not in por_sub:
                continue
            troca[chave] = png(por_sub[sub])
        en = next((c for c in campeao_en[skin["id"]].get("chromas", []) if c["id"] == ch["id"]), {})
        nome = ch["name"].split("(")[-1].rstrip(")")
        nome_en = en.get("name", "").split("(")[-1].rstrip(")") or nome
        lista.append({"num": num, "nome": nome, "nome_en": nome_en, "cores": ch.get("colors", []), "texturas": troca})
        print(f"{MAES[mae]} {num} {nome}: {len(troca)} textura(s)", file=sys.stderr)
    saida[MAES[mae]] = lista
print(json.dumps(saida, ensure_ascii=False))
