"""Extrai arquivos conhecidos de um .wad.client do LoL (versão 3) pelo hash do caminho."""
import struct, sys, pathlib, xxhash, zstandard, gzip, io

def ler_wad(caminho):
    f = open(caminho, "rb")
    mag, maj, mnr = struct.unpack("<2sBB", f.read(4))
    assert mag == b"RW", mag
    print("WAD versão", maj, mnr)
    f.read(256 + 8)  # assinatura + checksum (v3)
    (n,) = struct.unpack("<I", f.read(4))
    ent = {}
    for _ in range(n):
        h, off, csz, sz, tipo, sub, prim, chk = struct.unpack("<QIIIBBHQ", f.read(32))
        ent[h] = (off, csz, sz, tipo, sub, prim)
    return f, ent

def extrai(f, e):
    off, csz, sz, tipo, sub, prim = e
    f.seek(off); dados = f.read(csz)
    t = tipo & 0xF
    if t == 0: return dados
    if t == 1: return gzip.decompress(dados)
    if t in (3, 4):
        try:
            return zstandard.ZstdDecompressor().decompress(dados, max_output_size=sz)
        except Exception:
            # Bloco com sub-pedaços: pode haver trechos crus antes do quadro zstd.
            i = dados.find(b"\x28\xb5\x2f\xfd")
            return dados[:i] + zstandard.ZstdDecompressor().decompress(dados[i:], max_output_size=sz)
    raise ValueError(f"tipo {tipo}")

if __name__ == "__main__":
    wad, saida, lista = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3:]
    f, ent = ler_wad(wad)
    print(len(ent), "entradas")
    for p in lista:
        h = xxhash.xxh64(p.lower().encode()).intdigest()
        if h not in ent: print("não achei:", p); continue
        d = extrai(f, ent[h])
        out = saida / p.lower().split("/")[-1]; out.write_bytes(d)
        print(f"{out.name}: {len(d)} bytes (tipo {ent[h][3]})")
