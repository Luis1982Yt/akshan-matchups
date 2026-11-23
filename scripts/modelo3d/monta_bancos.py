"""Monta scripts/modelo3d/bancos/<campeão>/ com os bancos SFX e VO pt-BR prontos para o sons3d.py,
direto da instalação do LoL. O SFX sai do caminho padrão; a voz nem sempre tem caminho padrão
no .pt_BR.wad (varia por campeão), então é achada pelo conteúdo: o .bnk de eventos é o que resolve
"Play_vo_<Nome>_Taunt3DGeneral", e o .wpk de áudio é o que contém os .wem desse evento (não necessariamente o maior).

Uso: python monta_bancos.py <campeão>:<Nome> [<campeão>:<Nome> ...]
(<campeão> é a pasta em sons/, minúscula; <Nome> é como aparece em Riot Games/.../Champions/<Nome>.wad.client)
"""
import pathlib
import sys

import xxhash

from bnk import fnv1, hirc, midias_wpk, resolve
from wad import ler_wad, extrai

RAIZ_RIOT = pathlib.Path("C:/Riot Games/League of Legends/Game/DATA/FINAL/Champions")
SAIDA = pathlib.Path(__file__).with_name("bancos")

for par in sys.argv[1:]:
    camp, nome = par.split(":")
    dst = SAIDA / camp
    dst_vo = dst / "ptbr"
    dst_vo.mkdir(parents=True, exist_ok=True)

    f, ent = ler_wad(str(RAIZ_RIOT / f"{nome}.wad.client"))
    for sufixo in ("events", "audio"):
        caminho = f"assets/sounds/wwise2016/sfx/characters/{camp}/skins/base/{camp}_base_sfx_{sufixo}.bnk"
        h = xxhash.xxh64(caminho.lower().encode()).intdigest()
        (dst / f"{camp}_base_sfx_{sufixo}.bnk").write_bytes(extrai(f, ent[h]))

    f, ent = ler_wad(str(RAIZ_RIOT / f"{nome}.pt_BR.wad.client"))
    bnks, wpks = [], []
    for h, e in ent.items():
        d = extrai(f, e)
        if d[:4] == b"BKHD":
            bnks.append((h, d))
        elif d[:4] == b"r3d2":
            wpks.append((h, d))

    evento_taunt = f"Play_vo_{nome}_Taunt3DGeneral"
    objs_certo = wems_taunt = None
    for h, d in bnks:
        objs, _ = hirc(d)
        wems = resolve(objs, fnv1(evento_taunt))
        if wems:
            objs_certo, wems_taunt = objs, wems
            (dst_vo / f"{camp}_base_vo_events.bnk").write_bytes(d)
            break
    if objs_certo is None:
        print(f"{camp}: NÃO achei o bnk de eventos de voz!")
        continue

    for h, d in wpks:
        med = midias_wpk(d)
        if any(w in med for w in wems_taunt):
            (dst_vo / f"{camp}_base_vo_audio.wpk").write_bytes(d)
            break
    else:
        print(f"{camp}: NÃO achei o wpk de áudio certo!")
        continue

    print(f"{camp}: ok -> {dst}")
