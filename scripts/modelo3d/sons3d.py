"""Converte os sons das animações de um campeão (bancos do Wwise) para sons/<campeão>3d/*.ogg.

Uso: python sons3d.py [campeão] <pasta com os bancos> <vgmstream-cli.exe> <pasta de saída> [número da skin]
(sem o campeão, vale o Akshan, como antes). A pasta tem <campeão>_base_sfx_*.bnk e ptbr/<campeão>_base_vo_*,
que saem do .wad do jogo (scripts/modelo3d/wad.py; a dublagem pt-BR fica no Campeão.pt_BR.wad.client).
Com o número da skin, converte só os efeitos dela (Play_sfx_AkshanSkinNN_...); a voz é a do campeão padrão.
Gera também sons3d.json: {chave: número de variações}.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import soundfile as sf

from bnk import fnv1, hirc, midias_bnk, midias_wpk, resolve

args = sys.argv[1:]
CAMPEAO = "akshan" if pathlib.Path(args[0]).exists() else args.pop(0).lower()
PASTA, VGM, SAIDA = pathlib.Path(args[0]), args[1], pathlib.Path(args[2])
SKIN = int(args[3]) if len(args) > 3 else 0
SAIDA.mkdir(parents=True, exist_ok=True)

# chave curta no site -> evento do jogo (sem o "Play_sfx_<Campeão>_" / "Play_vo_<Campeão>_" do começo)
EVENTOS = {
    "akshan": ({
        "dance_cast": "Dance3D_cast", "dance": "Dance3D_buffactivate",
        "taunt_cast": "Taunt3D_cast", "taunt": "Taunt3D_buffactivate", "laugh": "Laugh3D_buffactivate",
        "recall": "Recall3D_buffactivate",
        "aa1": "AkshanBasicAttack_OnMissileCast", "aa2": "AkshanBasicAttack2_OnMissileCast", "crit": "AkshanCritAttack_OnMissileCast",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral", "vo_recall": "Recall3DGeneral",
        "vo_aa1": "AkshanBasicAttack_cast3D", "vo_aa2": "AkshanBasicAttack2_cast3D", "vo_crit": "AkshanCritAttack_cast3D",
    }),
    "mordekaiser": ({
        "dance_cast": "Dance_cast", "dance": "Dance_loop", "taunt": "Taunt_cast", "laugh": "Laugh_cast", "recall": "Recall_cast",
        "aa1": "MordekaiserBasicAttack_OnCast", "aa2": "MordekaiserBasicAttack2_OnCast",
        "hit1": "MordekaiserBasicAttack_OnHit", "hit2": "MordekaiserBasicAttack2_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral", "vo_recall": "Recall3DGeneral",
        "vo_aa1": "MordekaiserBasicAttack_cast3D", "vo_aa2": "MordekaiserBasicAttack2_cast3D",
    }),
    "illaoi": ({
        "dance_cast": "IllaoiDanceIn3D_buffactivate", "dance": "IllaoiDance3D_buffactivate", "taunt": "Taunt3D_buffactivate",
        "laugh": "Laugh3D_buffactivate", "recall": "Recall3D_buffactivate",
        "aa1": "IllaoiBasicAttack_OnCast", "aa2": "IllaoiBasicAttack2_OnCast", "crit": "IllaoiCritAttack_OnCast",
        "hit1": "IllaoiBasicAttack_OnHit", "hit2": "IllaoiBasicAttack2_OnHit", "hit_crit": "IllaoiCritAttack_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral", "vo_recall": "Recall3DGeneral",
        "vo_aa1": "IllaoiBasicAttack_cast3D", "vo_aa2": "IllaoiBasicAttack2_cast3D", "vo_crit": "IllaoiCritAttack_cast3D",
    }),
}
SFX, VO = EVENTOS[CAMPEAO]
NOME = {"akshan": "Akshan", "mordekaiser": "Mordekaiser", "illaoi": "Illaoi"}[CAMPEAO]

banco = f"{CAMPEAO}_skin{SKIN:02d}" if SKIN else f"{CAMPEAO}_base"
prefixo = f"Play_sfx_{NOME}Skin{SKIN:02d}_" if SKIN else f"Play_sfx_{NOME}_"
ev_sfx, _ = hirc((PASTA / f"{banco}_sfx_events.bnk").read_bytes())
_, s_audio = hirc((PASTA / f"{banco}_sfx_audio.bnk").read_bytes())
med_sfx = midias_bnk(s_audio)
if SKIN:
    VO = {}
else:
    ev_vo, _ = hirc((PASTA / "ptbr" / f"{CAMPEAO}_base_vo_events.bnk").read_bytes())
    med_vo = midias_wpk((PASTA / "ptbr" / f"{CAMPEAO}_base_vo_audio.wpk").read_bytes())

contagem, total = {}, 0
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    for chave, nome, objs, med in [(k, f"{prefixo}{v}", ev_sfx, med_sfx) for k, v in SFX.items()] + \
                                   [(k, f"Play_vo_{NOME}_{v}", ev_vo, med_vo) for k, v in VO.items()]:
        wems = [w for w in resolve(objs, fnv1(nome)) if w in med]
        if not wems:
            print("sem áudio:", nome)
            continue
        for i, w in enumerate(wems):
            destino = SAIDA / f"{chave}-{i}.ogg"
            if not destino.exists():  # dá para rodar de novo sem refazer o que já saiu
                wem, wav = tmp / f"{w}.wem", tmp / f"{w}.wav"
                wem.write_bytes(med[w])
                subprocess.run([VGM, "-o", str(wav), str(wem)], check=True, capture_output=True, timeout=60)
                dados, taxa = sf.read(wav, dtype="float32")
                if dados.ndim > 1:  # mono: som de efeito no navegador não precisa de estéreo, e pesa a metade
                    dados = dados.mean(axis=1)
                # Grava em blocos: o codificador Vorbis estoura a pilha com áudio longo de uma vez.
                with sf.SoundFile(destino, "w", taxa, 1, format="OGG", subtype="VORBIS") as f:
                    for k in range(0, len(dados), 4096):
                        f.write(dados[k:k + 4096])
            total += destino.stat().st_size
        contagem[chave] = len(wems)
        print(f"{chave}: {len(wems)} variação(ões)", flush=True)
(SAIDA / "sons3d.json").write_text(json.dumps(contagem), encoding="utf-8")
print(f"{sum(contagem.values())} arquivos, {total // 1024} KB")
