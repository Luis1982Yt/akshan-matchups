"""Monta o guia do Garen mid a partir da planilha do Triton ("Season 15 Master Garen Mid Matchup Guide by Triton v1").

Uso: python scripts/atualizar_garen.py
A planilha bloqueia o download em xlsx, mas o Google ainda entrega cada aba em CSV (endpoint gviz), então dá para
atualizar sozinho no workflow diário. Gera src/guias/garen/matchups.json e paginas.json.

Aba "Matchups": uma linha por campeão com Difficulty (0 a 10, às vezes uma faixa como "3-5"), Max First, Spells (uma
dupla por linha, a primeira é a principal), Main Rune, 2nd/3rd Shards, Split? (Y/N/S) e Strat (dicas e, no fim, a
build: "CORE BUILD (ORDER): ..." e os itens situacionais com o motivo entre parênteses).
Aba "FAQ": legenda das notas, bans, plano de split, notas de botas e Conquistador e a página de runas (imagem,
transcrita em PAGINA_RUNAS com a troca que o próprio autor anotou: Manto de Nimbus -> Arcanista do Axioma).
A aba "Index" e as células de Twitch, Discord, coaching e agradecimentos são sobre o autor e ficam de fora.
"""
import json
import re

from atualizar_mordekaiser import chave, icone_fragmento
from guia_comum import APELIDO_CAMPEAO, APELIDO_ITEM, DD, FEITICO, Ddragon, csv_aba, dificuldade_10, gravar_guia, limpa

ID = '1896y14zn9YDA2c_AZWOkGa2Bwb1vCFIOf2EOTQ_o6VQ'
PLANILHA = f'https://docs.google.com/spreadsheets/d/{ID}/edit'
ABAS = {'matchups': 0, 'faq': 588252149}
PAGINA_RUNAS = (['Phase Rush', 'Axiom Arcanist', 'Celerity', 'Gathering Storm'], ['Demolish', 'Second Wind'])
SPLIT = {'Y': 'Split push', 'N': 'Team fight', 'S': 'Split push or team fight, depending on the game'}


def aba(nome):
    return csv_aba(ID, ABAS[nome])


def dificuldade(t):
    return dificuldade_10(t) if limpa(t) else {'overall': None, 'valor': None, 'texto': ''}


def icone_item(nome, por_item):
    base = limpa(nome).strip(' .')
    k = chave(APELIDO_ITEM.get(base.lower(), base))
    if k in por_item:
        return por_item[k]
    achados = [v for kk, v in por_item.items() if kk.startswith(k) and len(k) >= 5]
    return achados[0] if len(achados) == 1 else None


def peca(nome, por_item, faltando):
    achado = icone_item(nome, por_item)
    if not achado:
        faltando.add(nome)
        return {'nome': limpa(nome), 'icone': None}
    return {'nome': achado[0], 'icone': achado[1]}


def build(strat, por_item, faltando):
    """Separa as dicas da build. Devolve (dicas, grupos de itens no formato do site)."""
    m = re.search(r'(?:CORE\s*(?:BUILD|ITEMS)(?:\s*ORDER)?|\bORDER)\s*:', strat)
    if not m:
        return strat, []
    dicas, resto = strat[:m.start()], strat[m.end():]
    s = re.search(r'(?:SITUATIONAL[A-Za-z0-9 \-\n]*?ITEMS|SITUATIONAL|FINAL ITEMS|4TH-5TH ITEMS)\s*:', resto, re.I)
    nucleo, situ = (resto[:s.start()], resto[s.end():]) if s else (resto, '')
    nucleo = nucleo.replace("Swifties Tiamat", "Swifties, Tiamat")  # vírgula que faltou na planilha (só para ler)
    # Motivo entre parênteses no núcleo: fica junto do nome do item ("Hullbreaker (if splitting)").
    motivos = [f'{limpa(a).strip(" ,.")} ({limpa(b)})' for a, b in re.findall(r'([^,(]+?)\s*\(([^)]*)\)', nucleo)]
    nucleo = re.sub(r'\([^)]*\)', ',', nucleo).strip()
    # Frase em maiúsculas no fim ("ITEMIZE INTO ENEMY TEAM") é recado, não item.
    recado = re.search(r'\.\s*([A-Z][A-Z \-!\']{8,})$', nucleo)
    if recado:
        nucleo = nucleo[:recado.start()]
    nomes = []
    for pedaco in re.split(r'\s*,\s*', nucleo):
        # Quebra de linha na célula: dentro do nome de um item ("Dead\nMan's Plate", "Exe\ncutioner's") ou no
        # lugar da vírgula ("Swifties\nStridebreaker").
        partes = [x.strip(' .') for x in pedaco.split('\n')]
        juntos = [' '.join(partes), ''.join(partes)]
        inteiro = next((j for j in juntos if icone_item(j, por_item)), None)
        nomes += [inteiro] if inteiro else partes
    passos = []
    for nome in nomes:
        if nome:
            passos.append([peca(n, por_item, faltando) for n in re.split(r'\s*(?:/|\+|\bOR\b|\bor\b)\s*', nome) if n.strip()])
    linhas = [{'tipo': 'item', 'passos': passos}]
    if motivos:
        linhas[0]['motivo'] = ' · '.join(motivos)
    if recado:
        linhas.append({'tipo': 'nota', 'texto': recado.group(1).strip()})
    grupos = [{'rotulo': 'Core build', 'linhas': linhas}]
    # Situacionais: "Item (motivo) Item (motivo) ..."; o que sobra sem parênteses vira item (se for item) ou nota.
    situ = limpa(situ)
    if situ:
        linhas = []
        pos = 0
        for x in re.finditer(r'([^()]+?)\s*\(([^)]*)\)', situ):
            linhas += sobra(situ[pos:x.start()], por_item, faltando)
            nome = x.group(1).strip(' .,')
            if icone_item(nome, por_item):
                linhas.append({'tipo': 'item', 'passos': [[peca(nome, por_item, faltando)]], 'motivo': x.group(2).strip()})
            else:
                linhas.append({'tipo': 'nota', 'texto': f'{nome} ({x.group(2).strip()})'})
            pos = x.end()
        linhas += sobra(situ[pos:], por_item, faltando)
        grupos.append({'rotulo': 'Situational items', 'linhas': linhas})
    return dicas, grupos


def sobra(t, por_item, faltando):
    t = t.strip(' .,')
    if not t:
        return []
    nomes = [n.strip(' .') for n in re.split(r'\s*,\s*', t)]
    if all(icone_item(n, por_item) for n in nomes):
        return [{'tipo': 'item', 'passos': [[peca(n, por_item, faltando)]]} for n in nomes]
    return [{'tipo': 'nota', 'texto': t}]


def feiticos(t):
    duplas = []
    for linha in t.split('\n'):
        nomes = [FEITICO.get(x.strip().lower()) for x in linha.split('+') if x.strip()]
        if nomes and all(nomes):
            duplas.append(nomes)
    if not duplas:
        return [], ''
    pecas = [{'nome': n, 'icone': f'{DD}/img/spell/{arq}.png'} for n, arq in duplas[0]]
    outras = ', '.join(' + '.join(n for n, _ in d) for d in duplas[1:])
    return pecas, (f'Other options: {outras}' if outras else '')


def runas(fragmentos, conq, por_runa):
    principais, secundarias = PAGINA_RUNAS
    frags = ['Adaptive Force'] + [f.strip() for f in fragmentos.split('\n') if f.strip()]
    linhas = [{'rotulo': 'Principal', 'pecas': [{'nome': n, 'icone': por_runa.get(chave(n))} for n in principais]},
              {'rotulo': 'Secundária', 'pecas': [{'nome': n, 'icone': por_runa.get(chave(n))} for n in secundarias]},
              {'rotulo': 'Fragmentos', 'pecas': [{'nome': f, 'icone': icone_fragmento(f)} for f in frags]}]
    if conq:
        linhas[0]['nota'] = 'Conqueror is also an option in this matchup.'
    return [linhas]


def gerar_matchups(linhas, campeoes, por_item, por_runa):
    por_nome = {}
    for ch in campeoes.values():
        por_nome[chave(ch['name'])] = ch
        por_nome[chave(ch['id'])] = ch
    for k, v in APELIDO_CAMPEAO.items():
        por_nome[k] = campeoes[v]
    saida, faltando = [], set()
    for l in linhas[1:]:
        nome = limpa(l[0])
        if not nome:
            continue
        ch = por_nome[chave(nome)]  # falha se um campeão não for reconhecido
        dif, maximo, spells, runa, frags, split, strat = l[1:8]
        dodge = 'DODGE' in (spells + runa).upper()
        dicas, itens = build(strat, por_item, faltando)
        tldr = []
        if not dodge and re.fullmatch(r'[QWE](\s*/\s*[QWE])?', maximo.strip()):
            tldr.append('Max ' + ' or '.join(x.strip() for x in maximo.split('/')) + ' first')
        if split.strip() in SPLIT:
            tldr.append(SPLIT[split.strip()])
        pecas_f, texto_f = feiticos(spells) if not dodge else ([], '')
        m = {
            'nome': ch['name'], 'planilha': nome, 'id': ch['id'], 'titulo': ch['title'], 'rota': 'Mid',
            'dificuldade': ({'overall': 5, 'valor': 10, 'texto': 'Dodge'} if dodge else dificuldade(dif)),
            'tldr': tldr, 'feiticos': pecas_f,
            'runas': [] if dodge else runas(frags, 'conq' in runa.lower(), por_runa),
            'imagens_runas': [], 'itens': itens,
            'secoes': [{'titulo': 'Strategy', 'blocos': [{'tipo': 'p', 'texto': limpa(dicas)}]}] if limpa(dicas) else [],
        }
        if texto_f:
            m['feiticos_texto'] = texto_f
        saida.append(m)
    return saida, faltando


def p(texto):
    return {'tipo': 'p', 'texto': limpa(texto), 'links': []}


def gerar_paginas(faq, por_runa):
    c = lambda r, k: faq[r][k] if r < len(faq) and k < len(faq[r]) else ''
    # Coluna A: legenda das notas. Coluna B: só as notas de jogo (botas, Conquistador); Twitch, Discord, coaching e
    # agradecimentos são sobre o autor e não entram. Coluna C: bans. Coluna D: plano de split e de larvas.
    legenda = [{'texto': limpa(c(r, 0)), 'links': []} for r in range(1, 6) if limpa(c(r, 0))]
    principais, secundarias = PAGINA_RUNAS
    pagina = [{'titulo': 'Sorcery', 'itens': [{'nome': n, 'icone': por_runa.get(chave(n))} for n in principais]},
              {'titulo': 'Resolve', 'itens': [{'nome': n, 'icone': por_runa.get(chave(n))} for n in secundarias]}]
    bans = [limpa(c(r, 2)) for r in range(1, 3) if limpa(c(r, 2))]
    return [
        {'id': 'geral', 'titulo': 'Geral', 'titulo_en': 'Overview', 'blocos': [
            {'tipo': 'secao', 'titulo': limpa(c(0, 0)), 'partes': [{'tipo': 'lista', 'itens': legenda}]},
            {'tipo': 'secao', 'titulo': limpa(c(0, 3)), 'partes': [p(c(r, 3)) for r in range(1, 4) if limpa(c(r, 3))]},
            {'tipo': 'secao', 'titulo': limpa(c(0, 2)), 'partes': [p(x) for x in bans]},
            {'tipo': 'secao', 'titulo': 'Notes', 'partes': [p(c(r, 1)) for r in (3, 4) if limpa(c(r, 1))]},
        ]},
        {'id': 'runas', 'titulo': 'Runas', 'titulo_en': 'Runes', 'blocos': [
            {'tipo': 'secao', 'titulo': limpa(c(0, 4)), 'partes': [
                {'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': pagina}},
                p(c(2, 4))]},
        ]},
    ]


def main():
    linhas, faq = aba('matchups'), aba('faq')
    dd = Ddragon()
    matchups, faltando = gerar_matchups(linhas, dd.campeoes, dd.por_item, dd.por_runa)
    paginas = gerar_paginas(faq, dd.por_runa)
    gravar_guia('garen', matchups, paginas, {'planilha': PLANILHA, 'autor': 'Triton', 'twitch': 'https://www.twitch.tv/triton'})
    print(f'{len(matchups)} matchups, {len(paginas)} páginas' + (f'; itens sem ícone: {sorted(faltando)}' if faltando else ''))


if __name__ == '__main__':
    main()
