"""Gera os ícones do BattleMatch (identidade "Rota", escolhida em 2026-10-28) a partir do desenho abaixo.

Você e o inimigo na mesma rota: um fio diagonal no quadrado escuro, uma bolinha cheia (você) embaixo à
esquerda e um anel (o inimigo) em cima à direita, em verde-limão. O mesmo desenho está em src/icone/marca.svg.
Saem: src/icone/icone-64.png e apple-180.png (aba do site), src/icone/original.png (1024, base do .ico do app),
icones/icone-192.png, icone-512.png e icone-maskable-512.png (manifest). Rode: python scripts/icone_marca.py
"""
import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
FUNDO, FIO, LIMAO = (20, 22, 28), (58, 63, 75), (198, 242, 78)
SUPER = 4  # desenha maior e reduz, para as bordas saírem suaves


def desenha(tam, sangra=False, pequeno=False):
    """Ícone em tam x tam. sangra: fundo até a borda e desenho no centro seguro (ícone maskable do Android).
    pequeno: sem o fio e com as bolinhas maiores, que é o que ainda se lê em 16-32 px."""
    s = tam * SUPER
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = s / 64  # o desenho é feito numa grade de 64
    if sangra:
        d.rectangle((0, 0, s, s), fill=FUNDO)
        u *= .8  # 80% do centro: a área que nenhuma máscara corta
        o = s * .1
    else:
        d.rounded_rectangle((0, 0, s - 1, s - 1), radius=14 * u, fill=FUNDO)
        o = 0
    p = lambda x, y: (o + x * u, o + y * u)
    if not pequeno:
        (x1, y1), (x2, y2) = p(14, 50), p(50, 14)
        d.line((x1, y1, x2, y2), fill=FIO, width=round(10 * u))
        for x, y in ((x1, y1), (x2, y2)):  # pontas redondas
            d.ellipse((x - 5 * u, y - 5 * u, x + 5 * u, y + 5 * u), fill=FIO)
    rv, ri, borda = (9, 9, 5) if pequeno else (8, 8, 4)
    cx, cy = p(21, 43)
    d.ellipse((cx - rv * u, cy - rv * u, cx + rv * u, cy + rv * u), fill=LIMAO)
    cx, cy = p(43, 21)
    d.ellipse((cx - ri * u, cy - ri * u, cx + ri * u, cy + ri * u), outline=LIMAO, width=round(borda * u))
    return img.resize((tam, tam), Image.LANCZOS)


if __name__ == "__main__":
    icone, pwa = ROOT / "src" / "icone", ROOT / "icones"
    desenha(64).save(icone / "icone-64.png", optimize=True)
    desenha(180).save(icone / "apple-180.png", optimize=True)
    desenha(1024).save(icone / "original.png", optimize=True)
    desenha(192).save(pwa / "icone-192.png", optimize=True)
    desenha(512).save(pwa / "icone-512.png", optimize=True)
    desenha(512, sangra=True).save(pwa / "icone-maskable-512.png", optimize=True)
    print("ícones gerados")
