"""Monta o guia do Taric (suporte) com todas as matchups do jogo: um campeão inimigo por matchup.

Uso: python scripts/atualizar_taric.py
Ainda não há planilha (pedido do dono em 2026-11-23: criar a aba já, as notas vêm depois). Por enquanto o guia lista
todos os campeões do Data Dragon, sem notas, e o site avisa que está em construção. Quando a fonte das notas existir,
este script passa a ler dela (ver .claude/skills/guia-novo/SKILL.md) e junta as notas a cada campeão desta lista.
Campeão novo no jogo entra sozinho: o workflow diário roda este script.
"""
import json
from pathlib import Path

from guia_comum import ROOT, Ddragon, gravar_guia

NOTAS = ROOT / "src/guias/taric/notas.json"  # o que já foi escrito para o guia (por enquanto, a tier list do dono)


def gerar_matchups(dd, notas):
    """Um campeão por matchup. Quem está na tier list (os suportes) ganha a dificuldade e a rota "Suporte"; os
    atiradores (tag Marksman do Data Dragon) ganham a rota "Atirador", para o filtro da lista e o 2x2 da bot lane."""
    dif = notas.get("dificuldade", {})
    saida = []
    for c in sorted(dd.campeoes.values(), key=lambda c: c["name"].lower()):
        nota = dif.get(c["id"])
        rota = "Suporte" if nota else ("Atirador" if "Marksman" in c.get("tags", []) else None)
        saida.append({
            "nome": c["name"], "planilha": c["name"], "id": c["id"], "titulo": c["title"],
            **({"rota": rota} if rota else {}),
            "dificuldade": {"overall": nota, "valor": nota, "texto": ""},
            "tldr": [], "feiticos": [], "runas": [], "imagens_runas": [], "itens": [], "secoes": [],
        })
    return saida


def main():
    dd = Ddragon()
    notas = json.loads(NOTAS.read_text(encoding="utf-8")) if NOTAS.exists() else {}
    matchups = gerar_matchups(dd, notas)
    gravar_guia("taric", matchups, [], {"planilha": "", "autor": ""})
    print(f"{len(matchups)} matchups (todos os campeões), {sum(1 for m in matchups if m['dificuldade']['overall'])} com dificuldade")


if __name__ == "__main__":
    main()
