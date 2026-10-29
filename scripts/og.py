"""Gera og.jpg (1200x630), a imagem que aparece quando o link do site é compartilhado.

Marca do BattleMatch (ícone de scripts/icone_marca.py e o nome) à esquerda e todos os guias do src/guias.json: uma faixa da splash de cada campeão (Data Dragon) com o nome,
a rota e o número de matchups. Precisa de internet para baixar as splashes. Rode de novo quando entrar
ou sair um guia: python scripts/og.py
"""
import io
import json
import pathlib
import re
import urllib.request

from PIL import Image, ImageDraw, ImageFont

from icone_marca import FIO, LIMAO, desenha

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
W, H = 1200, 630
FUNDO, CREME, BAIXO = (14, 15, 19), (242, 242, 238), (160, 165, 178)
# Onde fica o rosto na splash centralizada (fração da largura), para a faixa estreita não cortar a cabeça.
ROSTO = {"Akshan": .45, "Mordekaiser": .5, "Illaoi": .47, "Kayle": .73, "Fiora": .52, "K'Sante": .5}


def fonte(arquivo, tam, peso=None):
    f = ImageFont.truetype(str(SRC / "fonts" / arquivo), tam)
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def n_matchups(cfg):
    pasta = SRC / cfg["dados"]
    if cfg["formato"] == "simples":
        bruto = (pasta / "rows.js").read_text(encoding="utf-8").strip().rstrip(";")
        return len(json.loads(re.sub(r",\s*\]$", "]", bruto)))
    return len(json.loads((pasta / "matchups.json").read_text(encoding="utf-8"))["matchups"])


def splash(campeao):
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/centered/{campeao}_0.jpg"
    with urllib.request.urlopen(url, timeout=30) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


guias = [g for g in json.loads((SRC / "guias.json").read_text(encoding="utf-8")) if not g.get("oculto")]
img = Image.new("RGB", (W, H), FUNDO)
d = ImageDraw.Draw(img)

# Faixas das splashes à direita, uma por guia, separadas por um fio dourado.
x0, larg = 560, (W - 560) // len(guias)
for i, g in enumerate(guias):
    s = splash(g.get("id_campeao", g["campeao"]))
    s = s.resize((round(s.width * H / s.height), H), Image.LANCZOS)
    centro = round(s.width * ROSTO.get(g["campeao"], .5))
    faixa = s.crop((centro - larg // 2, 0, centro - larg // 2 + larg, H))
    # Escurece embaixo para o nome ficar legível.
    sombra = Image.new("L", (larg, H), 0)
    ds = ImageDraw.Draw(sombra)
    for y in range(H // 2, H):
        ds.line([(0, y), (larg, y)], fill=int(215 * ((y - H // 2) / (H // 2)) ** 1.4))
    faixa.paste(Image.new("RGB", (larg, H), FUNDO), (0, 0), sombra)
    img.paste(faixa, (x0 + i * larg, 0))
    if i:
        d.line([(x0 + i * larg, 0), (x0 + i * larg, H)], fill=FIO, width=2)

# A primeira faixa some no fundo escuro pela esquerda.
mascara = Image.new("L", (120, H), 0)
dm = ImageDraw.Draw(mascara)
for x in range(120):
    dm.line([(x, 0), (x, H)], fill=int(255 * (1 - x / 120) ** 1.5))
img.paste(Image.new("RGB", (120, H), FUNDO), (x0, 0), mascara)

# Nome, rota e número de matchups embaixo de cada faixa (o nome encolhe até caber).
for i, g in enumerate(guias):
    cx = x0 + i * larg + larg // 2 + (12 if i == 0 else 0)
    nome, tam = g["campeao"], 32
    while d.textlength(nome, font=fonte("HankenGrotesk-normal.woff2", tam, 800)) > larg - 24:
        tam -= 1
    d.text((cx, H - 92), nome, font=fonte("HankenGrotesk-normal.woff2", tam, 800), fill=CREME, anchor="ms")
    d.text((cx, H - 60), f"{g.get('rota', '')} · {n_matchups(g)}", font=fonte("HankenGrotesk-normal.woff2", 20, 600), fill=LIMAO, anchor="ms")

x = 64
icone = desenha(72)
img.paste(icone, (x, 92), icone)
marca = fonte("HankenGrotesk-normal.woff2", 52, 800)
d.text((x + 90, 128), "battle", font=marca, fill=(242, 242, 238), anchor="lm")
d.text((x + 90 + d.textlength("battle", font=marca), 128), "match", font=marca, fill=LIMAO, anchor="lm")
d.text((x, 196), "Guias de", font=fonte("HankenGrotesk-normal.woff2", 64, 800), fill=CREME)
d.text((x, 266), "matchup", font=fonte("HankenGrotesk-normal.woff2", 64, 800), fill=CREME)
d.line([(x, 354), (x + 120, 354)], fill=LIMAO, width=3)
d.text((x, 374), "As notas de quem joga, matchup", font=fonte("HankenGrotesk-normal.woff2", 28, 500), fill=CREME)
d.text((x, 410), "por matchup: runas, build,", font=fonte("HankenGrotesk-normal.woff2", 28, 500), fill=CREME)
d.text((x, 446), "cooldowns e como jogar.", font=fonte("HankenGrotesk-normal.woff2", 28, 500), fill=CREME)
d.text((x, 502), "League of Legends · português e inglês", font=fonte("HankenGrotesk-normal.woff2", 24, 600), fill=BAIXO)
d.text((x, H - 58), "battlematch.vercel.app", font=fonte("HankenGrotesk-normal.woff2", 22, 500), fill=BAIXO)

img.save(ROOT / "og.jpg", "JPEG", quality=86, optimize=True, progressive=True)
print("og.jpg", (ROOT / "og.jpg").stat().st_size // 1024, "KB")
