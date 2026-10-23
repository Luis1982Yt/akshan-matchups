"""Gera o .glb de uma skin do Akshan direto dos dados do jogo.

Uso: python skin3d.py <número da skin> <Akshan.wad.client> <pasta de trabalho> <saida.glb>

Lê a configuração da skin (skinN.bin.json) e das animações (animations/skinN.bin.json) no
CommunityDragon, extrai esqueleto, malha e animações do .wad da instalação do LoL, baixa as
texturas em PNG do CommunityDragon e chama o lol2glb.py com a configuração montada.
"""
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

import xxhash

from wad import extrai, ler_wad

N, WAD, PASTA, SAIDA = int(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3]), pathlib.Path(sys.argv[4])
PASTA.mkdir(parents=True, exist_ok=True)
CD = "https://raw.communitydragon.org/latest/game/"

# Clipe no site -> nome do arquivo de animação no jogo.
CLIPES = {
    "idle": "akshan_idle1.anm", "idle_var": "idle1_var1.anm", "dance_intro": "dance_intro.anm", "dance": "dance_loop.anm",
    "laugh": "laugh.anm", "taunt_intro": "taunt_intro.anm", "taunt": "taunt_cycle.anm", "attack1": "attack1.anm",
    "attack2": "attack2.anm", "crit": "akshan_base_crit.anm", "crit_to_idle": "crit_to_idle.anm", "recall": "recall.anm",
}


def baixa(url, binario=False):
    dados = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()
    return dados if binario else dados.decode("utf-8")


skin = json.loads(baixa(f"{CD}data/characters/akshan/skins/skin{N}.bin.json"))
anims = baixa(f"{CD}data/characters/akshan/animations/skin{N}.bin.json")

props = next(v["skinMeshProperties"] for v in skin.values() if isinstance(v, dict) and "skinMeshProperties" in v)
materiais = {k: v for k, v in skin.items() if isinstance(v, dict) and v.get("__type") == "StaticMaterialDef"}


def textura_do_material(nome):
    """Num material com vários mapas, fica a textura de cor (o *_tx_cm)."""
    m = materiais.get(nome, {})
    caminhos = [s.get("texturePath", "") for s in m.get("samplerValues", [])]
    cor = [c for c in caminhos if "_tx_cm" in c.lower()]
    return cor[0] if cor else None


texturas, submesh_textura = {}, {}


def registra(caminho_tex):
    chave = pathlib.Path(caminho_tex).stem.lower()
    if chave not in texturas:
        png = caminho_tex.lower().replace(".tex", ".png")
        destino = PASTA / f"{chave}.png"
        if not destino.exists():
            destino.write_bytes(baixa(CD + png, binario=True))
        texturas[chave] = (destino.name, "body" in chave or chave.endswith(f"skin{N}_tx_cm") or chave.endswith(f"skin{N:02d}_tx_cm"))
    return chave


padrao = registra(props["texture"])
for o in props.get("materialOverride", []):
    tex = o.get("texture") or textura_do_material(o.get("material") or o.get("Material") or "")
    if tex:
        submesh_textura[o["submesh"]] = registra(tex)
# As submalhas sem override usam a textura padrão da skin.
texturas = {"main": texturas[padrao], **{k: v for k, v in texturas.items() if k != padrao}}
submesh_textura = {s: ("main" if k == padrao else k) for s, k in submesh_textura.items()}
esconder = [x for x in re.split(r"[,\s]+", props.get("initialSubmeshToHide", "")) if x]

# Animações: o caminho de cada arquivo vem do grafo de animação da skin.
caminhos_anm = sorted(set(re.findall(r'"([^"]*\.anm)"', anims, re.I)))
por_nome = {}
for c in caminhos_anm:
    por_nome.setdefault(c.lower().split("/")[-1], c)

f, ent = ler_wad(WAD)
extrair = {props["skeleton"]: None, props["simpleSkin"]: None}
animacoes = []
for clipe, arquivo in CLIPES.items():
    if arquivo in por_nome:
        extrair[por_nome[arquivo]] = None
        animacoes.append([clipe, arquivo])
    else:
        print("sem animação na skin:", clipe, arquivo)
for caminho in extrair:
    h = xxhash.xxh64(caminho.lower().encode()).intdigest()
    if h not in ent:
        raise SystemExit(f"não achei no .wad: {caminho}")
    (PASTA / caminho.lower().split("/")[-1]).write_bytes(extrai(f, ent[h]))

config = {
    "skl": props["skeleton"].lower().split("/")[-1], "skn": props["simpleSkin"].lower().split("/")[-1],
    "texturas": texturas, "submesh_textura": submesh_textura, "esconder": esconder, "animacoes": animacoes,
}
(PASTA / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(config, ensure_ascii=False)[:600])
subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name("lol2glb.py")), str(PASTA), str(SAIDA), str(PASTA / "config.json")], check=True)
