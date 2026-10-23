"""Converte esqueleto (.skl), malha (.skn) e animações (.anm) do LoL para um .glb.

Uso: python lol2glb.py <pasta com os arquivos extraídos> <saida.glb> [config.json]

Sem config, gera o Akshan padrão. Para uma skin, o config (montado por skin3d.py a partir dos
dados do jogo) diz os arquivos de esqueleto e malha, as texturas, que submalha usa qual
textura, o que fica escondido e as animações.
"""
import io
import json
import math
import struct
import sys
import pathlib

import numpy as np
from PIL import Image

PASTA = pathlib.Path(sys.argv[1])
SAIDA = pathlib.Path(sys.argv[2])

SKL, SKN = "akshan_base.skl", "akshan_base.skn"
TEXTURAS = {"main": ("akshan_base_tx_cm.png", True), "weapon": ("akshan_base_weapon_tx_cm.png", False)}  # chave: (png, vira jpeg?)
ESCONDER = {"Hood", "Hood_Hair", "Rope"}  # initialSubmeshToHide da skin base
TEXTURA = {"Weapon": "weapon", "Hook": "weapon", "Boomerang": "weapon"}  # o resto usa a principal
ANIMACOES = [  # (nome no glb, arquivo)
    ("idle", "akshan_idle1.anm"), ("idle_var", "idle1_var1.anm"), ("dance_intro", "dance_intro.anm"),
    ("dance", "dance_loop.anm"), ("laugh", "laugh.anm"),
    ("taunt_intro", "taunt_intro.anm"), ("taunt", "taunt_cycle.anm"),
    ("attack1", "attack1.anm"), ("attack2", "attack2.anm"), ("crit", "akshan_base_crit.anm"), ("crit_to_idle", "crit_to_idle.anm"),
    ("recall", "recall.anm"),
]
if len(sys.argv) > 3:
    _cfg = json.loads(pathlib.Path(sys.argv[3]).read_text(encoding="utf-8"))
    SKL, SKN = _cfg["skl"], _cfg["skn"]
    TEXTURAS = {k: tuple(v) for k, v in _cfg["texturas"].items()}
    ESCONDER = set(_cfg["esconder"])
    TEXTURA = _cfg["submesh_textura"]
    ANIMACOES = [tuple(a) for a in _cfg["animacoes"]]
TOL_POS, TOL_ROT, TOL_ESC = 0.02, 0.0004, 0.001  # erro aceito ao tirar quadros (unidades do jogo, 1-|dot|, escala)


def enxuga(tempos, vals, eh_rot, tol):
    """Tira quadros que a interpolação linear entre os vizinhos já reproduz."""
    manter = [0]
    i = 0
    n = len(tempos)
    while i < n - 1:
        j = i + 2
        while j < n:
            ok = True
            for k in range(i + 1, j):
                f = (tempos[k] - tempos[i]) / ((tempos[j] - tempos[i]) or 1)
                if eh_rot:
                    q = vals[i] * (1 - f) + vals[j] * f
                    q /= np.linalg.norm(q) or 1
                    if 1 - abs(float(np.dot(q, vals[k]))) > tol:
                        ok = False; break
                elif np.abs(vals[i] * (1 - f) + vals[j] * f - vals[k]).max() > tol:
                    ok = False; break
            if not ok:
                break
            j += 1
        i = j - 1
        manter.append(i)
    return tempos[manter], vals[manter]


def elf(nome):
    h = 0
    for c in nome.lower().encode():
        h = ((h << 4) + c) & 0xFFFFFFFF
        alto = h & 0xF0000000
        if alto:
            h ^= alto >> 24
        h &= ~alto & 0xFFFFFFFF
    return h


# ---------- Conversão de eixos: o LoL é de mão esquerda; espelha o X ----------
def pos(v):
    return (-v[0], v[1], v[2])


def rot(q):
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w) or 1
    return (x / n, -y / n, -z / n, w / n)


# ---------- SKL ----------
def ler_skl(b):
    (tam, token, versao, flags, njoints, ninf, o_joints, o_jidx, o_inf, o_nome, o_asset, o_bnames) = struct.unpack_from("<IIIHHIiiiiii", b, 0)
    assert token == 0x22FD4FC3, hex(token)
    joints = []
    for i in range(njoints):
        o = o_joints + i * 100
        (fl, jid, pai, _, hash_, raio) = struct.unpack_from("<HhhhIf", b, o)
        lt = struct.unpack_from("<3f", b, o + 16)
        ls = struct.unpack_from("<3f", b, o + 28)
        lr = struct.unpack_from("<4f", b, o + 40)
        (onome,) = struct.unpack_from("<i", b, o + 96)
        p = o + 96 + onome
        nome = b[p:b.index(b"\0", p)].decode()
        joints.append({"id": jid, "pai": pai, "nome": nome, "t": lt, "s": ls, "r": lr})
    influencias = list(struct.unpack_from(f"<{ninf}H", b, o_inf))
    return joints, influencias


# ---------- SKN ----------
def ler_skn(b):
    magic, maj, mnr = struct.unpack_from("<IHH", b, 0)
    assert magic == 0x00112233 and maj == 4, (hex(magic), maj)
    o = 8
    (nsub,) = struct.unpack_from("<I", b, o); o += 4
    subs = []
    for _ in range(nsub):
        nome = b[o:o + 64].split(b"\0")[0].decode()
        vs, vc, is_, ic = struct.unpack_from("<4I", b, o + 64)
        subs.append({"nome": nome, "vs": vs, "vc": vc, "is": is_, "ic": ic})
        o += 80
    (flags, nidx, nvert, vtam, vtipo) = struct.unpack_from("<5I", b, o); o += 20
    o += 24 + 16  # caixa e esfera
    idx = np.frombuffer(b, "<u2", nidx, o).astype(np.uint32); o += nidx * 2
    dt = [("p", "<f4", 3), ("inf", "u1", 4), ("w", "<f4", 4), ("n", "<f4", 3), ("uv", "<f4", 2)]
    if vtipo >= 1:
        dt.append(("cor", "u1", 4))
    if vtipo >= 2:
        dt.append(("tan", "<f4", 4))
    v = np.frombuffer(b, np.dtype(dt), nvert, o)
    assert np.dtype(dt).itemsize == vtam, (np.dtype(dt).itemsize, vtam)
    return subs, idx, v


# ---------- ANM ----------
RAIZ2 = 1.41421356237


def quat48(a, b, c):
    bits = a | (b << 16) | (c << 32)
    mx = (bits >> 45) & 3
    va, vb, vc = (bits >> 30) & 0x7FFF, (bits >> 15) & 0x7FFF, bits & 0x7FFF
    fa, fb, fc = [(x / 32767.0) * RAIZ2 - 1 / RAIZ2 for x in (va, vb, vc)]
    d = math.sqrt(max(0.0, 1 - (fa * fa + fb * fb + fc * fc)))
    return [(d, fa, fb, fc), (fa, d, fb, fc), (fa, fb, d, fc), (fa, fb, fc, d)][mx]


def ler_anm(b):
    """Devolve (duração, {hash do osso: {"t": [(tempo, xyz)], "r": [...], "s": [...]}})."""
    magic = b[:8]
    (ver,) = struct.unpack_from("<I", b, 8)
    trilhas = {}
    if magic == b"r3d2canm":
        (_, _, flags, njoints, nframes, njump, dur, fps) = struct.unpack_from("<IIIiiiff", b, 12)
        o = 12 + 32 + 24
        tmin = struct.unpack_from("<3f", b, o); tmax = struct.unpack_from("<3f", b, o + 12)
        smin = struct.unpack_from("<3f", b, o + 24); smax = struct.unpack_from("<3f", b, o + 36)
        (o_frames, o_jump, o_hashes) = struct.unpack_from("<iii", b, o + 48)
        hashes = struct.unpack_from(f"<{njoints}I", b, o_hashes + 12)
        for i in range(nframes):
            (tc, bits, v0, v1, v2) = struct.unpack_from("<5H", b, o_frames + 12 + i * 10)
            jid, tipo = bits & 0x3FFF, bits >> 14
            tempo = tc / 65535.0 * dur
            tr = trilhas.setdefault(hashes[jid], {"t": [], "r": [], "s": []})
            if tipo == 0:
                tr["r"].append((tempo, quat48(v0, v1, v2)))
            else:
                mn, mxv = (tmin, tmax) if tipo == 1 else (smin, smax)
                val = tuple(mn[k] + (mxv[k] - mn[k]) * (v / 65535.0) for k, v in enumerate((v0, v1, v2)))
                tr["t" if tipo == 1 else "s"].append((tempo, val))
        for tr in trilhas.values():
            for k in tr:
                tr[k].sort(key=lambda x: x[0])
        return dur, trilhas
    assert magic == b"r3d2anmd", magic
    (_, _, _, flags, ntr, nframes, fdur) = struct.unpack_from("<IIIIiif", b, 12)
    (o_hashes, o_asset, o_tempo, o_vet, o_quat, o_frames) = struct.unpack_from("<6i", b, 12 + 28)
    o_hashes += 12; o_vet += 12; o_quat += 12; o_frames += 12
    if ver == 5:
        nvet = (o_quat - o_vet) // 12
        nquat = (o_hashes - o_quat) // 6
        vet = [struct.unpack_from("<3f", b, o_vet + i * 12) for i in range(nvet)]
        quats = [quat48(*struct.unpack_from("<3H", b, o_quat + i * 6)) for i in range(nquat)]
        hashes = struct.unpack_from(f"<{ntr}I", b, o_hashes)
        for f in range(nframes):
            for k in range(ntr):
                ti, si, ri = struct.unpack_from("<3H", b, o_frames + (f * ntr + k) * 6)
                tr = trilhas.setdefault(hashes[k], {"t": [], "r": [], "s": []})
                tr["t"].append((f * fdur, vet[ti])); tr["s"].append((f * fdur, vet[si])); tr["r"].append((f * fdur, quats[ri]))
    elif ver == 4:
        nvet = (o_quat - o_vet) // 12
        nquat = (o_frames - o_quat) // 16
        vet = [struct.unpack_from("<3f", b, o_vet + i * 12) for i in range(nvet)]
        quats = [struct.unpack_from("<4f", b, o_quat + i * 16) for i in range(nquat)]
        cont = {}
        for i in range(ntr * nframes):
            (h, ti, si, ri, _) = struct.unpack_from("<I4H", b, o_frames + i * 12)
            f = cont.get(h, 0); cont[h] = f + 1
            tr = trilhas.setdefault(h, {"t": [], "r": [], "s": []})
            tr["t"].append((f * fdur, vet[ti])); tr["s"].append((f * fdur, vet[si])); tr["r"].append((f * fdur, quats[ri]))
    else:
        raise ValueError(f"anm versão {ver}")
    return (nframes - 1) * fdur, trilhas


# ---------- Monta o glTF ----------
class Glb:
    def __init__(self):
        self.bin = bytearray()
        self.g = {"asset": {"version": "2.0", "generator": "lol2glb (akshan-matchups)"}, "buffers": [], "bufferViews": [],
                  "accessors": [], "nodes": [], "meshes": [], "skins": [], "animations": [], "materials": [],
                  "textures": [], "images": [], "samplers": [{"magFilter": 9729, "minFilter": 9987}], "scenes": [], "scene": 0}

    def view(self, dados, alvo=None):
        while len(self.bin) % 4:
            self.bin.append(0)
        bv = {"buffer": 0, "byteOffset": len(self.bin), "byteLength": len(dados)}
        if alvo:
            bv["target"] = alvo
        self.bin += dados
        self.g["bufferViews"].append(bv)
        return len(self.g["bufferViews"]) - 1

    def acc(self, arr, tipo, comp, alvo=None, minmax=False, norm=False):
        arr = np.ascontiguousarray(arr)
        a = {"bufferView": self.view(arr.tobytes(), alvo), "componentType": comp, "count": int(arr.shape[0]), "type": tipo}
        if minmax:
            a["min"] = arr.min(axis=0).tolist() if arr.ndim > 1 else [float(arr.min())]
            a["max"] = arr.max(axis=0).tolist() if arr.ndim > 1 else [float(arr.max())]
        if norm:
            a["normalized"] = True
        self.g["accessors"].append(a)
        return len(self.g["accessors"]) - 1

    def salva(self, caminho):
        while len(self.bin) % 4:
            self.bin.append(0)
        self.g["buffers"] = [{"byteLength": len(self.bin)}]
        js = json.dumps(self.g, separators=(",", ":")).encode()
        while len(js) % 4:
            js += b" "
        total = 12 + 8 + len(js) + 8 + len(self.bin)
        with open(caminho, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, total))
            f.write(struct.pack("<I4s", len(js), b"JSON")); f.write(js)
            f.write(struct.pack("<I4s", len(self.bin), b"BIN\0")); f.write(self.bin)


def trs_matriz(t, r, s):
    x, y, z, w = r
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4)
    M[:3, :3] = R * np.array(s)
    M[:3, 3] = t
    return M


def main():
    joints, influencias = ler_skl((PASTA / SKL).read_bytes())
    subs, idx, v = ler_skn((PASTA / SKN).read_bytes())
    print(f"{len(joints)} ossos, {len(influencias)} influências, {len(v)} vértices, submalhas: {[s['nome'] for s in subs]}")
    g = Glb()

    # Ossos (nós 0..n-1) com a pose de repouso convertida.
    filhos = {i: [] for i in range(len(joints))}
    raizes = []
    for i, j in enumerate(joints):
        (filhos[j["pai"]] if j["pai"] >= 0 else raizes).append(i)
    glob = [None] * len(joints)
    for i, j in enumerate(joints):
        t, r = pos(j["t"]), rot(j["r"])
        no = {"name": j["nome"], "translation": list(t), "rotation": list(r), "scale": list(j["s"])}
        if filhos[i]:
            no["children"] = filhos[i]
        g.g["nodes"].append(no)
    for i in range(len(joints)):  # pais vêm antes dos filhos no SKL
        j = joints[i]
        local = trs_matriz(pos(j["t"]), rot(j["r"]), j["s"])
        glob[i] = local if j["pai"] < 0 else glob[j["pai"]] @ local
    ibm = np.array([np.linalg.inv(m).T.reshape(-1) for m in glob], dtype="<f4")  # glTF é coluna-maior

    # Malha: só as submalhas visíveis na skin base.
    P = v["p"].astype("<f4").copy(); P[:, 0] *= -1
    N = v["n"].astype("<f4").copy(); N[:, 0] *= -1
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-8)
    UV = v["uv"].astype("<f4")
    J = np.array(influencias, dtype=np.uint16)[v["inf"]].astype("<u2")
    W = v["w"].astype("<f4"); W /= np.maximum(W.sum(axis=1, keepdims=True), 1e-8)
    # Só os vértices das submalhas visíveis: as escondidas (árvore do recall etc.) não pesam nem
    # entram na caixa do modelo, que o site usa para enquadrar o Akshan.
    visiveis = [sm for sm in subs if sm["nome"] not in ESCONDER]
    usados = np.unique(np.concatenate([idx[sm["is"]:sm["is"] + sm["ic"]] for sm in visiveis]))
    novo = np.full(len(P), -1, dtype=np.int64); novo[usados] = np.arange(len(usados))
    P, N, UV, J, W = P[usados], N[usados], UV[usados], J[usados], W[usados]
    idx = novo[idx]
    a_p = g.acc(P, "VEC3", 5126, 34962, minmax=True)
    a_n = g.acc(N, "VEC3", 5126, 34962)
    a_uv = g.acc(UV, "VEC2", 5126, 34962)
    a_j = g.acc(J, "VEC4", 5123, 34962)
    a_w = g.acc(W, "VEC4", 5126, 34962)

    materiais = {}
    # Só entram as texturas de submalhas visíveis (as escondidas, como as telas do recall, não pesam no arquivo).
    usadas = {TEXTURA.get(sm["nome"], "main") for sm in subs if sm["nome"] not in ESCONDER}
    for chave, (arquivo, jpeg) in TEXTURAS.items():
        if chave not in usadas:
            continue
        im = Image.open(PASTA / arquivo)
        buf = io.BytesIO()
        if jpeg:
            im.convert("RGB").save(buf, "JPEG", quality=82, optimize=True); mime = "image/jpeg"
        else:
            im.save(buf, "PNG", optimize=True); mime = "image/png"
        g.g["images"].append({"bufferView": g.view(buf.getvalue()), "mimeType": mime})
        g.g["textures"].append({"sampler": 0, "source": len(g.g["images"]) - 1})
        g.g["materials"].append({"name": chave, "pbrMetallicRoughness": {"baseColorTexture": {"index": len(g.g["textures"]) - 1},
                                 "metallicFactor": 0, "roughnessFactor": 1}, "alphaMode": "MASK", "alphaCutoff": 0.3,
                                 "doubleSided": True})
        materiais[chave] = len(g.g["materials"]) - 1
    prims = []
    for s in subs:
        if s["nome"] in ESCONDER:
            continue
        tri = idx[s["is"]:s["is"] + s["ic"]].reshape(-1, 3)[:, ::-1]  # espelhar inverte a ordem dos triângulos
        a_i = g.acc(tri.reshape(-1).astype("<u4"), "SCALAR", 5125, 34963)
        prims.append({"attributes": {"POSITION": a_p, "NORMAL": a_n, "TEXCOORD_0": a_uv, "JOINTS_0": a_j, "WEIGHTS_0": a_w},
                      "indices": a_i, "material": materiais[TEXTURA.get(s["nome"], "main")]})
    g.g["meshes"].append({"name": "Akshan", "primitives": prims})
    g.g["skins"].append({"joints": list(range(len(joints))), "inverseBindMatrices": g.acc(ibm, "MAT4", 5126), "skeleton": raizes[0]})
    malha = len(g.g["nodes"])
    g.g["nodes"].append({"name": "AkshanMesh", "mesh": 0, "skin": 0})
    raiz = len(g.g["nodes"])
    g.g["nodes"].append({"name": "Akshan", "children": raizes + [malha]})
    g.g["scenes"].append({"nodes": [raiz]})

    # Animações.
    por_hash = {elf(j["nome"]): i for i, j in enumerate(joints)}
    for nome, arquivo in ANIMACOES:
        dur, trilhas = ler_anm((PASTA / arquivo).read_bytes())
        canais, samplers = [], []
        usados = 0
        for h, tr in trilhas.items():
            if h not in por_hash:
                continue
            usados += 1
            no = por_hash[h]
            for chave, caminho in (("t", "translation"), ("r", "rotation"), ("s", "scale")):
                keys = tr[chave]
                if not keys:
                    continue
                # Tempos repetidos atrapalham o glTF: fica o último valor de cada tempo.
                limpo = {}
                for tempo, val in keys:
                    limpo[round(tempo, 5)] = val
                tempos = np.array(sorted(limpo), dtype="<f4")
                vals = [limpo[t] for t in sorted(limpo)]
                if chave == "t":
                    vals = [pos(x) for x in vals]
                elif chave == "r":
                    vals = [rot(x) for x in vals]
                    for k in range(1, len(vals)):  # mantém o caminho curto entre chaves
                        if np.dot(vals[k], vals[k - 1]) < 0:
                            vals[k] = tuple(-c for c in vals[k])
                vals = np.array(vals, dtype="<f4")
                repouso = {"t": np.array(pos(joints[no]["t"])), "r": np.array(rot(joints[no]["r"])), "s": np.array(joints[no]["s"])}[chave]
                tol = {"t": TOL_POS, "r": TOL_ROT, "s": TOL_ESC}[chave]
                # Trilha parada na pose de repouso não precisa ir para o arquivo.
                if chave == "r":
                    if all(1 - abs(float(np.dot(q, repouso))) < tol for q in vals):
                        continue
                elif np.abs(vals - repouso).max() < tol:
                    continue
                tempos, vals = enxuga(tempos, vals, chave == "r", tol)
                if chave == "r":  # rotação em 16 bits normalizados (permitido pelo glTF em animações)
                    saida = g.acc(np.round(np.clip(vals, -1, 1) * 32767).astype("<i2"), "VEC4", 5122, norm=True)
                else:
                    saida = g.acc(vals.astype("<f4"), "VEC3", 5126)
                samplers.append({"input": g.acc(tempos.astype("<f4"), "SCALAR", 5126, minmax=True),
                                 "output": saida, "interpolation": "LINEAR"})
                canais.append({"sampler": len(samplers) - 1, "target": {"node": no, "path": caminho}})
        g.g["animations"].append({"name": nome, "channels": canais, "samplers": samplers})
        print(f"animação {nome}: {dur:.2f}s, {usados}/{len(trilhas)} trilhas ligadas a ossos")
    g.salva(SAIDA)
    print(SAIDA, SAIDA.stat().st_size // 1024, "KB")


main()
