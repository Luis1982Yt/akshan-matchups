"""Importa a "Fiora Bible 2026" do Sad (planilha pública do Google, uma aba só), sem OCR.

Uso: python scripts/atualizar_fiora.py [caminho.xlsx]
Sem argumento, baixa a planilha original. Requer Pillow.

A planilha tem, de cima para baixo: a apresentação do Sad, prints de ranking, as quatro páginas de runas
(Conq, PTA, Chuva de Lâminas e Stormsurge), a itemização, a legenda de dificuldade e a tabela de matchups
("FUTURE VICTIMS"). Na tabela, runas e feitiços são imagens: cada uma é reconhecida pelo md5 dos bytes.
A página completa de cada runa principal vem dos prints de páginas do próprio Sad (PAGINAS_RUNAS).
"""
import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request

from PIL import Image

from atualizar_mordekaiser import chave, icone_fragmento, montar_icones
from planilha_xlsx import Planilha
from versao_dd import VER

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'src/guias/fiora'
IMAGENS = ROOT / 'imagens/fiora'
PLANILHA = '1g_YjX4jYcz15k8FZuOkhc4IWA1LLm28WinrVCGBXxLY'
FONTE = f'https://docs.google.com/spreadsheets/d/{PLANILHA}/export?format=xlsx'
DD = f'https://ddragon.leagueoflegends.com/cdn/{VER}'

# Ícones da tabela de matchups (md5 da imagem colada na planilha -> runa ou feitiço).
# Conferidos comparando cada imagem com as do Data Dragon.
RUNAS_MD5 = {
    '7d7e6ec292db357109bbfceba1ece248': 'Press the Attack',
    '0eb4363c5f3230539d5f3619d4fce3d8': 'Press the Attack',
    'ee2856e8f9be5b864bfef9a7a47d82c5': 'Conqueror',
    '1eec493570594f36c5bb3a155077e8ea': 'Conqueror',
    '4add76342bc5976ebda92773ec434eaa': 'Hail of Blades',
    'd65746f39f00d61f046d8690ab552c89': "Stormraider's Surge",
}
FEITICOS_MD5 = {
    '5a78ced013eaada412c42832c0e009f1': ('Ignite', 'SummonerDot'),
    'bf65f6ad55edee8d44f4af7ae5ce5e1c': ('Exhaust', 'SummonerExhaust'),
    '87576941c3d9ac91ab8fd502d34dc27a': ('Barrier', 'SummonerBarrier'),
}
# Imagens de brincadeira (o gato na linha do espelho Fiora x Fiora): não são runa nem feitiço.
IGNORAR_MD5 = {'88c870d016e8c4de3e5ae8187daf15ef'}
# Itens que aparecem como ícone na itemização (md5 -> id do item no Data Dragon).
ITENS_MD5 = {
    '4a34ebe6d45b26b4615a0ea770a84ec5': '6692', '473bbfe6fc9310898718c2712591b6e0': '3074',
    'fb43ef3a49b84df82c12fe5fc7d39c3e': '3074', 'c0aa3e5e11fd0dd71995d97989f76ecd': '3078',
    '1a4f00551a73b25d05223c813bfcb5b2': '6333', 'd2a61a14bc43737da474e4c0bcc51652': '6333',
    '213aeb37c876c21fe073fe34e9403f5d': '2517', '3597812fcc128ed723a9b9c89860514a': '3181',
    '887bc2dd80d3470623788dd4ef47b4eb': '3053', 'e8867fb2d44e1713972e4e0c3335e197': '3161',
    '1d1403d7b8484efcce2dd84ce19e2517': '6699', '3344b06a799ac2e12ca8f5b7523e79aa': '3042',
    '2bd804ad23db275192d406cb0faa1c8f': '3156', 'dea5052bd0b5d07193499b447402721b': '3155',
}
# As quatro páginas dos prints "CONQ / PTA / Hail of Blades / Stormsurge Page" da planilha.
PAGINAS_RUNAS = {
    'Conqueror': (['Conqueror', 'Triumph', 'Legend: Alacrity', 'Last Stand'], ['Nimbus Cloak', 'Transcendence']),
    'Press the Attack': (['Press the Attack', 'Triumph', 'Legend: Alacrity', 'Last Stand'], ['Nimbus Cloak', 'Transcendence']),
    'Hail of Blades': (['Hail of Blades', 'Sudden Impact', 'Grisly Mementos', 'Treasure Hunter'], ['Nimbus Cloak', 'Transcendence']),
    "Stormraider's Surge": (["Stormraider's Surge", 'Nimbus Cloak', 'Transcendence', 'Scorch'], ['Sudden Impact', 'Treasure Hunter']),
}
FRAGMENTOS = ['Adaptive Force', 'Adaptive Force', 'Health']
# Legenda de cada print de página de runas (texto da célula acima dele, na ordem da esquerda para a direita).
LEGENDAS_PAGINAS = ['CONQ Page', 'PTA Page', 'Hail of Blades Page', 'Stormsurge Page']
NIVEIS = {'VERY EASY': 1, 'EASY': 2, 'MEDIUM': 3, 'HARD': 4, 'VERY HARD': 5}


def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as resposta:
        return resposta.read()


def de_md5(tabela, md5):
    return tabela.get(md5)


def salvar_imagem(dados, alt, pasta=IMAGENS, maximo=1400):
    """Imagem em PNG (ou JPEG, se for foto grande), identificada pelo conteúdo. Prints maiores que `maximo`
    pixels de largura são reduzidos, para o site não ficar pesado."""
    with Image.open(io.BytesIO(dados)) as original:
        im = original.convert('RGBA')
    if im.width > maximo:
        im = im.resize((maximo, round(im.height * maximo / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if im.width > 200:
        im.convert('RGB').save(buf, 'JPEG', quality=84, optimize=True, progressive=True)
        ext = 'jpg'
    else:
        im.save(buf, 'PNG', optimize=True)
        ext = 'png'
    conteudo = buf.getvalue()
    nome = hashlib.sha256(conteudo).hexdigest()[:40] + '.' + ext
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / nome
    if not destino.exists():
        destino.write_bytes(conteudo)
    return {'src': f'imagens/fiora/{nome}', 'alt': alt, 'largura': im.width, 'altura': im.height}


def limpa(t):
    """Tira os espaços que a planilha usa para abrir lugar para os ícones (o texto em si fica igual)."""
    linhas = [re.sub(r'[ \t]{2,}', ' ', l).strip() for l in t.split('\n')]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(linhas)).strip()


def linha_de(c, texto, coluna=None):
    achadas = [r for (r, col), t in c.items() if t.strip().upper().startswith(texto) and (coluna is None or col == coluna)]
    if not achadas:
        raise ValueError(f'Estrutura inesperada: não achei "{texto}" na planilha do Sad.')
    return min(achadas)


def pagina_runas(keystone, por_runa):
    principais, secundarias = PAGINAS_RUNAS[keystone]
    peca = lambda n: {'nome': n, 'icone': por_runa.get(chave(n))}
    return [{'rotulo': 'Principal', 'pecas': [peca(n) for n in principais]},
            {'rotulo': 'Secundária', 'pecas': [peca(n) for n in secundarias]},
            {'rotulo': 'Fragmentos', 'pecas': [{'nome': f, 'icone': icone_fragmento(f)} for f in FRAGMENTOS]}]


def nivel(texto):
    return NIVEIS.get(re.sub(r'\s+', ' ', (texto or '').strip().upper()))


def gerar_matchups(xl, campeoes, por_runa, itens):
    aba = next(iter(xl.abas))
    c = xl.celulas(aba)
    inicio = linha_de(c, 'FUTURE VICTIMS', 0) + 1
    # A tabela vai até a última linha com campeão e dica (embaixo dela só vem o crédito).
    fim = max(r for (r, col) in c if col == 0 and r >= inicio and (r, 4) in c) + 1
    por_nome = {}
    for ch in campeoes.values():
        por_nome[chave(ch['name'])] = ch
        por_nome[chave(ch['id'])] = ch
    icones = defaultdict(list)
    desconhecidas = set()
    for r, col, _, md5, _ in xl.imagens(aba):
        if inicio <= r < fim and col >= 5 and md5 not in IGNORAR_MD5:
            achado = de_md5(RUNAS_MD5, md5) or de_md5(FEITICOS_MD5, md5)
            if achado:
                icones[r].append(achado)
            else:
                desconhecidas.add((c.get((r, 0), '?').strip(), md5))
    for nome, md5 in sorted(desconhecidas):
        print(f'  aviso: ícone novo na linha de {nome} (md5 {md5}); confira e ponha em RUNAS_MD5 ou FEITICOS_MD5')
    build = itens_gerais(c, itens)
    saida = []
    for r in range(inicio, fim):
        nome = (c.get((r, 0)) or '').strip()
        if not nome or (r, 4) not in c:
            continue
        # "Sir Thomas Kench (Tahm Kench)": vale o nome entre parênteses.
        real = re.search(r'\(([^)]+)\)\s*$', nome)
        ch = por_nome[chave(real.group(1) if real else nome)]  # falha se um campeão não for reconhecido
        rota, jogo = nivel(c.get((r, 2))), nivel(c.get((r, 3)))
        keystones = [k for k in icones[r] if isinstance(k, str)]
        feiticos = [{'nome': n, 'icone': f'{DD}/img/spell/{arq}.png'} for n, arq in (f for f in icones[r] if isinstance(f, tuple))]
        saida.append({
            'nome': ch['name'], 'planilha': nome, 'id': ch['id'], 'titulo': ch['title'],
            'dificuldade': {'overall': rota, 'rota': rota, 'jogo': jogo,
                            'rota_texto': (c.get((r, 2)) or '').strip(), 'jogo_texto': (c.get((r, 3)) or '').strip()},
            # Mais de um feitiço = alternativas ("If I've put multiple, pick the one you are more comfortable with").
            'tldr': [], 'feiticos': list({f['nome']: f for f in feiticos}.values()), 'feiticos_ou': True,
            'runas': [pagina_runas(k, por_runa) for k in dict.fromkeys(keystones)],
            'imagens_runas': [], 'itens': build if ch['id'] != 'Fiora' else [],
            'secoes': [{'titulo': 'Tips and Tricks', 'blocos': [{'tipo': 'p', 'texto': c[r, 4].strip()}]}],
        })
    return saida


def item(iid, itens):
    return {'nome': itens[iid]['name'], 'icone': f'{DD}/img/item/{iid}.png'}


def itens_gerais(c, itens):
    """A build que o Sad manda fazer sempre ("ALWAYS BUILD ... UNLESS STH IS SPECIFICALLY MENTIONED IN THE
    MATCHUP SECTION"), na ordem do parágrafo da itemização: Ravenous > Trinity/Eclipse > DD ou Hullbreaker >
    Sterak's, Shojin ou Hullbreaker. O aviso da planilha vai junto, em cada matchup."""
    r = linha_de(c, 'ALWAYS BUILD')
    aviso = next(t for (rr, _), t in c.items() if rr == r and t.strip().upper().startswith('ALWAYS BUILD'))
    passos = [['3074'], ['3078', '6692'], ['6333', '3181'], ['3053', '3161', '3181']]
    return [{'rotulo': '', 'linhas': [
        {'tipo': 'item', 'passos': [[item(i, itens) for i in p] for p in passos]},
        {'tipo': 'nota', 'texto': limpa(aviso)}]}]


def paragrafos(texto):
    """Cada linha da célula vira um parágrafo ("Stream: ...", "Channel: ...", um emoji por linha); a linha que
    começa com minúscula continua a frase de cima (a planilha quebrou a linha no meio)."""
    saida = []
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha:
            continue
        if saida and linha[0].islower():
            saida[-1] += ' ' + linha
        else:
            saida.append(linha)
    return saida


def p(texto, links=None):
    return {'tipo': 'p', 'texto': texto, 'links': links or []}


LINK = re.compile(r'(?:https?://|www\.)[^\s!]+')


def com_links(texto):
    """Parágrafo com os endereços escritos no texto virando links (o texto fica igual)."""
    links = [{'texto': u, 'url': u if u.startswith('http') else 'https://' + u} for u in LINK.findall(texto)]
    return p(texto, links)


def gerar_paginas(xl, itens):
    aba = next(iter(xl.abas))
    c = xl.celulas(aba)
    imagens = xl.imagens(aba)
    r_runas = linha_de(c, 'CONQ PAGE')
    r_itens = linha_de(c, 'ITEMIZATION', 0)
    r_dif = linha_de(c, 'DIFFICULTY IS BASED')
    r_tabela = linha_de(c, 'FUTURE VICTIMS', 0)

    # Geral: apresentação (parágrafos da célula grande), novidades, Discord, prints de ranking e o crédito final.
    geral = []
    for (r, col), t in sorted(c.items()):
        if r >= r_runas - 1 or not t.strip() or re.fullmatch(r'\s*(Rank.*|Challenger.*)', t):
            continue
        if r == 0:
            continue  # o título "Fiora Matchup Spreadsheet 2026 - Updated October -" vira o subtítulo da Geral
        for par in paragrafos(limpa(t)):
            geral.append(com_links(par))
    rankings = []
    legendas = {(r, col): limpa(t) for (r, col), t in c.items() if r < r_runas - 1 and re.fullmatch(r'\s*(Rank.*|Challenger.*)', t)}
    for r, col, _, _, dados in imagens:
        if r < r_runas - 1:
            # O print fica embaixo da legenda escrita logo acima dele: a mais próxima na mesma coluna, senão em qualquer uma.
            acima = sorted((k for k in legendas if k[0] <= r), key=lambda k: (k[1] != col, -k[0]))
            leg = legendas[acima[0]] if acima else ''
            rankings.append({**salvar_imagem(dados, 'Sad — ranking (original spreadsheet)'), 'legenda': leg})
    titulo = limpa(c.get((0, 0), ''))
    secoes_geral = [{'tipo': 'secao', 'titulo': titulo, 'partes': geral}]
    if rankings:
        secoes_geral.append({'tipo': 'secao', 'titulo': '', 'partes': [{'tipo': 'imagens', 'imagens': rankings}]})
    # Legenda de dificuldade ("VERY EASY - ..."), que vale para Lane Threat e Game Threat.
    dif = [p(limpa(c[r_dif, 4]))]
    for r in range(r_dif + 1, r_tabela):
        if c.get((r, 0)) and c.get((r, 4)):
            dif += [{'tipo': 'sub', 'texto': limpa(c[r, 0])}, p(limpa(c[r, 4]))]
    secoes_geral.append({'tipo': 'secao', 'titulo': limpa(c.get((r_tabela, 2), 'LANE THREAT')) + ' / ' + limpa(c.get((r_tabela, 3), 'GAME THREAT')), 'partes': dif})
    fim = [p(limpa(t)) for (r, col), t in sorted(c.items()) if r > r_tabela and col == 0 and t.strip().lower().startswith('created and organised')]
    if fim:
        secoes_geral.append({'tipo': 'secao', 'titulo': '', 'partes': fim})

    # Runas: os quatro prints de páginas, com a legenda da planilha.
    prints = [i for i in imagens if r_runas <= i[0] < r_itens]
    paginas_runas = [{**salvar_imagem(d, f'Fiora — {leg} — Sad'), 'legenda': leg}
                     for (_, _, _, _, d), leg in zip(prints, LEGENDAS_PAGINAS)]

    # Itemização: o aviso, a data, o parágrafo e cada item com a explicação ao lado do ícone.
    partes_itens = []
    textos = sorted((r, col, t) for (r, col), t in c.items() if r_itens < r < r_dif and t.strip())
    icones_linha = defaultdict(list)
    posicoes = []  # (linha, deslocamento x, id) de cada ícone de item da itemização
    for r, col, dx, md5, _ in imagens:
        if r_runas < r < r_dif:  # alguns ícones da build ficam um pouco acima do título "ITEMIZATION"
            iid = de_md5(ITENS_MD5, md5)
            if iid:
                icones_linha[r].append(iid)
                posicoes.append((r, dx, iid))
    explicados = []
    for r, col, t in textos:
        texto = limpa(t)
        if texto.startswith('-'):
            # O ícone do item fica na linha de cima do texto (às vezes duas): o primeiro deles é o item explicado.
            iid = next((icones_linha[k][0] for k in (r - 2, r - 1, r) if icones_linha.get(k)), None)
            if iid:
                explicados.append({**item(iid, itens), 'id': iid, 'texto': texto.lstrip('- ').strip()})
                continue
        if explicados:
            partes_itens.append({'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [{'titulo': '', 'itens': explicados}]}})
            explicados = []
        partes_itens.append(p(texto) if not re.fullmatch(r'Updated\s+\w+\s+\d+', texto) else {'tipo': 'sub', 'texto': texto.replace('\n', ' ')})
        if texto.upper().startswith('ALWAYS BUILD'):
            # Os ícones desenhados logo acima do aviso, da esquerda para a direita (ícone empilhado = alternativa).
            acima = sorted((dx, -rr, i) for rr, dx, i in posicoes if r - 6 <= rr <= r)
            partes_itens.append({'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [{'titulo': '', 'itens': [
                {**item(i, itens), 'id': i} for i in dict.fromkeys(i for _, _, i in acima)]}]}})
    if explicados:
        partes_itens.append({'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [{'titulo': '', 'itens': explicados}]}})
    return [
        {'id': 'geral', 'titulo': 'Geral', 'titulo_en': 'Overview', 'blocos': secoes_geral},
        {'id': 'runas', 'titulo': 'Runas', 'titulo_en': 'Runes', 'blocos': [
            {'tipo': 'secao', 'titulo': limpa(c.get((r_tabela, 5), 'RUNES')).split('\n')[0], 'partes': [{'tipo': 'imagens', 'imagens': paginas_runas}]}]},
        {'id': 'itens', 'titulo': 'Itens', 'titulo_en': 'Itemization', 'blocos': [
            {'tipo': 'secao', 'titulo': limpa(c[r_itens, 0]), 'partes': partes_itens}]},
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xlsx', nargs='?', type=Path)
    args = parser.parse_args()
    xl = Planilha(args.xlsx.read_bytes() if args.xlsx else baixar(FONTE))
    if len(xl.abas) != 1:
        raise ValueError('Estrutura inesperada: a planilha do Sad tinha uma aba só.')
    campeoes = json.loads(baixar(f'{DD}/data/pt_BR/champion.json'))['data']
    _, por_runa = montar_icones({}, json.loads(baixar(f'{DD}/data/en_US/runesReforged.json')))
    itens = json.loads(baixar(f'{DD}/data/en_US/item.json'))['data']
    matchups = gerar_matchups(xl, campeoes, por_runa, itens)
    paginas = gerar_paginas(xl, itens)
    DEST.mkdir(parents=True, exist_ok=True)
    fonte = {'planilha': f'https://docs.google.com/spreadsheets/d/{PLANILHA}/edit', 'autor': 'Sad',
             'twitch': 'https://www.twitch.tv/justsad42', 'youtube': 'https://www.youtube.com/@JustSad42'}
    for nome, valor in [('matchups.json', {'versao': VER, 'fonte': fonte, 'matchups': matchups}), ('paginas.json', paginas)]:
        (DEST / nome).write_text(json.dumps(valor, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{len(matchups)} matchups, {len(paginas)} páginas; '
          f'{sum(1 for m in matchups if m["runas"])} com runas, {sum(1 for m in matchups if m["feiticos"])} com feitiço.')


if __name__ == '__main__':
    main()
