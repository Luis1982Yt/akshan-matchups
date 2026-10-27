"""Importa o Excel original de UJard, preservando textos e imagens sem OCR.

Uso: python scripts/atualizar_kayle.py [caminho.xlsx]
Sem argumento, baixa o arquivo original público. Requer Pillow.
"""
import argparse
from collections import defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import re
import urllib.request

from PIL import Image

from atualizar_mordekaiser import chave, montar_icones
from planilha_xlsx import Planilha
from versao_dd import VER

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'src/guias/kayle'
IMAGENS = ROOT / 'imagens/kayle'
FONTE = 'https://drive.google.com/uc?export=download&id=1xxu7pVNnshjdwiSmwZrs9K4rEwfhIQL3'
DD = f'https://ddragon.leagueoflegends.com/cdn/{VER}'
PAGINAS = [
    ('runas', 'Runas', 'Runes'), ('itens', 'Itens', 'Builds'),
    ('macro', 'Macro e gameplay', 'Macro and Gameplay'),
    ('dicas', 'Dicas', 'Tips and Tricks'),
    ('habilidades', 'Habilidades', 'Ability Maxing'),
    ('ameacas', 'Ameaças', 'Problematic Enemy Champions'),
    ('inspiracao', 'Inspiração', 'Why Inspiration Secondary'),
    ('notas', 'Notas', 'Notes'),
]
SPELLS = {'Flash': 'SummonerFlash', 'Ghost': 'SummonerHaste',
          'Teleport': 'SummonerTeleport', 'Ignite': 'SummonerDot',
          'Cleanse': 'SummonerBoost', 'Exhaust': 'SummonerExhaust'}


def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as resposta:
        return resposta.read()


def dificuldade(texto):
    numeros = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', texto)]
    if not numeros:
        return {'overall': None, 'valor': None, 'texto': texto}
    if any(not 1 <= n <= 10 for n in numeros):
        raise ValueError(f'Dificuldade inválida: {texto!r}')
    return {'overall': math.ceil(max(numeros) / 2), 'valor': max(numeros),
            'texto': f'{float(texto):g}/10' if re.fullmatch(r'\d+(?:\.\d+)?', texto) else texto}


def salvar_imagem(dados, alt, pasta):
    """PNG em resolução original, identificado pelo conteúdo PNG, sem perdas."""
    with Image.open(io.BytesIO(dados)) as original:
        im = original.convert('RGBA')
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
    png = buf.getvalue()
    nome = hashlib.sha256(png).hexdigest() + '.png'
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / nome
    if not destino.exists():
        destino.write_bytes(png)
    return {'src': f'imagens/kayle/{nome}', 'alt': alt,
            'largura': im.width, 'altura': im.height}


def celula(texto, link=None):
    return {'texto': texto, 'links': [{'texto': texto, 'url': link}] if link else []}


def texto_bloco(texto, link=None):
    return {'tipo': 'texto', **celula(texto, link)}


def runas(texto_principal, texto_secundario, por_runa):
    """Somente nomes explicitamente escritos; nunca completa uma página."""
    if not texto_principal and not texto_secundario:
        return []
    principal = texto_principal.rstrip('.')
    secundarias = []
    conhecidos = {
        'Jack': 'Jack Of All Trades', 'Triple Tonic': 'Triple Tonic',
        'Second Wind': 'Second Wind', 'Overgrowth': 'Overgrowth',
        'Bone Plating': 'Bone Plating', 'Unflinching': 'Unflinching',
        'Celerity': 'Celerity', 'Gathering Storm': 'Gathering Storm', 'GS': 'Gathering Storm',
    }
    for escrito, nome in conhecidos.items():
        if re.search(r'\b' + re.escape(escrito) + r'\b', texto_secundario):
            if not any(p['nome'] == nome for p in secundarias):
                secundarias.append({'nome': nome, 'icone': por_runa.get(chave(nome))})
    return [[{'rotulo': 'Principal', 'pecas': [
        {'nome': principal, 'icone': por_runa.get(chave(principal))}]},
        {'rotulo': 'Secundária', 'texto': texto_secundario, 'pecas': secundarias}]]


def gerar_matchups(xl, campeoes, por_runa, pasta=IMAGENS):
    aba = next(iter(xl.abas))
    c = xl.celulas(aba)
    imagens = defaultdict(list)
    for r, col, _, _, dados in xl.imagens(aba):
        if col == 7 and 6 <= r < 177:
            imagens[r].append(salvar_imagem(
                dados, f'Minor runes — {c[r, 2]} — UJard (original spreadsheet)', pasta))
    por_nome = {}
    for ch in campeoes.values():
        por_nome[chave(ch['name'])] = ch
        por_nome[chave(ch['id'])] = ch
    por_nome['wukong'] = por_nome['monkeyking']
    por_nome['nunu'] = por_nome['nunuwillump'] if 'nunuwillump' in por_nome else por_nome['nunu']
    saida = []
    for r in range(6, 177):
        nome = c[r, 2]
        ch = por_nome[chave(nome)]  # falha explicitamente se um campeão não for reconhecido
        get = lambda col: c.get((r, col), '')
        feiticos = [{'nome': nome_spell, 'icone': f'{DD}/img/spell/{icone}.png'}
                    for nome_spell, icone in SPELLS.items()
                    if re.search(r'\b' + nome_spell + r'\b', get(4), re.I)]
        saida.append({
            'nome': ch['name'], 'planilha': nome, 'id': ch['id'], 'titulo': ch['title'],
            'dificuldade': dificuldade(get(3)), 'dificuldade_texto': get(3),
            'tldr': [], 'feiticos': feiticos, 'feiticos_texto': get(4),
            'runas': runas(get(5), get(6), por_runa),
            'runas_texto': get(5), 'secundarias_texto': get(6),
            'imagens_runas': imagens[r],
            'itens': [{'rotulo': 'Starting Items', 'linhas': itens_iniciais(get(8))}] if get(8) else [],
            'secoes': [{'titulo': 'Tips Against the Matchup', 'blocos': [
                {'tipo': 'p', 'texto': get(9)}]}] if get(9) else [],
        })
    return saida


def itens_iniciais(texto):
    """A nota original fica inteira; os ícones representam só os iniciais escritos."""
    inicio = texto.split('\n\n', 1)[0].lower()
    pecas = []
    for termo, nome, iid in [
            ("doran's blade", "Doran's Blade", '1055'),
            ("doran's shield", "Doran's Shield", '1054'),
            ("ring", "Doran's Ring", '1056'), ('cull', 'Cull', '1083'),
            ('cloth arm', 'Cloth Armor', '1029'), ('health potion', 'Health Potion', '2003')]:
        if termo in inicio:
            pecas.append({'nome': nome, 'icone': f'{DD}/img/item/{iid}.png'})
    linhas = [{'tipo': 'nota', 'texto': texto}]
    if pecas:
        # "or" é alternativa; "+" é uma compra conjunta.
        passos = [pecas] if ' or ' in inicio else [[p] for p in pecas]
        linhas.append({'tipo': 'item', 'passos': passos})
    return linhas


def gerar_paginas(xl, pasta=IMAGENS, itens=None):
    """Mantém células intactas e ordem de leitura; tabelas recebem colunas reais."""
    abas = list(xl.abas)
    c = xl.celulas(abas[0])
    geral = [texto_bloco(t) for (r, col), t in sorted(c.items())
             if r < 6 or col > 9 or r >= 177]
    geral.append({'tipo': 'lista', 'texto': 'UJard', 'links': [], 'itens': [
        celula('YouTube: UJard', 'https://www.youtube.com/c/UJard'),
        celula('Patreon: UJard', 'https://www.patreon.com/UJard')]})
    paginas = [{'id': 'geral', 'titulo': 'Geral', 'titulo_en': 'Overview', 'blocos': geral}]
    for aba, (pid, titulo, titulo_en) in zip(abas[1:], PAGINAS):
        c, links = xl.celulas(aba), xl.links(aba)
        por_linha = defaultdict(list)
        usados = set()
        # Duas tabelas reais: ameaças e comparação Inspiration/Gathering Storm.
        if pid == 'ameacas':
            cols, cab, linhas = [1, 3, 7, 8], 8, range(9, 23)
        elif pid == 'inspiracao':
            cols, cab, linhas = list(range(8, 14)), 5, range(6, 8)
        else:
            cols, cab, linhas = [], 0, []
        if cols:
            usados.update((cab, k) for k in cols)
            tabela = {'tipo': 'tabela', 'colunas': [c.get((cab, k), '') for k in cols],
                      'linhas': []}
            for r in linhas:
                tabela['linhas'].append([celula(c.get((r, k), ''), links.get((r, k))) for k in cols])
                usados.update((r, k) for k in cols)
            por_linha[cab].append(tabela)
        for (r, col), t in sorted(c.items()):
            if (r, col) not in usados:
                if pid == 'itens' and t.startswith('{"title":'):
                    conjunto = json.loads(t)
                    grupos = []
                    for grupo in conjunto['blocks']:
                        pecas = []
                        for item in grupo['items']:
                            iid = str(item['id'])
                            nome = (itens or {}).get(iid, {}).get('name', f'Item {iid}')
                            pecas.append({'nome': nome, 'icone': f'{DD}/img/item/{iid}.png',
                                          'id': iid, 'quantidade': item['count']})
                        grupos.append({'titulo': grupo['type'], 'itens': pecas})
                    por_linha[r].append({'tipo': 'pecas', 'grupos': grupos,
                                         'codigo_importacao': t})
                    continue
                por_linha[r].append(texto_bloco(t, links.get((r, col))))
        # Retratos de campeão na aba ameaças são redundantes. Todas as outras
        # imagens contêm informação original (inclusive barras de poder por nível).
        if pid != 'ameacas':
            for r, col, _, _, dados in xl.imagens(aba):
                legenda = f'{titulo_en} — UJard'
                imagem = salvar_imagem(dados, legenda, pasta)
                por_linha[r].append({'tipo': 'imagens', 'imagens': [imagem]})
        paginas.append({'id': pid, 'titulo': titulo, 'titulo_en': titulo_en,
                        'blocos': [b for r in sorted(por_linha) for b in por_linha[r]]})
    return paginas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xlsx', nargs='?', type=Path)
    args = parser.parse_args()
    xl = Planilha(args.xlsx.read_bytes() if args.xlsx else baixar(FONTE))
    if len(xl.abas) != 9 or next(iter(xl.abas)) != '1. Spreadsheet':
        raise ValueError('Estrutura inesperada: esperadas nove abas do guia UJard.')
    campeoes = json.loads(baixar(f'{DD}/data/pt_BR/champion.json'))['data']
    _, por_runa = montar_icones({}, json.loads(baixar(f'{DD}/data/en_US/runesReforged.json')))
    matchups = gerar_matchups(xl, campeoes, por_runa)
    itens = json.loads(baixar(f'{DD}/data/en_US/item.json'))['data']
    paginas = gerar_paginas(xl, itens=itens)
    DEST.mkdir(parents=True, exist_ok=True)
    for nome, valor in [('matchups.json', {'versao': VER, 'fonte': {
            'planilha': FONTE, 'autor': 'UJard',
            'youtube': 'https://www.youtube.com/c/UJard',
            'patreon': 'https://www.patreon.com/UJard',
            'aviso': xl.celulas(next(iter(xl.abas)))[0, 1]}, 'matchups': matchups}),
                        ('paginas.json', paginas)]:
        (DEST / nome).write_text(json.dumps(valor, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{len(matchups)} matchups, {len(paginas)} páginas; '
          f'{sum(len(m["imagens_runas"]) for m in matchups)} imagens de minor runes.')
    print('Kayle (linha 68) não tem imagem de minor runes no Excel original.')


if __name__ == '__main__':
    main()
