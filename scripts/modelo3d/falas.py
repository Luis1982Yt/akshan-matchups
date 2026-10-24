"""Extrai as falas do Akshan (dublagem pt-BR) que tocam ao trocar de skin: as de mover o campeão e de
primeiro encontro. Saem em sons/vo/akshan/fala-N.ogg, curtas e mono.

Uso: python falas.py <pasta com ptbr/akshan_base_vo_events.bnk e .wpk> <vgmstream-cli.exe> <pasta de saída>
"""
import pathlib
import subprocess
import sys
import tempfile

import soundfile as sf

from bnk import fnv1, hirc, midias_wpk, resolve

PASTA, VGM, SAIDA = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
SAIDA.mkdir(parents=True, exist_ok=True)
EVENTOS = ["Play_vo_Akshan_Move2DFirst", "Play_vo_Akshan_Move2DStandard", "Play_vo_Akshan_FirstEncounter3DGeneral"]

ev, _ = hirc((PASTA / "ptbr" / "akshan_base_vo_events.bnk").read_bytes())
med = midias_wpk((PASTA / "ptbr" / "akshan_base_vo_audio.wpk").read_bytes())
wems = []
for nome in EVENTOS:
    for w in resolve(ev, fnv1(nome)):
        if w in med and w not in wems:
            wems.append(w)

n, total = 0, 0
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    for w in wems:
        wem, wav = tmp / f"{w}.wem", tmp / f"{w}.wav"
        wem.write_bytes(med[w])
        subprocess.run([VGM, "-o", str(wav), str(wem)], check=True, capture_output=True, timeout=60)
        dados, taxa = sf.read(wav, dtype="float32")
        if dados.ndim > 1:
            dados = dados.mean(axis=1)
        if len(dados) / taxa > 6:  # fala longa demais para um toque de troca de skin
            continue
        destino = SAIDA / f"fala-{n}.ogg"
        with sf.SoundFile(destino, "w", taxa, 1, format="OGG", subtype="VORBIS") as f:
            for k in range(0, len(dados), 4096):
                f.write(dados[k:k + 4096])
        total += destino.stat().st_size
        n += 1
print(f"{n} falas, {total // 1024} KB")
