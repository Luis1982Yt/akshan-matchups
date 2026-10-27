"""Monta, para cada matchup, a página de runas e o conjunto de itens que o app importa no cliente do LoL.

Grava src/guias/<guia>/importar.json:
  {slug: {"runas": [página, ...], "itens": [bloco, ...]}}
  página: {"primaryStyleId", "subStyleId", "selectedPerkIds"} no formato da API do cliente (/lol-perks/v1/pages),
          uma por opção de runas da planilha (Opção 1, Opção 2...);
  bloco:  {"tipo": rótulo em inglês, "tipo_pt": rótulo em português, "itens": ["3076", ...]} (/lol-item-sets).
O build junta tudo no guias-app.json, que o app baixa.

Formato completo (Mordekaiser, Illaoi): runas e itens saem do matchups.json, pelos ícones de cada peça.
Formato simples (Akshan): a planilha só traz a runa principal e as duas secundárias; o resto da árvore principal
e os fragmentos vêm de meta.json > paginas_padrao (combinado com o dono do site).
Precisa de internet (Data Dragon). Rode depois dos atualizar_*.py e do traducao_pt.py e antes do build.
"""
import itertools
import json
import pathlib
import re
import sys
import unicodedata
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
GUIAS = RAIZ / "src" / "guias"
sys.path.insert(0, str(RAIZ / "scripts"))
from versao_dd import VER  # noqa: E402

DD = "https://ddragon.leagueoflegends.com/cdn/"
# Fragmentos: id no cliente e as três linhas (Ataque, Flex, Defesa) em que cada um pode entrar.
FRAG = {"adaptativa": 5008, "vel_ataque": 5005, "aceleracao": 5007, "vel_movimento": 5010, "vida_nivel": 5001,
        "vida": 5011, "tenacidade": 5013}
LINHAS_FRAG = [{5008, 5005, 5007}, {5008, 5010, 5001}, {5011, 5013, 5001}]
FRAG_PADRAO = [5008, 5008, 5011]
PADROES_FRAG = [(r"scaling\s*health|health\s*scaling|vida\s*por\s*n", "vida_nivel"), (r"tenacity|slow\s*resist|tenacidade", "tenacidade"),
                (r"adap|adp", "adaptativa"), (r"attack\s*speed|velocidade\s*de\s*ataque", "vel_ataque"),
                (r"ability\s*haste|cdr|acelera", "aceleracao"), (r"move(ment)?\s*speed|\bms\b|velocidade\s*de\s*movimento", "vel_movimento"),
                (r"health|\bhp\b|vida", "vida")]
# Runas que saíram do jogo: no cliente entra a que ficou no lugar.
SUBSTITUTA = {"LegendTenacity": "Legend: Haste", "PhaseRush": "Stormraider's Surge"}


def baixa(caminho):
    with urllib.request.urlopen(DD + caminho, timeout=30) as r:
        return json.load(r)


def chave(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


class Runas:
    """Runas do Data Dragon: árvore e linha (0 = principal) de cada uma, achadas pelo ícone ou pelo nome."""

    def __init__(self, dados):
        self.por_icone, self.por_nome = {}, {}
        for arvore in dados:
            for linha, slot in enumerate(arvore["slots"]):
                for r in slot["runes"]:
                    info = {"id": r["id"], "arvore": arvore["id"], "linha": linha, "nome": r["name"]}
                    self.por_icone[r["icon"].split("perk-images/", 1)[-1]] = info
                    self.por_nome[chave(r["name"])] = info
                    self.por_nome[chave(r["name"].split(":")[-1])] = info

    def acha(self, peca):
        icone = (peca.get("icone") or "").split("perk-images/", 1)[-1]
        if icone in self.por_icone:
            return self.por_icone[icone]
        velha = next((n for k, n in SUBSTITUTA.items() if f"/{k}/" in "/" + icone), None)
        nome = velha or re.sub(r"\s+or$", "", peca.get("nome", ""), flags=re.I)
        return self.por_nome.get(chave(nome))


def fragmentos(nomes):
    """Nomes da planilha ("Double Adaptive -> Flat Health", "Tenacity / Slow Resist") -> 3 ids, um por linha."""
    tipos = []
    for nome in nomes:
        for parte in re.split(r"\s*(?:->|\+|,)\s*", nome):
            tipo = next((t for padrao, t in PADROES_FRAG if re.search(padrao, parte, re.I)), None)
            if tipo:
                tipos += [FRAG[tipo]] * (2 if re.search(r"double|dupla|x2", parte, re.I) else 1)
    # A planilha nem sempre segue a ordem das linhas ("Tenacity, Adaptive, Attack Speed"): fica a arrumação que
    # encaixa mais fragmentos, preferindo a ordem escrita; linha que sobrar leva o padrão.
    n = min(3, len(tipos))
    melhor, pontos = [None] * 3, -1
    for ordem in itertools.permutations(range(len(tipos)), n):
        escolha = [tipos[j] if j is not None and tipos[j] in LINHAS_FRAG[i] else None for i, j in enumerate(list(ordem) + [None] * (3 - n))]
        if sum(e is not None for e in escolha) > pontos:
            melhor, pontos = escolha, sum(e is not None for e in escolha)
    return [e if e is not None else FRAG_PADRAO[i] for i, e in enumerate(melhor)]


def pagina(principais, secundarias, frags):
    """Página válida no cliente, ou None. Com alternativas na planilha ("Second Wind OR..."), vale a primeira."""
    chave_runa = next((r for r in principais if r and r["linha"] == 0), None)
    if not chave_runa:
        return None
    arvore = chave_runa["arvore"]
    linhas = [next((r for r in principais if r and r["arvore"] == arvore and r["linha"] == n), None) for n in (1, 2, 3)]
    if None in linhas:
        return None
    sec = [r for r in secundarias if r and r["arvore"] != arvore and r["linha"] > 0]
    if not sec:
        return None
    sub = sec[0]["arvore"]
    duas = []
    for r in sec:
        if r["arvore"] == sub and all(r["linha"] != d["linha"] for d in duas):
            duas.append(r)
    if len(duas) < 2:
        return None
    return {"primaryStyleId": arvore, "subStyleId": sub,
            "selectedPerkIds": [chave_runa["id"]] + [r["id"] for r in linhas] + [r["id"] for r in duas[:2]] + frags}


class Itens:
    """Itens do Data Dragon: o id do ícone vira o id da Summoner's Rift (as versões de outros modos, 22xxxx, viram a normal)."""

    def __init__(self, dados):
        self.validos = {k for k, v in dados.items() if v.get("maps", {}).get("11") and v.get("gold", {}).get("purchasable")}

    def id(self, icone):
        m = re.search(r"/img/item/(\d+)\.png$", icone or "")
        if not m:
            return None
        i = m.group(1)
        for c in (i, i[2:] if len(i) == 6 else None):
            if c in self.validos:
                return c
        return None


def curto(rotulo, limite=90):
    """Rótulo do bloco na loja: corta numa palavra inteira se for longo demais."""
    rotulo = " ".join(rotulo.split())
    return rotulo if len(rotulo) <= limite else rotulo[:limite].rsplit(" ", 1)[0] + "…"


def blocos_completo(m, itens, textos):
    blocos = []
    for grupo in m["itens"]:
        cond = (grupo.get("rotulo") or "").strip()
        cond = "" if cond == "Items vs." else cond
        atual = {"rotulo": cond, "itens": []}
        partes = [atual]
        for l in grupo["linhas"]:
            if l["tipo"] in ("sep", "rotulo"):
                atual = {"rotulo": l.get("texto") or cond, "itens": []}
                partes.append(atual)
            elif l["tipo"] == "item":
                for passo in l["passos"]:
                    for p in passo:
                        i = itens.id(p.get("icone"))
                        if i and i not in atual["itens"]:
                            atual["itens"].append(i)
        for p in partes:
            if p["itens"]:
                en = re.sub(r":\s*$", "", p["rotulo"]) or "Build"
                pt = re.sub(r":\s*$", "", textos.get(p["rotulo"], p["rotulo"])) or "Build"
                blocos.append({"tipo": curto(en), "tipo_pt": curto(pt), "itens": p["itens"]})
    return blocos


def slug(nome):
    """A mesma regra da função slug() do src/template.html."""
    s = unicodedata.normalize("NFD", nome.lower())
    s = re.sub("[̀-ͯ]", "", s)
    s = re.sub("['’.]", "", s)
    return re.sub(r"\s+", "-", s)


def guia_completo(pasta, runas_, itens):
    dados = json.loads((pasta / "matchups.json").read_text(encoding="utf-8"))
    trad = pasta / "traducao_pt.json"
    textos = json.loads(trad.read_text(encoding="utf-8"))["textos"] if trad.exists() else {}
    saida, falhas = {}, []
    for m in dados["matchups"]:
        paginas = []
        for opcao in m["runas"]:
            parte = {l["rotulo"]: l["pecas"] for l in opcao}
            pg = pagina([runas_.acha(p) for p in parte.get("Principal", [])], [runas_.acha(p) for p in parte.get("Secundária", [])],
                        fragmentos([p["nome"] for p in parte.get("Fragmentos", [])]))
            if pg:
                paginas.append(pg)
            else:
                falhas.append(m["nome"])
        saida[slug(m["nome"])] = {"runas": paginas, "itens": blocos_completo(m, itens, textos)}
    return saida, falhas


def guia_simples(pasta, runas_, itens):
    """Akshan: a página padrão da runa principal (meta.json > paginas_padrao) com as duas secundárias da planilha."""
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    icones = json.loads((pasta / "icones_planilha.json").read_text(encoding="utf-8"))
    bruto = (pasta / "rows.js").read_text(encoding="utf-8").strip().rstrip(";")
    rows = json.loads(re.sub(r",\s*\]$", "]", bruto))
    padrao = meta.get("paginas_padrao", {})

    def pecas(nome, campo, valor):
        # Mesma regra do pecasDe() do template: imagens da planilha, escolha manual ou palavras conhecidas.
        p = icones.get(nome, {}).get(campo)
        if p and p["texto"] == valor and p["pecas"]:
            return p["pecas"]
        man = meta.get("pecas_manuais", {}).get(nome, {}).get(campo)
        if man and man["texto"] == valor:
            return man["pecas"]
        ks = [k for w in re.split(r"\s*[/,]\s*", re.sub(r"rush|!+", "", valor, flags=re.I)) for k in meta.get("texto_pecas", {}).get(w.strip().lower(), [])]
        return list(dict.fromkeys(ks))

    saida, falhas = {}, []
    for nome, runa, sec, _spell, bota, build, *_ in rows:
        principais = [runas_.acha(meta["pecas"][k]) for k in pecas(nome, "runa", runa) if k in meta["pecas"]]
        chave_runa = next((r for r in principais if r and r["linha"] == 0), None)
        base = padrao.get(chave_runa["nome"]) if chave_runa else None
        paginas = []
        if base:
            linhas = [runas_.por_nome.get(chave(n)) for n in base["linhas"]]
            secs = [runas_.acha(meta["pecas"][k]) for k in pecas(nome, "sec", sec) if k in meta["pecas"]]
            frags = [FRAG[f] for f in base["fragmentos"]]
            pg = pagina([chave_runa] + linhas, secs, frags)
            if pg:
                paginas.append(pg)
        if not paginas:
            falhas.append(nome)
        blocos = []
        for campo, valor, en, pt in (("bota", bota, "Boots", "Botas"), ("build", build, "Build", "Build")):
            ids = [i for i in (itens.id(meta["pecas"].get(k, {}).get("icone")) for k in pecas(nome, campo, valor)) if i]
            if ids:
                blocos.append({"tipo": en, "tipo_pt": pt, "itens": list(dict.fromkeys(ids))})
        saida[slug(nome)] = {"runas": paginas, "itens": blocos}
    return saida, falhas


def main():
    runas_ = Runas(baixa(f"{VER}/data/en_US/runesReforged.json"))
    itens = Itens(baixa(f"{VER}/data/en_US/item.json")["data"])
    for cfg in json.loads((RAIZ / "src" / "guias.json").read_text(encoding="utf-8")):
        pasta = RAIZ / "src" / cfg["dados"]
        saida, falhas = (guia_simples if cfg["formato"] == "simples" else guia_completo)(pasta, runas_, itens)
        (pasta / "importar.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
        com_runas = sum(1 for v in saida.values() if v["runas"])
        com_itens = sum(1 for v in saida.values() if v["itens"])
        print(f"{cfg['id']}: {len(saida)} matchups, {com_runas} com runas, {com_itens} com itens"
              + (f"; página incompleta na planilha: {sorted(set(falhas))}" if falhas else ""))


if __name__ == "__main__":
    main()
