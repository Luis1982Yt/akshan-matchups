"""Leitura de qualquer aba de uma planilha do Google exportada como xlsx: texto de cada célula e
as imagens presas às células (as abas de guia usam imagem no lugar do nome de item e de runa).

Só usa a biblioteca padrão, como scripts/icones_planilha.py.
"""
import hashlib
import html
import re
import zipfile


def publicado(html_aba):
    """Lê uma aba da versão publicada (htmlview/sheet?gid=...): {(linha, coluna): {"texto", "links"}}.
    É de onde vêm os links, que a exportação em xlsx perde."""
    import urllib.parse
    out = {}
    ocupado = set()  # células cobertas por rowspan de linhas de cima
    corpo = html_aba[html_aba.find("<tbody>"):]
    for m in re.finditer(r'<tr[^>]*><th id="\d+R(\d+)"[^>]*>.*?</th>(.*?)</tr>', corpo, re.S):
        r, col = int(m.group(1)), 0
        for td in re.finditer(r"<td([^>]*)>(.*?)</td>", m.group(2), re.S):
            while (r, col) in ocupado:
                col += 1
            attrs, dentro = td.groups()
            cs = int((re.search(r'colspan="(\d+)"', attrs) or [0, 1])[1])
            rs = int((re.search(r'rowspan="(\d+)"', attrs) or [0, 1])[1])
            for dr in range(1, rs):
                for dc in range(cs):
                    ocupado.add((r + dr, col + dc))
            links = []
            for href, txt in re.findall(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', dentro, re.S):
                href = html.unescape(href)
                if href.startswith("https://www.google.com/url?"):
                    href = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("q", [href])[0]
                links.append({"texto": html.unescape(re.sub(r"<[^>]+>", "", txt)).strip(), "url": href})
            texto = re.sub(r"<br\s*/?>", "\n", dentro)
            texto = html.unescape(re.sub(r"<[^>]+>", "", texto)).replace("\xa0", " ").strip()
            if texto or links:
                out[(r, col)] = {"texto": texto, "links": links}
            col += cs
    return out


class Planilha:
    def __init__(self, dados):
        import io
        self.z = zipfile.ZipFile(io.BytesIO(dados))
        self.nomes = set(self.z.namelist())
        self.strings = ["".join(re.findall(r"<t[^>]*>(.*?)</t>", s, re.S))
                        for s in re.findall(r"<si>(.*?)</si>", self._ler("xl/sharedStrings.xml"), re.S)]
        alvo = {}
        for t in re.findall(r"<Relationship [^>]*>", self._ler("xl/_rels/workbook.xml.rels")):
            alvo[re.search(r'Id="([^"]+)"', t).group(1)] = re.search(r'Target="([^"]+)"', t).group(1)
        self.abas = {}
        for tag in re.findall(r"<sheet [^>]*/>", self._ler("xl/workbook.xml")):
            nome = html.unescape(re.search(r'name="([^"]*)"', tag).group(1))
            self.abas[nome] = "xl/" + alvo[re.search(r'r:id="([^"]*)"', tag).group(1)].replace("/xl/", "").lstrip("/")

    def _ler(self, caminho):
        return self.z.read(caminho).decode("utf-8")

    def celulas(self, aba):
        """{(linha, coluna): texto}, contando do zero."""
        folha = self._ler(self.abas[aba])
        out = {}
        # Célula vazia vem como <c .../>, sem </c>.
        for ref, attrs, corpo in re.findall(r'<c r="([A-Z]+\d+)"([^>]*?)(?:/>|>(.*?)</c>)', folha, re.S):
            v = re.search(r"<v>(.*?)</v>", corpo or "", re.S)
            t = v and (self.strings[int(v.group(1))] if 't="s"' in attrs else v.group(1))
            if not t and corpo and "<is>" in corpo:
                t = "".join(re.findall(r"<t[^>]*>(.*?)</t>", corpo, re.S))
            if t:
                m = re.match(r"([A-Z]+)(\d+)", ref)
                col = 0
                for ch in m.group(1):
                    col = col * 26 + ord(ch) - 64
                out[(int(m.group(2)) - 1, col - 1)] = html.unescape(t).replace("\r\n", "\n")
        return out

    def links(self, aba):
        """{(linha, coluna): url} dos hyperlinks da aba."""
        folha = self._ler(self.abas[aba])
        rel = self.abas[aba].replace("worksheets/", "worksheets/_rels/") + ".rels"
        alvos = {}
        if rel in self.nomes:
            for t in re.findall(r"<Relationship [^>]*>", self._ler(rel)):
                alvos[re.search(r'Id="([^"]+)"', t).group(1)] = html.unescape(re.search(r'Target="([^"]+)"', t).group(1))
        out = {}
        for ref, rid in re.findall(r'<hyperlink [^>]*ref="([A-Z]+\d+)"[^>]*r:id="([^"]+)"', folha):
            m = re.match(r"([A-Z]+)(\d+)", ref)
            col = 0
            for ch in m.group(1):
                col = col * 26 + ord(ch) - 64
            if rid in alvos:
                out[(int(m.group(2)) - 1, col - 1)] = alvos[rid]
        return out

    def imagens(self, aba):
        """[(linha, coluna, deslocamento_x, md5, bytes)] das imagens presas às células, em ordem de leitura."""
        rel = self.abas[aba].replace("worksheets/", "worksheets/_rels/") + ".rels"
        if rel not in self.nomes:
            return []
        d = re.search(r'Target="([^"]*drawings/[^"]+)"', self._ler(rel))
        if not d:
            return []
        dpath = "xl/drawings/" + d.group(1).split("/")[-1]
        drels = dpath.replace("drawings/", "drawings/_rels/") + ".rels"
        if drels not in self.nomes:
            return []
        mapa = {}
        for t in re.findall(r"<Relationship [^>]*>", self._ler(drels)):
            m = re.search(r'media/([^"]+)"', t)
            if m:
                mapa[re.search(r'Id="([^"]+)"', t).group(1)] = m.group(1)
        out = []
        for a in re.findall(r"<xdr:(?:oneCellAnchor|twoCellAnchor)[^>]*>(.*?)</xdr:(?:oneCellAnchor|twoCellAnchor)>", self._ler(dpath), re.S):
            pos = re.search(r"<xdr:from><xdr:col>(\d+)</xdr:col><xdr:colOff>(-?\d+)</xdr:colOff><xdr:row>(\d+)</xdr:row>", a)
            emb = re.search(r'r:embed="([^"]+)"', a)
            if pos and emb and emb.group(1) in mapa:
                b = self.z.read("xl/media/" + mapa[emb.group(1)])
                out.append((int(pos.group(3)), int(pos.group(1)), int(pos.group(2)), hashlib.md5(b).hexdigest(), b))
        return sorted(out, key=lambda i: i[:3])
