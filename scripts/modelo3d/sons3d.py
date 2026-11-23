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
    }),    "kayle": ({
        "dance_cast": "Dance3D_buffactivate_in", "dance": "Dance3D_loop", "taunt": "Taunt3D_buffactivate",
        "laugh": "Laugh3D_buffactivate", "recall": "Recall3D_leadin",
        "aa1": "KayleBasicAttack_OnCast", "aa2": "KayleBasicAttack2_OnCast",
        "hit1": "KayleBasicAttack_OnHit", "hit2": "KayleBasicAttack2_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral", "vo_recall": "Recall3DGeneral",
        "vo_aa1": "KayleBasicAttack_cast3D", "vo_aa2": "KayleBasicAttack2_cast3D",
    }),
    "fiora": ({
        "dance": "Dance3D_buffactivate", "taunt": "Taunt3D_buffactivate",
        "aa1": "FioraBasicAttack_OnCast", "hit1": "FioraBasicAttack_OnHit",
        "aa2": "FioraBasicAttack2_OnCast", "hit2": "FioraBasicAttack2_OnHit",
        "crit": "FioraCritAttack_OnCast", "hit_crit": "FioraCritAttack_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral",
        "vo_aa1": "FioraBasicAttack_cast3D", "vo_aa2": "FioraBasicAttack2_cast3D", "vo_crit": "FioraCritAttack_cast3D",
    }),  # sem laugh/recall no SFX, sem recall na voz
    "ksante": ({
        "dance_cast": "Dance3D_leadin", "dance": "Dance3D_loop_buffactivate", "taunt": "Taunt3D_buffactivate",
        "laugh": "Laugh3D_buffactivate", "recall": "Recall3D_buffactivate",
        "aa1": "KSanteBasicAttack_OnCast", "hit1": "KSanteBasicAttack_OnHit",
        "aa2": "KSanteBasicAttack2_OnCast", "hit2": "KSanteBasicAttack2_OnHit",
        "aa3": "KSanteBasicAttack3_OnCast", "hit3": "KSanteBasicAttack3_OnHit",
        "aa4": "KSanteBasicAttack4_OnCast", "hit4": "KSanteBasicAttack4_OnHit",
        "crit": "KSanteCritAttack_OnCast", "hit_crit": "KSanteCritAttack_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral", "vo_recall": "Recall3DGeneral",
        "vo_aa1": "KSanteBasicAttack_cast3D", "vo_aa2": "KSanteBasicAttack2_cast3D",
        "vo_aa3": "KSanteBasicAttack3_cast3D", "vo_aa4": "KSanteBasicAttack4_cast3D", "vo_crit": "KSanteCritAttack_cast3D",
    }),
    "akali": ({
        "dance": "Dance3D", "taunt_cast": "Taunt3D_buffactivate", "taunt": "Taunt3D_loop",
        "aa1": "AkaliBasicAttack_OnCast", "hit1": "AkaliBasicAttack_OnHit",
        "aa2": "AkaliBasicAttack2_OnCast", "hit2": "AkaliBasicAttack2_OnHit",
        "crit": "AkaliCritAttack_OnCast", "hit_crit": "AkaliCritAttack_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral",
        "vo_aa1": "AkaliBasicAttack_cast3D", "vo_aa2": "AkaliBasicAttack2_cast3D", "vo_crit": "AkaliCritAttack_cast3D",
    }),  # sem laugh/recall no SFX, sem recall na voz
    "garen": ({
        "dance_cast": "Dance3D_buffactivate", "dance": "Dance3D_loop", "taunt": "Taunt3D_buffactivate",
        "laugh": "Laugh3D_buffactivate",
        "aa1": "GarenBasicAttack_OnCast", "hit1": "GarenBasicAttack_OnHit",
        "aa2": "GarenBasicAttack2_OnCast", "hit2": "GarenBasicAttack2_OnHit",
        "crit": "GarenCritAttack_OnCast", "hit_crit": "GarenCritAttack_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral",
        "vo_aa1": "GarenBasicAttack_cast3D", "vo_aa2": "GarenBasicAttack2_cast3D", "vo_crit": "GarenCritAttack_cast3D",
    }),  # sem recall no SFX nem na voz
    "azir": ({
        "dance_cast": "Base_Dance3D_leadin", "dance": "Base_Dance3D_buffactivate", "taunt": "Base_Taunt3D_buffactivate",
        "laugh": "Base_Laugh3D_buffactivate", "recall": "Recall_leadin",
        "aa1": "AzirBasicAttack_OnCast", "hit1": "AzirBasicAttack_OnHit",
        "aa2": "AzirBasicAttack2_OnCast", "hit2": "AzirBasicAttack2_OnHit",
        "crit": "AzirCritAttack_OnCast", "hit_crit": "AzirCritAttack_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral", "vo_recall": "Recall3DGeneral",
        "vo_aa1": "AzirBasicAttack_cast3D", "vo_aa2": "AzirBasicAttack2_cast3D", "vo_crit": "AzirCritAttack_cast3D",
    }),
    "taric": ({
        "dance_cast": "Base_Dance3D_buffactivate", "dance": "Base_Dance3D_loop_buffactivate",
        "taunt": "Base_Taunt3D_buffactivate", "laugh": "Base_Laugh3D_buffactivate", "recall": "Base_Recall3D_buffactivate",
        "aa1": "TaricBasicAttack_OnCast", "hit1": "TaricBasicAttack_OnHit",
        "aa2": "TaricBasicAttack2_OnCast", "hit2": "TaricBasicAttack2_OnHit",
        "aa3": "TaricBasicAttack3_OnCast", "hit3": "TaricBasicAttack3_OnHit",
        "crit": "TaricCritAttack_OnCast", "hit_crit": "TaricCritAttack_OnHit",
    }, {
        "vo_taunt": "Taunt3DGeneral", "vo_laugh": "Laugh3DGeneral", "vo_recall": "Recall3DGeneral",
        "vo_aa1": "TaricBasicAttack_cast3D", "vo_aa2": "TaricBasicAttack2_cast3D",
        "vo_aa3": "TaricBasicAttack3_cast3D", "vo_crit": "TaricCritAttack_cast3D",
    }),
}
SFX, VO = EVENTOS[CAMPEAO]
NOME = {
    "akshan": "Akshan", "mordekaiser": "Mordekaiser", "illaoi": "Illaoi", "kayle": "Kayle",
    "fiora": "Fiora", "ksante": "KSante", "akali": "Akali", "garen": "Garen", "azir": "Azir", "taric": "Taric",
}[CAMPEAO]

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
