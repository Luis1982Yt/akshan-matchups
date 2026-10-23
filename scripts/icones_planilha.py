"""Lê as imagens coladas na planilha do Peteruso (exportada como xlsx) e diz quais ícones
aparecem em cada célula de runa, secundária, bota e build.

A exportação em CSV só traz o texto; as imagens só vêm no xlsx, como desenhos presos às
células. Cada imagem é reconhecida pelo md5 dos bytes, comparado com a tabela "imagens" do
meta.json (md5 -> peça). Imagem nova que não está na tabela volta em `desconhecidas`.
"""
import hashlib
import io
import re
import zipfile

# Coluna da planilha (0 = A) -> campo do site.
CAMPOS = {1: "runa", 2: "sec", 4: "bota", 5: "build"}


def _celulas(z):
    folha = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    largura = {}
    for mn, mx, w in re.findall(r'<col [^>]*min="(\d+)" max="(\d+)" width="([\d.]+)"', folha):
        for c in range(int(mn), int(mx) + 1):
            largura[c - 1] = float(w)
    altura = {int(r) - 1: float(h) for r, h in re.findall(r'<row r="(\d+)" ht="([\d.]+)"', folha)}
    # Larguras em caracteres e alturas em pontos, convertidas para EMU (a unidade dos desenhos).
    xs, ys = [0], [0]
    for c in range(30):
        xs.append(xs[-1] + (largura.get(c, 12.63) * 7 + 5) * 9525)
    for r in range(1000):
        ys.append(ys[-1] + altura.get(r, 15) * 12700)

    rels = {}
    for t in re.findall(r"<Relationship [^>]*>", z.read("xl/drawings/_rels/drawing1.xml.rels").decode("utf-8")):
        alvo = re.search(r'media/([^"]+)"', t)
        if alvo:
            rels[re.search(r'Id="([^"]+)"', t).group(1)] = alvo.group(1)
    desenho = z.read("xl/drawings/drawing1.xml").decode("utf-8")
    por_celula = {}
    for a in re.findall(r"<xdr:oneCellAnchor>(.*?)</xdr:oneCellAnchor>", desenho, re.S):
        pos = re.search(r"<xdr:from><xdr:col>(\d+)</xdr:col><xdr:colOff>(-?\d+)</xdr:colOff>"
                        r"<xdr:row>(\d+)</xdr:row><xdr:rowOff>(-?\d+)</xdr:rowOff>", a)
        emb = re.search(r'r:embed="([^"]+)"', a)
        ext = re.search(r'<xdr:ext cx="(\d+)" cy="(\d+)"', a)
        if not (pos and emb and ext) or emb.group(1) not in rels:
            continue
        col, col_off, row, row_off = map(int, pos.groups())
        # A imagem pertence à célula onde está o centro dela (algumas transbordam da âncora).
        x = xs[col] + col_off + int(ext.group(1)) / 2
        y = ys[row] + row_off + int(ext.group(2)) / 2
        c = max(i for i in range(len(xs)) if xs[i] <= x)
        r = max(i for i in range(len(ys)) if ys[i] <= y)
        por_celula.setdefault((r, c), []).append((x, rels[emb.group(1)]))
    return por_celula


def icones_da_planilha(xlsx, imagens):
    """xlsx: bytes do arquivo. imagens: {md5: chave da peça}.
    Devolve ({campeão: {campo: {"texto": ..., "pecas": [chaves]}}}, [(campeão, campo, md5)])."""
    z = zipfile.ZipFile(io.BytesIO(xlsx))
    strings = ["".join(re.findall(r"<t[^>]*>(.*?)</t>", s, re.S))
               for s in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8"), re.S)]
    folha = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    texto = {}
    # Célula vazia vem como <c .../>, sem </c>.
    for ref, attrs, corpo in re.findall(r'<c r="([A-Z]+\d+)"([^>]*?)(?:/>|>(.*?)</c>)', folha, re.S):
        v = re.search(r"<v>(.*?)</v>", corpo, re.S)
        if v:
            bruto = strings[int(v.group(1))] if 't="s"' in attrs else v.group(1)
            texto[ref] = (bruto.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                          .replace("&quot;", '"').replace("&#39;", "'").strip())
    por_celula = _celulas(z)
    md5 = {}
    resultado, desconhecidas = {}, []
    for r in range(1, 1000):
        nome = texto.get(f"A{r + 1}")
        if not nome:
            continue
        campos = {}
        for c, campo in CAMPOS.items():
            letra = "ABCDEFGH"[c]
            pecas = []
            for _, arquivo in sorted(por_celula.get((r, c), [])):
                if arquivo not in md5:
                    md5[arquivo] = hashlib.md5(z.read("xl/media/" + arquivo)).hexdigest()
                chave = imagens.get(md5[arquivo])
                if chave is None:
                    desconhecidas.append((nome, campo, md5[arquivo]))
                elif chave not in pecas:  # a planilha tem imagens repetidas empilhadas
                    pecas.append(chave)
            campos[campo] = {"texto": texto.get(f"{letra}{r + 1}", ""), "pecas": pecas}
        resultado[nome] = campos
    return resultado, desconhecidas
