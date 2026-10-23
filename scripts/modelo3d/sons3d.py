"""Converte os sons das animações do Akshan (bancos do Wwise) para sons/akshan3d/*.ogg.

Uso: python sons3d.py <pasta com os bancos> <vgmstream-cli.exe> <pasta de saída>
Gera também sons3d.json: {chave: número de variações}.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import soundfile as sf

from bnk import fnv1, hirc, midias_bnk, midias_wpk, resolve

PASTA, VGM, SAIDA = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
SAIDA.mkdir(parents=True, exist_ok=True)

# chave curta no site -> evento do jogo
SFX = {
    "dance_cast": "Dance3D_cast", "dance": "Dance3D_buffactivate",
    "taunt_cast": "Taunt3D_cast", "taunt": "Taunt3D_buffactivate", "laugh": "Laugh3D_buffactivate",
    "recall": "Recall3D_buffactivate",
    "aa1": "AkshanBasicAttack_OnMissileCast", "aa2": "AkshanBasicAttack2_OnMissileCast", "crit": "AkshanCritAttack_OnMissileCast",
}
VO = {
    "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral", "vo_recall": "Recall3DGeneral",
    "vo_aa1": "AkshanBasicAttack_cast3D", "vo_aa2": "AkshanBasicAttack2_cast3D", "vo_crit": "AkshanCritAttack_cast3D",
}

ev_sfx, _ = hirc((PASTA / "akshan_base_sfx_events.bnk").read_bytes())
_, s_audio = hirc((PASTA / "akshan_base_sfx_audio.bnk").read_bytes())
med_sfx = midias_bnk(s_audio)
ev_vo, _ = hirc((PASTA / "ptbr" / "akshan_base_vo_events.bnk").read_bytes())
med_vo = midias_wpk((PASTA / "ptbr" / "akshan_base_vo_audio.wpk").read_bytes())

contagem, total = {}, 0
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    for chave, nome, objs, med in [(k, f"Play_sfx_Akshan_{v}", ev_sfx, med_sfx) for k, v in SFX.items()] + \
                                   [(k, f"Play_vo_Akshan_{v}", ev_vo, med_vo) for k, v in VO.items()]:
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
