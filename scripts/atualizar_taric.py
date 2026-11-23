"""Monta o guia do Taric (suporte) com todas as matchups do jogo: um campeão inimigo por matchup.

Uso: python scripts/atualizar_taric.py
Ainda não há planilha (pedido do dono em 2026-11-23: criar a aba já, as notas vêm depois). Por enquanto o guia lista
todos os campeões do Data Dragon, sem notas, e o site avisa que está em construção. Quando a fonte das notas existir,
este script passa a ler dela (ver .claude/skills/guia-novo/SKILL.md) e junta as notas a cada campeão desta lista.
Campeão novo no jogo entra sozinho: o workflow diário roda este script.
"""
from guia_comum import Ddragon, gravar_guia


def gerar_matchups(dd):
    saida = []
    for c in sorted(dd.campeoes.values(), key=lambda c: c["name"].lower()):
        saida.append({
            "nome": c["name"], "planilha": c["name"], "id": c["id"], "titulo": c["title"],
            "dificuldade": {"overall": None, "valor": None, "texto": ""},
            "tldr": [], "feiticos": [], "runas": [], "imagens_runas": [], "itens": [], "secoes": [],
        })
    return saida


def main():
    dd = Ddragon()
    matchups = gerar_matchups(dd)
    gravar_guia("taric", matchups, [], {"planilha": "", "autor": ""})
    print(f"{len(matchups)} matchups (todos os campeões), sem notas ainda")


if __name__ == "__main__":
    main()
