"""Gera og.jpg (1200x630), a imagem que aparece quando o link do site é compartilhado.

Usa a arte de src/icone/original.webp e as fontes de src/fonts. Rode de novo se mudar o
número de matchups ou a arte: python scripts/og.py
"""
import json
import pathlib
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
W, H = 1200, 630
FUNDO, OURO, CREME, BAIXO = (14, 13, 11), (255, 214, 107), (255, 244, 214), (191, 179, 154)

bruto = (SRC / "guias" / "akshan" / "rows.js").read_text(encoding="utf-8").strip().rstrip(";")
n = len(json.loads(re.sub(r",\s*\]$", "]", bruto)))


def fonte(arquivo, tam, peso=None):
    f = ImageFont.truetype(str(SRC / "fonts" / arquivo), tam)
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


img = Image.new("RGB", (W, H), FUNDO)
arte = Image.open(SRC / "icone" / "original.webp").convert("RGB").resize((H, H), Image.LANCZOS)
# A arte entra pela direita e some no fundo escuro à esquerda.
mascara = Image.new("L", (H, H), 255)
d = ImageDraw.Draw(mascara)
for x in range(260):
    d.line([(x, 0), (x, H)], fill=int(255 * (x / 260) ** 1.6))
img.paste(arte, (W - H, 0), mascara)

d = ImageDraw.Draw(img)
x = 72
d.text((x, 150), "AKSHAN", font=fonte("Cinzel-normal.woff2", 104, 800), fill=OURO)
d.text((x, 280), "Guia de matchups", font=fonte("Cinzel-normal.woff2", 46, 600), fill=CREME)
d.line([(x, 356), (x + 120, 356)], fill=OURO, width=3)
d.text((x, 382), f"Notas do Peteruso · {n} matchups", font=fonte("HankenGrotesk-normal.woff2", 32, 600), fill=BAIXO)
d.text((x, 432), "Runas, build e lembrete de cada lane", font=fonte("HankenGrotesk-normal.woff2", 28, 400), fill=BAIXO)
d.text((x, H - 72), "akshan-matchups.vercel.app", font=fonte("HankenGrotesk-normal.woff2", 24, 500), fill=(150, 140, 120))

img.save(ROOT / "og.jpg", "JPEG", quality=86, optimize=True, progressive=True)
print("og.jpg", (ROOT / "og.jpg").stat().st_size // 1024, "KB")
