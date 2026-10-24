"""Gera o app/dist/AkshanMatchups.exe (um arquivo só, sem console).

Rode da raiz do repositório: python app/gerar_exe.py
"""

import os
import subprocess
import sys

from PIL import Image

APP = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(APP)
SRC = os.path.join(RAIZ, "src")

ico = os.path.join(APP, "build", "icone.ico")
os.makedirs(os.path.dirname(ico), exist_ok=True)
Image.open(os.path.join(SRC, "icone", "original.webp")).convert("RGBA").save(
    ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

# Cópias embutidas do guia (usadas se o GitHub não responder) e o ícone da bandeja.
dados = [os.path.join(SRC, "guias", "akshan", "rows.js"), os.path.join(SRC, "guias", "akshan", "meta.json"),
         os.path.join(SRC, "icone", "icone-64.png")]
subprocess.run([
    sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed",
    "--name", "AkshanMatchups", "--icon", ico,
    "--distpath", os.path.join(APP, "dist"), "--workpath", os.path.join(APP, "build"), "--specpath", os.path.join(APP, "build"),
    *[a for d in dados for a in ("--add-data", f"{d}{os.pathsep}dados")],
    *[a for m in ("numpy", "tkinter", "unittest", "pydoc") for a in ("--exclude-module", m)],
    os.path.join(APP, "akshan_app.py"),
], check=True)
print("Pronto:", os.path.join(APP, "dist", "AkshanMatchups.exe"))
