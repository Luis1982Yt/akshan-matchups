"""Gera og.jpg (1200x630), a imagem que aparece quando o link do site é compartilhado.

Mostra todos os guias do src/guias.json: uma faixa da splash de cada campeão (Data Dragon) com o nome,
a rota e o número de matchups. Precisa de internet para baixar as splashes. Rode de novo quando entrar
ou sair um guia: python scripts/og.py
"""
import io
import json
import pathlib
import re
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
W, H = 1200, 630
FUNDO, OURO, CREME, BAIXO = (14, 13, 11), (255, 214, 107), (255, 244, 214), (191, 179, 154)
# Onde fica o rosto na splash centralizada (fração da largura), para a faixa estreita não cortar a cabeça.
ROSTO = {"Akshan": .45, "Mordekaiser": .5, "Illaoi": .47, "Kayle": .73}


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
    s = splash(g["campeao"])
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
        d.line([(x0 + i * larg, 0), (x0 + i * larg, H)], fill=(120, 100, 50), width=2)

# A primeira faixa some no fundo escuro pela esquerda.
mascara = Image.new("L", (120, H), 0)
dm = ImageDraw.Draw(mascara)
for x in range(120):
    dm.line([(x, 0), (x, H)], fill=int(255 * (1 - x / 120) ** 1.5))
img.paste(Image.new("RGB", (120, H), FUNDO), (x0, 0), mascara)

# Nome, rota e número de matchups embaixo de cada faixa (o nome encolhe até caber).
for i, g in enumerate(guias):
    cx = x0 + i * larg + larg // 2 + (12 if i == 0 else 0)
    nome, tam = g["campeao"].upper(), 34
    while d.textlength(nome, font=fonte("Cinzel-normal.woff2", tam, 800)) > larg - 28:
        tam -= 1
    d.text((cx, H - 96), nome, font=fonte("Cinzel-normal.woff2", tam, 800), fill=OURO, anchor="ms")
    d.text((cx, H - 62), f"{g.get('rota', '')} · {n_matchups(g)} matchups", font=fonte("HankenGrotesk-normal.woff2", 20, 600), fill=CREME, anchor="ms")

x = 64
d.text((x, 118), "LEAGUE OF LEGENDS", font=fonte("HankenGrotesk-normal.woff2", 22, 700), fill=BAIXO)
d.text((x, 150), "Guias de", font=fonte("Cinzel-normal.woff2", 70, 800), fill=OURO)
d.text((x, 228), "matchup", font=fonte("Cinzel-normal.woff2", 70, 800), fill=OURO)
d.line([(x, 330), (x + 120, 330)], fill=OURO, width=3)
d.text((x, 356), "As notas de quem joga, matchup", font=fonte("HankenGrotesk-normal.woff2", 28, 500), fill=CREME)
d.text((x, 392), "por matchup: runas, build,", font=fonte("HankenGrotesk-normal.woff2", 28, 500), fill=CREME)
d.text((x, 428), "cooldowns e como jogar.", font=fonte("HankenGrotesk-normal.woff2", 28, 500), fill=CREME)
d.text((x, 486), "Português e inglês", font=fonte("HankenGrotesk-normal.woff2", 24, 600), fill=BAIXO)
d.text((x, H - 58), "battlematch.vercel.app", font=fonte("HankenGrotesk-normal.woff2", 22, 500), fill=(150, 140, 120))

img.save(ROOT / "og.jpg", "JPEG", quality=86, optimize=True, progressive=True)
print("og.jpg", (ROOT / "og.jpg").stat().st_size // 1024, "KB")
