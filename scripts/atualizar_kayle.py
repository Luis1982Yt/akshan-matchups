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

from atualizar_mordekaiser import chave, icone_fragmento, montar_icones
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


# Nome em inglês de cada fragmento de paginas_padrao.json (a tradução vem do traducao_pt.json).
NOME_FRAGMENTO = {'adaptativa': 'Adaptive Force', 'vel_ataque': 'Attack Speed', 'aceleracao': 'Ability Haste',
                  'vel_movimento': 'Movement Speed', 'vida_nivel': 'Scaling Health', 'vida': 'Health',
                  'tenacidade': 'Tenacity and Slow Resist'}


def runas(texto_principal, texto_secundario, por_runa, padrao=None, imagem=''):
    """Os nomes escritos na célula. Com padrao (src/guias/kayle/paginas_padrao.json, tirado da aba de runas do UJard),
    a página fica completa como nos outros guias: as linhas fixas da Precisão e os fragmentos da captura da matchup."""
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
    principais = [{'nome': principal, 'icone': por_runa.get(chave(principal))}]
    linhas = [{'rotulo': 'Principal', 'pecas': principais},
              {'rotulo': 'Secundária', 'texto': texto_secundario, 'pecas': secundarias}]
    if padrao:
        principais += [{'nome': n, 'icone': por_runa.get(chave(n))} for n in padrao['linhas']]
        frags = padrao['fragmentos_por_imagem'].get(imagem, padrao['fragmentos'])
        linhas.append({'rotulo': 'Fragmentos', 'pecas': [
            {'nome': NOME_FRAGMENTO[f], 'icone': icone_fragmento(NOME_FRAGMENTO[f])} for f in frags]})
    return [linhas]


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
    arq_padrao = DEST / 'paginas_padrao.json'
    padrao = json.loads(arq_padrao.read_text(encoding='utf-8')) if arq_padrao.exists() else None
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
            'runas': runas(get(5), get(6), por_runa, padrao,
                           imagens[r][0]['src'].rsplit('/', 1)[-1][:-4] if imagens[r] else ''),
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


# Cabeçalhos da tabela de matchups da aba 1: já viram o próprio guia, não entram na página Geral.
CABECALHOS_MATCHUPS = ('Champion', 'Difficulty (easy=1', 'Summoner Spell', 'Rune Setup', 'Starting Items', 'Tips Against the Matchup',
                       'Keystones', 'Secondary', 'Minor Runes', 'CHECK IN CHAMP SELECT', 'CHECK IN GAME LOADING SCREEN')
# Convites do YouTube/Patreon repetidos no topo de algumas abas: o link fica uma vez só, na Geral.
CONVITES = re.compile(r'^(Subscribe to UJard|Support UJard|www\.youtube\.com/c/UJard|https://www\.patreon\.com/UJard)', re.I)


def eh_titulo(t):
    """Célula curta de uma linha, sem pontuação final (ou em caixa-alta): título de seção ou legenda de imagem."""
    t = t.strip()
    if not t or '\n' in t or len(t) > 60 or re.match(r'^(\d+\.|-|Lvl|Levels? \d+.*:)', t):
        return False
    return t.isupper() or not t.endswith(('.', ':', '!', ')', ',', '-'))


# Runas que a aba de runas mostra como ícone no meio da frase (o texto da célula fica com o buraco).
# Identificadas comparando cada captura com os ícones do Data Dragon; o nome entra no lugar do buraco, na ordem.
ICONES_NA_FRASE = {
    '4e44ea5b1bbfa48353818763245ce73eea3de55becd008bdee72426a78d1f379': 'Overgrowth',
    'd04bf9920f4112088e72b997b86dec9cb290965d8376b70528b36d2887f81440': 'Bone Plating',
    '63726f48d9c6f4119f7467fc362cd6c70b0e7e2a4c5d46a9b9c4560483c1f581': 'Second Wind',
    '86a880fa16279eebc0bf5321c29f84a2ffd0fa7418d33f81da2d98a8c5958890': 'Presence of Mind',
    'a3f1190a2a8b6d7f239c67d61a96bdd6fc43f63dd4ded7f669e46a0530b12a7b': 'Triumph',
}


def preenche_icones(texto, imagens):
    """Troca cada buraco (4+ espaços) da frase pelo nome do ícone correspondente, na ordem."""
    nomes = [ICONES_NA_FRASE.get(i['src'].rsplit('/', 1)[-1][:-4]) for i in imagens]
    if not nomes or None in nomes or len(re.findall(r'\s{4,}', texto)) != len(nomes):
        return texto
    for n in nomes:
        texto = re.sub(r'\s{4,}', f' {n} ', texto, count=1)
    return re.sub(r' +,', ',', re.sub(r' {2,}', ' ', texto))


def eh_item(t):
    return bool(re.match(r'^(\d+\.\s|Lvls? ?\d+[-\d]*:\s|-\s)', t.strip()))


def seccionar(blocos, pid):
    """Agrupa os blocos soltos (um por célula, na ordem de leitura) em seções com título.
    Títulos seguidos de imagens viram as legendas delas, na mesma ordem (como na planilha)."""
    secoes, atual, titulos = [], None, []

    def nova(titulo=''):
        nonlocal atual
        atual = {'tipo': 'secao', 'titulo': titulo, 'partes': []}
        secoes.append(atual)

    def parte(x):
        if atual is None:
            nova()
        ultima = atual['partes'][-1] if atual['partes'] else None
        if x['tipo'] == 'lista' and ultima and ultima['tipo'] == 'lista':
            ultima['itens'] += x['itens']
        elif x['tipo'] == 'imagens' and ultima and ultima['tipo'] == 'imagens':
            ultima['imagens'] += x['imagens']
        else:
            atual['partes'].append(x)

    def descarrega_titulos():
        # Títulos que não legendaram imagem: o primeiro abre a seção, os outros viram subtítulos dentro dela.
        nonlocal titulos
        if titulos:
            nova(titulos[0]['texto'])
            for t in titulos[1:]:
                parte({'tipo': 'sub', 'texto': t['texto']})
        titulos = []

    # Imagens seguidas viram um grupo só (para casar com as legendas na mesma ordem).
    juntos = []
    for b in blocos:
        if b['tipo'] == 'imagens' and juntos and juntos[-1]['tipo'] == 'imagens':
            juntos[-1] = {'tipo': 'imagens', 'imagens': juntos[-1]['imagens'] + b['imagens']}
        else:
            juntos.append(b)
    for b in juntos:
        if b['tipo'] == 'texto':
            t = b['texto']
            if pid == 'notas':  # anotações soltas do autor: uma lista
                parte({'tipo': 'lista', 'itens': [{'texto': t, 'links': b.get('links', [])}]})
                continue
            if pid == 'geral' and t.startswith(CABECALHOS_MATCHUPS):
                continue
            if pid != 'geral' and CONVITES.match(t.strip()):
                continue
            if eh_titulo(t) and not b.get('links'):
                titulos.append(b)
                continue
            descarrega_titulos()
            # Frase com os ícones de runa no meio: os ícones vêm logo antes, na última parte da seção.
            antes = atual['partes'][-1] if atual and atual['partes'] else None
            if antes and antes['tipo'] == 'imagens' and all(i['largura'] <= 100 for i in antes['imagens']):
                t = preenche_icones(t, antes['imagens'])
            parte({'tipo': 'lista', 'itens': [{'texto': t, 'links': b.get('links', [])}]} if eh_item(t)
                  else {'tipo': 'p', 'texto': t, 'links': b.get('links', [])})
        elif b['tipo'] == 'imagens':
            imagens = [dict(i) for i in b['imagens']]
            # Várias imagens grandes logo depois de títulos: os últimos títulos são as legendas delas, na ordem.
            n = len(imagens)
            if n >= 2 and len(titulos) >= n and all(i['largura'] > 100 for i in imagens):
                for i, t in zip(imagens, titulos[-n:]):
                    i['legenda'] = t['texto']
                titulos = titulos[:-n]
            descarrega_titulos()
            parte({'tipo': 'imagens', 'imagens': imagens})
        else:
            descarrega_titulos()
            parte({'tipo': 'bloco', 'bloco': b})
    descarrega_titulos()
    return [x for x in secoes if x['partes'] or x['titulo']]


def gerar_paginas(xl, pasta=IMAGENS, itens=None):
    """Mantém células intactas e ordem de leitura; tabelas recebem colunas reais."""
    abas = list(xl.abas)
    c = xl.celulas(abas[0])
    geral = [texto_bloco(t) for (r, col), t in sorted(c.items())
             if r < 6 or col > 9 or r >= 177]
    geral.append({'tipo': 'lista', 'texto': 'UJard', 'links': [], 'itens': [
        celula('YouTube: UJard', 'https://www.youtube.com/c/UJard'),
        celula('Patreon: UJard', 'https://www.patreon.com/UJard')]})
    paginas = [{'id': 'geral', 'titulo': 'Geral', 'titulo_en': 'Overview', 'blocos': seccionar(geral, 'geral')}]
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
                        'blocos': seccionar([b for r in sorted(por_linha) for b in por_linha[r]], pid)})
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
