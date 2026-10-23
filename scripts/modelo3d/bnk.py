"""Lê bancos do Wwise do LoL (.bnk e .wpk) e resolve evento -> arquivos .wem."""
import struct


def fnv1(nome):
    h = 2166136261
    for c in nome.lower().encode():
        h = (h * 16777619) & 0xFFFFFFFF
        h ^= c
    return h


def secoes(b):
    o, out = 0, {}
    while o + 8 <= len(b):
        tag, tam = b[o:o + 4].decode("latin1"), struct.unpack_from("<I", b, o + 4)[0]
        out[tag] = b[o + 8:o + 8 + tam]
        o += 8 + tam
    return out


def hirc(b):
    """{id: (tipo, dados)} dos objetos da hierarquia."""
    s = secoes(b)
    objs = {}
    if "HIRC" not in s:
        return objs, s
    h = s["HIRC"]
    (n,) = struct.unpack_from("<I", h, 0)
    o = 4
    for _ in range(n):
        tipo, tam, oid = struct.unpack_from("<BII", h, o)
        objs[oid] = (tipo, h[o + 9:o + 5 + tam])
        o += 5 + tam
    return objs, s


def midias_bnk(s):
    """wem embutidos num .bnk (DIDX + DATA): {id: bytes}."""
    if "DIDX" not in s:
        return {}
    d, data = s["DIDX"], s.get("DATA", b"")
    out = {}
    for i in range(0, len(d), 12):
        wid, off, tam = struct.unpack_from("<III", d, i)
        out[wid] = data[off:off + tam]
    return out


def midias_wpk(b):
    assert b[:4] == b"r3d2", b[:4]
    (ver, n) = struct.unpack_from("<II", b, 4)
    out = {}
    for i in range(n):
        (oe,) = struct.unpack_from("<I", b, 12 + i * 4)
        if not oe:
            continue
        off, tam, nl = struct.unpack_from("<III", b, oe)
        nome = b[oe + 12:oe + 12 + nl * 2].decode("utf-16-le")
        out[int(nome.split(".")[0])] = b[off:off + tam]
    return out


CONTEINER = (5, 6, 7, 9)


def pais(objs):
    """Pai de cada objeto: o primeiro id de contêiner que aparece nos dados dele (DirectParentID)."""
    out = {}
    for oid, (t, d) in objs.items():
        if t not in (2,) + CONTEINER:
            continue
        ini = 9 if t == 2 else 0  # no Sound, pula plugin/stream/source
        for k in range(ini, len(d) - 3):
            (x,) = struct.unpack_from("<I", d, k)
            if x != oid and x in objs and objs[x][0] in CONTEINER:
                # ActorMixer só pode ser filho de outro ActorMixer.
                if t == 7 and objs[x][0] != 7:
                    continue
                out[oid] = x
                break
    # Desfaz ciclos (A pai de B e B pai de A): fica o lado em que o pai é ActorMixer.
    for o, p in list(out.items()):
        if out.get(p) == o and objs[o][0] != 7:
            out.pop(p, None)
    return out


def resolve(objs, evento_id, filhos=None):
    """Ids de .wem tocados por um evento (segue ações Play e desce pelos filhos)."""
    if evento_id not in objs:
        return []
    if filhos is None:
        filhos = {}
        for o, pai in pais(objs).items():
            filhos.setdefault(pai, []).append(o)
    tipo, d = objs[evento_id]
    n = d[0]
    ids = struct.unpack_from(f"<{n}I", d, 1)
    wems = []

    vistos = set()

    def desce(oid, prof=0):
        if oid not in objs or prof > 8 or oid in vistos:
            return
        vistos.add(oid)
        t, dd = objs[oid]
        if t == 2:
            (src,) = struct.unpack_from("<I", dd, 5)
            if src not in wems:
                wems.append(src)
            return
        for f in filhos.get(oid, []):
            desce(f, prof + 1)

    for aid in ids:
        if aid in objs and objs[aid][0] == 3:
            (atipo, alvo) = struct.unpack_from("<HI", objs[aid][1], 0)
            if atipo == 0x0403:
                desce(alvo)
    return wems
