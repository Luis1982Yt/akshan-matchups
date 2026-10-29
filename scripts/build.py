"""Gera o index.html juntando src/template.html, os guias de src/guias.json e as fontes de src/fonts."""
import base64
import html as html_lib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# Fontes embutidas no próprio HTML, para o site funcionar em file:// e sem internet.
FONTS = [
    ("Cinzel", "normal", "500 800", "Cinzel-normal.woff2"),
    ("Hanken Grotesk", "normal", "400 700", "HankenGrotesk-normal.woff2"),
    ("Hanken Grotesk", "italic", "400", "HankenGrotesk-italic.woff2"),
]


def font_faces():
    faces = []
    for family, style, weight, file in FONTS:
        data = base64.b64encode((SRC / "fonts" / file).read_bytes()).decode("ascii")
        faces.append(
            f'@font-face {{ font-family: "{family}"; font-style: {style}; font-weight: {weight}; '
            f'font-display: swap; src: url(data:font/woff2;base64,{data}) format("woff2"); }}'
        )
    return "\n".join(faces)


def icone(arquivo):
    """Ícone da aba (src/icone) embutido como data URI, como as fontes."""
    return "data:image/png;base64," + base64.b64encode((SRC / "icone" / arquivo).read_bytes()).decode("ascii")


def guia_simples(cfg, pasta):
    """Planilha no formato do Akshan: [campeão, runa, secundária, feitiço, bota, build, lembrete, noGuia]."""
    bruto = (pasta / "rows.js").read_text(encoding="utf-8").strip().rstrip(";")
    rows = json.loads(re.sub(r",\s*\]$", "]", bruto))
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    eu = meta["champs"][cfg["campeao"]]
    traducao = pasta / "traducao_en.json"
    planilha = pasta / "icones_planilha.json"
    return {"campeao": {"id": eu["id"], "nome": cfg["campeao"], "titulo": eu["title"], "titulo_en": eu.get("title_en", "")},
            "champs": meta["champs"], "icones": meta["icons"], "matchups": rows,
            "pecas": meta.get("pecas", {}), "texto_pecas": meta.get("texto_pecas", {}), "pecas_manuais": meta.get("pecas_manuais", {}), "feitico_extra": meta.get("feitico_extra", {}),
            "icones_planilha": json.loads(planilha.read_text(encoding="utf-8")) if planilha.exists() else {},
            "traducao": json.loads(traducao.read_text(encoding="utf-8")) if traducao.exists() else None}


def guia_completo(cfg, pasta):
    """Planilha já separada por scripts/atualizar_<campeão>.py em matchups.json."""
    dados = json.loads((pasta / "matchups.json").read_text(encoding="utf-8"))
    # Camada em português (scripts/traducao_pt.py): frases traduzidas, nomes do cliente em PT e títulos em inglês.
    arq = pasta / "traducao_pt.json"
    camada = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    titulos_en = camada.get("titulos_en", {})
    for m in dados["matchups"]:
        m["titulo_en"] = titulos_en.get(m["id"], "")
    # "id_campeao" quando o nome não é o id da Riot (K'Sante -> KSante); é o que monta as imagens do Data Dragon.
    cid = cfg.get("id_campeao", cfg["campeao"])
    eu = next((m for m in dados["matchups"] if m["id"] == cid), None)
    # Sem o espelho na planilha, o título vem do guias.json.
    campeao = {"id": cid, "nome": eu["nome"] if eu else cfg["campeao"], "titulo": eu["titulo"] if eu else cfg.get("titulo", ""),
               "titulo_en": cfg.get("titulo_en") or titulos_en.get(cid, "")}
    return {"campeao": campeao, "matchups": dados["matchups"],
            "traducao_pt": {"textos": camada.get("textos", {}), "nomes": camada.get("nomes", {})} if camada else None}


def _normal(t):
    return re.sub(r"\s+", " ", (t or "")).strip().lower()


def curar(paginas, cur):
    """Curadoria das páginas do guia (src/guias/<guia>/curadoria.json), aplicada aqui para a atualização diária não desfazer.
    O site é para aprender a matchup: sai o que é sobre o criador da planilha (bio, redes, Discord pessoal, doação,
    aviso de beta, prints de ranking) e o que é útil mas está em primeira pessoa vira texto neutro.
      "remover": começos de texto; some o texto, a imagem (pela legenda), o item de lista ou a seção inteira (pelo título).
      "trocar": {começo do texto original: {"en": texto novo, "pt": tradução}} (os links do original continuam).
    Devolve as páginas curadas e as traduções PT dos textos novos. As notas das matchups não passam por aqui."""
    remover = [_normal(x) for x in cur.get("remover", [])]
    trocar = [(_normal(k), v) for k, v in cur.get("trocar", {}).items()]
    usados, pt = set(), {}

    def bate(t):
        n = _normal(t)
        achado = next((r for r in remover if n and n.startswith(r)), None)
        if achado:
            usados.add(achado)
        return bool(achado)

    def troca(x):
        if isinstance(x, dict):
            for k in ("texto", "titulo"):
                if isinstance(x.get(k), str):
                    n = _normal(x[k])
                    for chave, novo in trocar:
                        if n and n.startswith(chave):
                            usados.add(chave)
                            x[k] = novo["en"]
                            if novo.get("pt"):
                                pt[novo["en"]] = novo["pt"]
                            break
            for v in x.values():
                troca(v)
        elif isinstance(x, list):
            for v in x:
                troca(v)

    def bloco(b):
        """O bloco curado, ou None se ele sai inteiro."""
        if bate(b.get("titulo")) or (b["tipo"] in ("texto", "aviso", "lista") and bate(b.get("texto"))):
            return None
        if "itens" in b and b["tipo"] == "lista":
            antes = len(b["itens"])
            b["itens"] = [i for i in b["itens"] if not bate(i.get("texto"))]
            if antes and not b["itens"]:
                return None
        if b["tipo"] == "secao":
            partes = []
            for x in b["partes"]:
                if x["tipo"] in ("p", "sub") and bate(x.get("texto")):
                    continue
                if x["tipo"] == "lista":
                    x["itens"] = [i for i in x["itens"] if not bate(i.get("texto"))]
                    if not x["itens"]:
                        continue
                if x["tipo"] == "imagens":
                    x["imagens"] = [i for i in x["imagens"] if not bate(i.get("legenda"))]
                    if not x["imagens"]:
                        continue
                if x["tipo"] == "bloco":
                    x["bloco"] = bloco(x["bloco"])
                    if not x["bloco"]:
                        continue
                partes.append(x)
            b["partes"] = partes
            if not partes:
                return None
        return b

    for pg in paginas:
        pg["blocos"] = [b for b in (bloco(b) for b in pg["blocos"]) if b]
    troca(paginas)
    sobrando = [r for r in remover + [k for k, _ in trocar] if r not in usados]
    if sobrando:
        print("  curadoria: textos que não existem mais na planilha (confira o curadoria.json):", sobrando)
    return paginas, pt


template = (SRC / "template.html").read_text(encoding="utf-8")
for marker in ("/*GUIAS*/", "/*FONTS*/", "/*IDS*/", "/*ICONE*/", "/*ICONE_APPLE*/", "/*TITULO_OG*/", "/*VER_DD*/"):
    if template.count(marker) != 1:
        raise SystemExit(f"O template precisa ter exatamente um {marker}")

guias = []
for cfg in json.loads((SRC / "guias.json").read_text(encoding="utf-8")):
    if cfg.get("oculto"):
        continue  # guia guardado, fora do site por enquanto
    pasta = SRC / cfg["dados"]
    montar = guia_simples if cfg["formato"] == "simples" else guia_completo
    g = {**{k: v for k, v in cfg.items() if k != "dados"}, **montar(cfg, pasta)}
    # Outras abas da planilha do autor (itens, runas, criadores...), gravadas por scripts/paginas_<campeão>.py.
    if (pasta / "paginas.json").exists():
        g["paginas"] = json.loads((pasta / "paginas.json").read_text(encoding="utf-8"))
        if (pasta / "curadoria.json").exists():
            print(f"{cfg['id']}:")
            g["paginas"], pt = curar(g["paginas"], json.loads((pasta / "curadoria.json").read_text(encoding="utf-8")))
            if g.get("traducao_pt"):
                g["traducao_pt"]["textos"].update(pt)
    guias.append(g)

# Lista para o app da seleção de campeões (app/akshan_app.py): de qual campeão é cada guia, a rota
# e as matchups com o mesmo slug do site. O app baixa este arquivo, então guia novo já funciona nele.
ROTA_LCU = {"top": "TOP", "jungle": "JUNGLE", "mid": "MIDDLE", "adc": "BOTTOM", "bot": "BOTTOM", "sup": "UTILITY", "support": "UTILITY"}


def slug(nome):
    """A mesma regra da função slug() do src/template.html."""
    import unicodedata
    s = unicodedata.normalize("NFD", nome.lower())
    s = re.sub("[̀-ͯ]", "", s)
    s = re.sub("['’.]", "", s)
    return re.sub(r"\s+", "-", s)


def matchups_app(g):
    if g["formato"] == "simples":
        return [[r[0], g["champs"][r[0]]["id"], slug(r[0])] for r in g["matchups"]]
    return [[m["nome"], m["id"], slug(m["nome"])] for m in g["matchups"]]


# Página de runas e conjunto de itens de cada matchup para o app importar no cliente (scripts/importar_lol.py).
PASTAS = {c["id"]: SRC / c["dados"] for c in json.loads((SRC / "guias.json").read_text(encoding="utf-8"))}


def importar_app(g):
    arq = PASTAS[g["id"]] / "importar.json"
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}


app = {"guias": [{"id": g["id"], "campeao": g["campeao"]["nome"], "chave": g.get("chave"), "rota": ROTA_LCU.get((g.get("rota") or "").lower()),
                  "matchups": matchups_app(g), "importar": importar_app(g)} for g in guias]}
(ROOT / "guias-app.json").write_text(json.dumps(app, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")

# Descrição para buscadores e para a prévia do link (WhatsApp, Discord, X), com todos os guias publicados.
def em_lista(itens):
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1]


descricao = ("Guias de matchup de League of Legends com as notas de quem joga: "
             + em_lista([f"{g['campeao']['nome']} {(g.get('rota') or '').lower()} ({g['autor']})" if g.get('autor') else f"{g['campeao']['nome']} {(g.get('rota') or '').lower()}" for g in guias])
             + ". Runas, build, cooldowns e como jogar cada confronto, em português e inglês.")
titulo_og = "Guias de matchup · " + em_lista([g["campeao"]["nome"] for g in guias])
og_alt = "Faixas das splash arts de " + em_lista([g["campeao"]["nome"] for g in guias]) + " ao lado do título Guias de matchup"
template = template.replace("/*DESCRICAO*/", html_lib.escape(descricao)).replace("/*TITULO_OG*/", html_lib.escape(titulo_og)).replace("/*OG_ALT*/", html_lib.escape(og_alt)).replace(
    "/*VER_DD*/", (SRC / "versao_dd.txt").read_text(encoding="utf-8").strip())

html = template.replace("/*ICONE*/", icone("icone-64.png")).replace("/*ICONE_APPLE*/", icone("apple-180.png")).replace("/*IDS*/", json.dumps([g["id"] for g in guias])).replace("/*FONTS*/", font_faces()).replace(
    "/*GUIAS*/", json.dumps(guias, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
)
(ROOT / "index.html").write_text(html, encoding="utf-8", newline="\n")
print("index.html gerado: " + ", ".join(f"{g['campeao']['nome']} ({len(g['matchups'])})" for g in guias))
