"""Monta o guia do Taric (suporte) com todas as matchups do jogo: um campeão inimigo por matchup.

Uso: python scripts/atualizar_taric.py
Ainda não há planilha (pedido do dono em 2026-11-23: criar a aba já, as notas vêm depois). Por enquanto o guia lista
todos os campeões do Data Dragon, sem notas, e o site avisa que está em construção. Quando a fonte das notas existir,
este script passa a ler dela (ver .claude/skills/guia-novo/SKILL.md) e junta as notas a cada campeão desta lista.
Campeão novo no jogo entra sozinho: o workflow diário roda este script.
O mono Taric escreve dicas e dificuldades pelo modo editor do site (api/taric.js grava em notas.json, e o workflow
taric-editor.yml roda este script e o build a cada mudança).
"""
import json
from pathlib import Path

from guia_comum import FEITICO, ROOT, Ddragon, gravar_guia

NOTAS = ROOT / "src/guias/taric/notas.json"  # o que já foi escrito para o guia (por enquanto, a tier list do dono)


def runas(dd, pagina):
    """Página de runas de um print do mono Taric (nomes em inglês, como no cliente). Runa sem ícone dá erro."""
    def peca(nome, icone):
        if not icone:
            raise KeyError(f"runa sem ícone: {nome}")
        return {"nome": nome, "icone": icone}
    return [[{"rotulo": "Principal", "pecas": [peca(n, dd.runa(n)) for n in pagina["principal"]]},
             {"rotulo": "Secundária", "pecas": [peca(n, dd.runa(n)) for n in pagina["secundaria"]]},
             {"rotulo": "Fragmentos", "pecas": [peca(n, dd.fragmento(n)) for n in pagina["fragmentos"]]}]]


NOME_FEITICO = {arq: nome for nome, arq in FEITICO.values()}


def feiticos(dd, arquivos):
    """['SummonerFlash', 'SummonerExhaust'] -> peças com ícone (o app importa pelo nome do arquivo do ícone)."""
    return [{"nome": NOME_FEITICO.get(a, a.replace("Summoner", "")), "icone": dd.feitico(a)} for a in arquivos]


def anotacoes(linhas):
    """Anotações do setup (itens, plano de jogo): aparecem no quadro de itens, uma por linha."""
    return [{"rotulo": "Build", "linhas": [{"tipo": "nota", "texto": l} for l in linhas]}] if linhas else []


def gerar_matchups(dd, notas):
    """Um campeão por matchup. Quem está na tier list de suportes ganha a dificuldade e a rota "Suporte"; quem está na
    tier list de atiradores do mono Taric (ou tem a tag Marksman do Data Dragon) ganha a rota "Atirador", para o filtro
    da lista e o 2x2 da bot lane. "adc" guarda a dificuldade como ADC inimigo (Ashe e Seraphine estão nas duas listas)."""
    dif, dif_adc, dicas = notas.get("dificuldade", {}), notas.get("dificuldade_adc", {}), notas.get("dicas", {})
    setup = notas.get("setup", {})  # runas, feitiços e anotações por campeão, do modo editor (vale mais que os prints)
    sinergia = notas.get("sinergia", {})
    lane = {}  # dificuldade da dupla (suporte|ADC) que o mono Taric marcou à mão; sem ela, o site faz a média
    for chave, v in notas.get("dificuldade_lane", {}).items():
        sup, adc = chave.split("|")
        lane.setdefault(sup, {})[adc] = v  # dicas jogando junto com esse ADC (escritas pelo modo editor do site)
    # Campeão em mais de um print (Zilean) fica com as duas páginas, como opções.
    runas_de = {}
    for p in notas.get("paginas_runas", []):
        for c in p["contra"]:
            runas_de.setdefault(c, []).extend(runas(dd, p))
    for c, e in setup.items():
        if e.get("runas"):
            runas_de[c] = runas(dd, e["runas"])
    saida = []
    for c in sorted(dd.campeoes.values(), key=lambda c: c["name"].lower()):
        sup, adc = dif.get(c["id"]), dif_adc.get(c["id"])
        atirador = adc is not None or "Marksman" in c.get("tags", [])
        rota = "Suporte" if sup else ("Atirador" if atirador else None)
        nota = sup or adc
        saida.append({
            "nome": c["name"], "planilha": c["name"], "id": c["id"], "titulo": c["title"],
            **({"rota": rota} if rota else {}),
            **({"adc": adc or True} if atirador else {}),
            **({"lane": lane[c["id"]]} if c["id"] in lane else {}),
            "dificuldade": {"overall": nota, "valor": nota, "texto": ""},
            **({"sinergia": [{"titulo": "", "blocos": [{"tipo": "lista", "itens": sinergia[c["id"]]}]}]} if sinergia.get(c["id"]) else {}),
            "tldr": dicas.get(c["id"], []), "feiticos": feiticos(dd, setup.get(c["id"], {}).get("feiticos", [])), "runas": runas_de.get(c["id"], []),
            "imagens_runas": [], "itens": anotacoes(setup.get(c["id"], {}).get("anotacoes", [])), "secoes": [],
        })
    falta = (set(dif) | set(dif_adc) | set(dicas) | set(sinergia) | set(setup) | set(runas_de) | set(lane)
            | {a for v in lane.values() for a in v}) - set(dd.campeoes)
    if falta:
        raise KeyError(f"campeão da tier list fora do Data Dragon: {sorted(falta)}")
    return saida


def main():
    dd = Ddragon()
    notas = json.loads(NOTAS.read_text(encoding="utf-8")) if NOTAS.exists() else {}
    matchups = gerar_matchups(dd, notas)
    gravar_guia("taric", matchups, [], {"planilha": "", "autor": ""})
    print(f"{len(matchups)} matchups (todos os campeões), {sum(1 for m in matchups if m['dificuldade']['overall'])} com dificuldade")


if __name__ == "__main__":
    main()
