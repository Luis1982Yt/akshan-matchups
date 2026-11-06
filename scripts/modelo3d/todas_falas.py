"""Tira TODAS as falas dubladas (pt-BR) de um campeão, uma por arquivo, e (opcional) escreve o que cada uma diz.

Serve para achar uma fala específica (ex.: o "por favor e obrigado" do Akshan) e cortar no editor de áudio.
Só roda no PC com o LoL instalado: os áudios estão no Campeão.pt_BR.wad.client, extraído antes com wad.py
(o mesmo passo do falas.py), e precisa do vgmstream-cli.

Uso:
  python todas_falas.py <pasta com ptbr/akshan_base_vo_audio.wpk> <vgmstream-cli.exe> <pasta de saída> [--transcrever]

Saída: <pasta de saída>/fala-001.wav, fala-002.wav... (WAV, bom para editar). Com --transcrever (precisa de
`pip install faster-whisper soundfile numpy`), grava também falas.txt com "arquivo | texto", para procurar a palavra.
"""
import pathlib
import subprocess
import sys

from bnk import midias_wpk

PASTA, VGM, SAIDA = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
TRANSCREVER = "--transcrever" in sys.argv
SAIDA.mkdir(parents=True, exist_ok=True)

wpk = next((PASTA / "ptbr").glob("*_vo_audio.wpk"))
med = midias_wpk(wpk.read_bytes())
arquivos = []
for n, (wid, dados) in enumerate(sorted(med.items()), 1):
    wem, wav = SAIDA / f"{wid}.wem", SAIDA / f"fala-{n:03d}.wav"
    wem.write_bytes(dados)
    subprocess.run([VGM, "-o", str(wav), str(wem)], check=True, capture_output=True, timeout=60)
    wem.unlink()
    arquivos.append(wav)
print(f"{len(arquivos)} falas em {SAIDA}")

if TRANSCREVER:
    import numpy as np
    import soundfile as sf
    from faster_whisper import WhisperModel
    modelo = WhisperModel("small", device="cpu", compute_type="int8")
    linhas = []
    for wav in arquivos:
        audio, taxa = sf.read(wav, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        n = int(len(audio) * 16000 / taxa)  # o modelo quer 16 kHz
        audio = np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio).astype("float32")
        texto = " ".join(s.text.strip() for s in modelo.transcribe(audio, language="pt")[0])
        linhas.append(f"{wav.name} | {texto}")
        print(linhas[-1])
    (SAIDA / "falas.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("transcrição em", SAIDA / "falas.txt")
