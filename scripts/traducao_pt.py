"""Camada em português dos guias que vêm em inglês (Mordekaiser, Illaoi).

Grava src/guias/<guia>/traducao_pt.json com:
  textos: frase original da planilha (exatamente como está no matchups.json / paginas.json) -> português.
          A tradução é feita à mão; o script só guarda as que ainda aparecem no guia e lista as que faltam.
  nomes:  ícone -> nome do item / runa no cliente em português (Data Dragon pt_BR).
  titulos_en: id do campeão -> título em inglês (a planilha só traz o título em português).

Uso:
  python scripts/traducao_pt.py                 atualiza os nomes e mostra quantas frases estão sem tradução
  python scripts/traducao_pt.py --faltando      lista as frases sem tradução (para traduzir e pôr em "textos")
  python scripts/traducao_pt.py --importar DIR  junta pares NN.json ([id, origem, texto]) + NN_pt.json ({id: pt})

Frase nova na planilha sem tradução aparece em inglês no modo PT até alguém traduzir.
"""
import glob
import json
import pathlib
import re
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
GUIAS = RAIZ / "src" / "guias"
VER = re.search(r'VER = "([\d.]+)"', (RAIZ / "src" / "template.html").read_text(encoding="utf-8")).group(1)
DD = "https://ddragon.leagueoflegends.com/cdn/"
# Chaves que não são texto para traduzir (endereços, ícones, ids) e os campos do campeão da matchup.
PULA = {"url", "icone", "id", "src", "versao", "fonte", "chave", "largura", "altura", "tipo"}
PULA_MATCHUP = {"nome", "planilha", "titulo", "id"}


def textos_do_guia(guia):
    """Todas as frases do guia que o site mostra (mesma regra do template: tem palavra de 3+ letras)."""
    achadas = []

    def anda(x, chave=None, nivel_matchup=False):
        if isinstance(x, str):
            if chave not in PULA and re.search(r"[A-Za-z]{3,}", x) and not re.fullmatch(r"\s*https?://\S+\s*", x):
                achadas.append(x)
        elif isinstance(x, list):
            for y in x:
                anda(y, chave)
        elif isinstance(x, dict):
            # Peça com ícone (ou item com id) usa o nome do jogo (nomes), não precisa de tradução escrita.
            # Fragmento tem ícone mas o nome é o que o autor escreveu ("Double Adaptive"): esse é traduzido.
            nome_do_jogo = (x.get("icone") and "/StatMods/" not in x["icone"]) or x.get("id") and "estagios" in x or x.get("id") and "nome" in x and len(x) <= 3
            for k, v in x.items():
                if nivel_matchup and k in PULA_MATCHUP:
                    continue
                if nome_do_jogo and k == "nome":
                    continue
                # Linha de item: o site mostra as peças (passos), não o texto cru da célula.
                if x.get("tipo") == "item" and k == "texto":
                    continue
                anda(v, k)

    pasta = GUIAS / guia
    for m in json.loads((pasta / "matchups.json").read_text(encoding="utf-8"))["matchups"]:
        anda(m, nivel_matchup=True)
    if (pasta / "paginas.json").exists():
        anda(json.loads((pasta / "paginas.json").read_text(encoding="utf-8")))
    vistos = set()
    return [t for t in achadas if not (t in vistos or vistos.add(t))]


def icones_do_guia(guia):
    """Ícones de item e runa usados no guia (inclusive itens da página de itens, que só têm o id)."""
    pasta = GUIAS / guia
    bruto = (pasta / "matchups.json").read_text(encoding="utf-8")
    if (pasta / "paginas.json").exists():
        pag = (pasta / "paginas.json").read_text(encoding="utf-8")
        bruto += pag
        for b in (bl for p in json.loads(pag) for bl in p["blocos"] if bl["tipo"] == "itens"):
            for g in b["grupos"]:
                for it in g["itens"]:
                    bruto += f' "{DD}{VER}/img/item/{it["id"]}.png" '
                    bruto += " ".join(f'"{DD}{VER}/img/item/{e["id"]}.png"' for e in it["estagios"] if e and e.get("id"))
    return set(re.findall(r'"(https://ddragon\.leagueoflegends\.com/cdn/[^"]+\.png)"', bruto))


def baixa(caminho):
    with urllib.request.urlopen(DD + caminho, timeout=30) as r:
        return json.load(r)


def nomes_pt(icones):
    itens = baixa(f"{VER}/data/pt_BR/item.json")["data"]
    runas = {}
    # A versão antiga entra primeiro: runas que saíram do jogo (Lenda: Tenacidade, Ímpeto Gradual) ainda têm nome.
    for arvore in baixa("13.24.1/data/pt_BR/runesReforged.json") + baixa(f"{VER}/data/pt_BR/runesReforged.json"):
        runas["perk-images/" + arvore["icon"].split("perk-images/", 1)[-1]] = arvore["name"]
        for s in arvore["slots"]:
            for r in s["runes"]:
                runas[r["icon"]] = r["name"]
    nomes = {}
    for url in sorted(icones):
        m = re.search(r"/img/item/(\d+)\.png$", url)
        if m and m.group(1) in itens:
            nomes[url] = itens[m.group(1)]["name"]
            continue
        m = re.search(r"/img/(perk-images/.+\.png)$", url)
        if m and m.group(1) in runas:
            nomes[url] = runas[m.group(1)]
    return nomes


def importa(pasta):
    """Junta as traduções feitas em lote: NN.json ([id, origem, texto]) com NN_pt.json ({id: pt})."""
    pares = {}
    for f in sorted(glob.glob(str(pathlib.Path(pasta) / "*_pt.json"))):
        fonte = pathlib.Path(f.replace("_pt.json", ".json"))
        pt = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        for i, _, texto in json.loads(fonte.read_text(encoding="utf-8")):
            if str(i) in pt:
                pares[texto] = pt[str(i)]
    return pares


def main():
    novos, iguais_novos = {}, []
    if "--importar" in sys.argv:
        pasta = pathlib.Path(sys.argv[sys.argv.index("--importar") + 1])
        novos = importa(pasta)
        if (pasta / "iguais.json").exists():
            iguais_novos = json.loads((pasta / "iguais.json").read_text(encoding="utf-8"))
    for cfg in json.loads((RAIZ / "src" / "guias.json").read_text(encoding="utf-8")):
        if cfg["formato"] != "completo":
            continue
        guia = cfg["dados"].split("/")[-1]
        arq = GUIAS / guia / "traducao_pt.json"
        atual = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {"textos": {}, "nomes": {}}
        todos = {**atual["textos"], **novos}
        frases = textos_do_guia(guia)
        textos = {t: todos[t] for t in frases if t in todos and todos[t] != t}
        # "iguais": nomes, perfis e siglas que ficam iguais em PT (só para não aparecerem como faltando).
        iguais = sorted({t for t in [*atual.get("iguais", []), *iguais_novos, *(t for t in todos if todos[t] == t)] if t in frases and t not in textos})
        try:
            nomes = nomes_pt(icones_do_guia(guia))
            ids = {m["id"] for m in json.loads((GUIAS / guia / "matchups.json").read_text(encoding="utf-8"))["matchups"]}
            titulos = {c["id"]: c["title"] for c in baixa(f"{VER}/data/en_US/champion.json")["data"].values()
                       if c["id"] in ids or c["name"] == cfg["campeao"]}
        except OSError as e:
            print(f"{guia}: sem Data Dragon ({e}), mantém os nomes que já tinha")
            nomes, titulos = atual.get("nomes", {}), atual.get("titulos_en", {})
        arq.write_text(json.dumps({"textos": textos, "nomes": nomes, "titulos_en": titulos, "iguais": iguais},
                                  ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
        faltando = [t for t in frases if t not in textos and t not in iguais]
        print(f"{guia}: {len(textos)} frases traduzidas, {len(nomes)} nomes, {len(faltando)} sem tradução")
        if "--faltando" in sys.argv:
            for t in faltando:
                print("   ", json.dumps(t, ensure_ascii=False)[:160])


if __name__ == "__main__":
    main()
