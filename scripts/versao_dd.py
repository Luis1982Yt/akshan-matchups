"""Versão do Data Dragon (patch do LoL) usada pelo site e pelos scripts, guardada em src/versao_dd.txt.

Os scripts fazem `from versao_dd import VER`; o build põe a mesma versão no template.
`python scripts/versao_dd.py` troca para a versão mais nova que a Riot publicou (o workflow diário roda isso
antes de baixar as planilhas, então ícones e cooldowns acompanham o patch).
"""
import json
import pathlib
import urllib.request

ARQ = pathlib.Path(__file__).resolve().parent.parent / "src" / "versao_dd.txt"
VER = ARQ.read_text(encoding="utf-8").strip()

if __name__ == "__main__":
    with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json", timeout=30) as r:
        nova = json.load(r)[0]
    if nova != VER:
        ARQ.write_text(nova + "\n", encoding="utf-8", newline="\n")
        print(f"Data Dragon: {VER} -> {nova}")
    else:
        print(f"Data Dragon já está na {VER}")
