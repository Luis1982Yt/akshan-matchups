"""Gera o index.html juntando src/template.html, os guias de src/guias.json e as fontes de src/fonts."""
import base64
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
    eu = next((m for m in dados["matchups"] if m["id"] == cfg["campeao"]), None)
    # Sem o espelho na planilha, o título vem do guias.json.
    campeao = {"id": cfg["campeao"], "nome": eu["nome"] if eu else cfg["campeao"], "titulo": eu["titulo"] if eu else cfg.get("titulo", ""),
               "titulo_en": cfg.get("titulo_en") or titulos_en.get(cfg["campeao"], "")}
    return {"campeao": campeao, "matchups": dados["matchups"],
            "traducao_pt": {"textos": camada.get("textos", {}), "nomes": camada.get("nomes", {})} if camada else None}


template = (SRC / "template.html").read_text(encoding="utf-8")
for marker in ("/*GUIAS*/", "/*FONTS*/", "/*IDS*/", "/*ICONE*/", "/*ICONE_APPLE*/"):
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


app = {"guias": [{"id": g["id"], "campeao": g["campeao"]["nome"], "chave": g.get("chave"), "rota": ROTA_LCU.get((g.get("rota") or "").lower()),
                  "matchups": matchups_app(g)} for g in guias]}
(ROOT / "guias-app.json").write_text(json.dumps(app, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")

html = template.replace("/*ICONE*/", icone("icone-64.png")).replace("/*ICONE_APPLE*/", icone("apple-180.png")).replace("/*IDS*/", json.dumps([g["id"] for g in guias])).replace("/*FONTS*/", font_faces()).replace(
    "/*GUIAS*/", json.dumps(guias, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
)
(ROOT / "index.html").write_text(html, encoding="utf-8", newline="\n")
print("index.html gerado: " + ", ".join(f"{g['campeao']['nome']} ({len(g['matchups'])})" for g in guias))
