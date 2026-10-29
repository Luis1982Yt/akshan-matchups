"""Baixa do CommunityDragon os sons do cliente do LoL usados no site e as falas de escolha de cada campeão de guia.

Grava em sons/ui/ e sons/vo/<id do campeão>.ogg (inglês em sons/vo/en/) (ao lado do index.html). Rode de novo se entrar um guia novo.
Os sons são da Riot Games; o site é de fã, sem ligação com a Riot.
"""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CD = "https://raw.communitydragon.org/latest/plugins"
UI = f"{CD}/rcp-fe-lol-champ-select/global/default/sounds"
VO = f"{CD}/rcp-be-lol-game-data/global/pt_br/v1/champion-choose-vo"
VO_EN = f"{CD}/rcp-be-lol-game-data/global/default/v1/champion-choose-vo"  # voz original em inglês

SONS_UI = {
    "grade": "sfx-uikit-grid-click",
    "passa": "sfx-uikit-grid-hover",
    "travar": "sfx-cs-lockin-button-click",
    "avanca": "sfx-uikit-button-arrowfwd-click",
    "volta": "sfx-uikit-button-arrowback-click",
    "chip": "sfx-uikit-button-pip-click",
    "abre": "sfx-cs-champgrid-button-open",
    "fecha": "sfx-cs-champgrid-button-close",
    "clique": "sfx-uikit-generic-click-small",
}
# Id numérico do campeão no cliente, para a fala de escolha.
CHAVE = {"Akshan": 166, "Mordekaiser": 82, "Illaoi": 420, "Kayle": 10, "Fiora": 114, "K'Sante": 897}


def baixar(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(urllib.request.urlopen(req).read())
    print(f"{destino.relative_to(ROOT)} ({destino.stat().st_size // 1024} KB)")


for nome, arquivo in SONS_UI.items():
    baixar(f"{UI}/{arquivo}.ogg", ROOT / "sons" / "ui" / f"{nome}.ogg")

for guia in json.loads((ROOT / "src" / "guias.json").read_text(encoding="utf-8")):
    campeao = guia["campeao"]
    arquivo = guia.get("id_campeao", campeao)  # o site toca sons/vo/<id do campeão>.ogg
    if campeao in CHAVE:
        baixar(f"{VO}/{CHAVE[campeao]}.ogg", ROOT / "sons" / "vo" / f"{arquivo}.ogg")
        baixar(f"{VO_EN}/{CHAVE[campeao]}.ogg", ROOT / "sons" / "vo" / "en" / f"{arquivo}.ogg")
    else:
        print(f"Sem id numérico para {campeao}: acrescente em CHAVE para ter a fala de escolha.")
