"""Monta o guia da Akali (mid e top) a partir de src/guias/akali/planilha_bruta.json.

Uso: python scripts/atualizar_akali.py
A planilha do SupremeG0at tem download e cópia bloqueados, então não dá para baixar o xlsx como nos outros guias:
a cópia bruta é lida da página do Google Sheets no navegador por `node scripts/akali_baixar.js` (rodar à mão quando
quiser atualizar; não está no workflow diário). Este script só transforma a cópia em matchups.json e paginas.json.

Planilha: uma linha por campeão (mid de Ahri a Zoe, top de Aatrox a Zac), com "What to do as Akali", "What to look
out for" e "Timers to think about"; a dificuldade é a cor da célula do campeão. Aba "Runes/items/summoners": a
explicação de cada feitiço, a página de runas única do autor (imagem; transcrita em PAGINA_RUNAS) e os itens (cada
item é um ícone ao lado do texto; os ids estão em ITENS_ABA2, conferidos com o Data Dragon).
"""
import json
from pathlib import Path
import re
import urllib.request

from atualizar_mordekaiser import chave, icone_fragmento, montar_icones
from versao_dd import VER

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'src/guias/akali'
DD = f'https://ddragon.leagueoflegends.com/cdn/{VER}'
# Cor da célula do campeão -> (nota de 1 a 5, legenda da planilha). Laranja e vermelho-escuro aparecem em algumas
# células sem estar na legenda: ficam como difícil e muito difícil. "Thematic counter" (Galio, TF, Malzahar...) é
# um campeão que atrapalha a Akali pelo kit, mais do que pela rota: entra como difícil, com a legenda do autor.
CORES = {'#e06666': (5, 'Very hard'), '#cc0000': (5, 'Very hard'), '#dd7e6b': (4, 'Hard'), '#f6b26b': (4, 'Hard'),
         '#ffd966': (3, 'Skill matchup'), '#93c47d': (2, 'Akali favoured'), '#6aa84f': (1, 'Easy matchup'),
         '#3c78d8': (4, 'Thematic counter/special matchup')}
# Página de runas do print do autor (aba 2): Eletrocutar + Determinação, fragmentos adaptativa / velocidade / vida por nível.
PAGINA_RUNAS = (['Electrocute', 'Sudden Impact', 'Grisly Mementos', 'Ultimate Hunter'], ['Second Wind', 'Overgrowth'],
                ['Adaptive Force', 'Movement Speed', 'Scaling Health'])
# Linha da aba 2 -> id do item do ícone ao lado do texto.
ITENS_ABA2 = {26: '1056', 27: '1054', 28: '1082', 31: '1001', 32: '3175', 33: '3173', 34: '3174', 35: '3168',
              37: '3146', 38: '4646', 39: '3100', 40: '4645', 41: '3089', 42: '3135', 43: '3157'}
FEITICOS_ABA2 = {1: ('Ignite', 'SummonerDot'), 2: ('Flash', 'SummonerFlash'), 3: ('Teleport', 'SummonerTeleport'),
                 4: ('Cleanse', 'SummonerBoost')}
SECOES = [('fazer', 'What to do as Akali'), ('observar', 'What to look out for'), ('timers', 'Timers to think about')]


def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as r:
        return r.read()


def itens_da_celula(texto):
    """'-Faça isso\\ncontinua\\n-Outra dica' -> ['Faça isso continua', 'Outra dica'] (o autor quebra a linha no meio
    da frase para caber na célula; só o '-' no começo abre uma dica nova). O texto continua o mesmo."""
    itens = []
    for linha in texto.split('\n'):
        l = linha.strip()
        if not l:
            continue
        if l.startswith('-') or not itens:
            itens.append(l.lstrip('-').strip())
        else:
            itens[-1] += ' ' + l
    return [i for i in itens if i]


def peca_item(iid, itens):
    return {'nome': itens[iid]['name'], 'icone': f'{DD}/img/item/{iid}.png'}


def build(rota, itens, aba2):
    """A build do autor (aba 2): Anel de Doran, Pistola-Laminar primeiro sempre, o 2º item muda com a matchup, Cajado do
    Vazio e Zhonya na build completa; botas de nível 3 no mid, as botas simples no top."""
    # Só a primeira frase da nota de itens ("...only 2nd item changes and ordering.").
    nota = re.split(r'(?<=\.)\s+probably', aba2.get('44,0', '').split('\n')[0])[0].strip()
    botas = '3175' if rota == 'Mid' else '1001'
    passos = [['1056'], ['3146'], ['4646', '3089', '3100', '4645'], ['3135', '3157'], [botas]]
    linhas = [{'tipo': 'item', 'passos': [[peca_item(i, itens) for i in p] for p in passos]}]
    if nota:
        linhas.append({'tipo': 'nota', 'texto': nota})
    return [{'rotulo': '', 'linhas': linhas}]


def runas(por_runa):
    principais, secundarias, frags = PAGINA_RUNAS
    peca = lambda n: {'nome': n, 'icone': por_runa.get(chave(n))}
    return [[{'rotulo': 'Principal', 'pecas': [peca(n) for n in principais]},
             {'rotulo': 'Secundária', 'pecas': [peca(n) for n in secundarias]},
             {'rotulo': 'Fragmentos', 'pecas': [{'nome': f, 'icone': icone_fragmento(f)} for f in frags]}]]


def gerar_matchups(bruto, campeoes, por_runa, itens):
    por_nome = {}
    for ch in campeoes.values():
        por_nome[chave(ch['name'])] = ch
        por_nome[chave(ch['id'])] = ch
    por_nome['vlad'] = por_nome['vladimir']
    saida = []
    for rota, lista in (('Mid', bruto['mid']), ('Top', bruto['top'])):
        for m in lista:
            ch = por_nome[chave(m['nome'])]  # falha se um campeão não for reconhecido
            nota, legenda = CORES[m['cor']]
            saida.append({
                'nome': ch['name'], 'planilha': m['nome'], 'id': ch['id'], 'titulo': ch['title'], 'rota': rota,
                'dificuldade': {'overall': nota, 'texto': legenda},
                'tldr': [], 'feiticos': [{'nome': 'Flash', 'icone': f'{DD}/img/spell/SummonerFlash.png'},
                                         {'nome': 'Ignite', 'icone': f'{DD}/img/spell/SummonerDot.png'}],
                'runas': runas(por_runa), 'imagens_runas': [], 'itens': build(rota, itens, bruto['aba2']),
                'secoes': [{'titulo': titulo, 'blocos': [{'tipo': 'lista', 'itens': itens_da_celula(m[campo])}]}
                           for campo, titulo in SECOES if m.get(campo)],
            })
    return saida


def p(texto):
    return {'tipo': 'p', 'texto': texto, 'links': []}


def gerar_paginas(bruto, itens):
    g, a2 = bruto['geral'], bruto['aba2']
    # "Some things to keep in mind": o autor escreveu o texto em várias linhas da coluna B; juntas, viram parágrafos
    # que começam nas perguntas dele ("Akali's biggest cap:", "When is Akali strong in a draft?", "Wincondition?").
    corrido = ' '.join(g[f'{r},1'].strip() for r in range(5, 24) if f'{r},1' in g)
    paragrafos = [x.strip() for x in re.split(r"(?=Akali's biggest cap:|When is Akali strong in a draft\?|And when enemy|Wincondition\?)", corrido) if x.strip()]
    legenda = [{'tipo': 'lista', 'itens': [{'texto': nome, 'links': []} for nome in bruto['legenda']]}]
    geral = [
        {'tipo': 'secao', 'titulo': g.get('4,1', ''), 'partes': [p(x) for x in paragrafos]},
        {'tipo': 'secao', 'titulo': g.get('17,0', 'Matchup difficulty'), 'partes': legenda},
    ]
    feiticos = [{'nome': n, 'icone': f'{DD}/img/spell/{arq}.png', 'texto': a2[f'{r},1']}
                for r, (n, arq) in FEITICOS_ABA2.items() if f'{r},1' in a2]
    runas_txt = [p(a2[f'{r},0']) for r in range(17, 24) if f'{r},0' in a2]

    def grupo(titulo, linhas):
        return {'titulo': titulo, 'itens': [{**peca_item(ITENS_ABA2[r], itens), 'id': ITENS_ABA2[r], 'texto': a2[f'{r},1']}
                                            for r in linhas if f'{r},1' in a2]}
    pg_itens = [{'tipo': 'secao', 'titulo': a2.get('24,0', 'ITEMS'), 'partes': [
        {'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [grupo(a2.get('25,0', 'STARTER ITEMS'), [26, 27, 28])]}},
        p(a2.get('29,0', '')),
        {'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [grupo(a2.get('30,0', 'Boots'), [31, 32, 33, 34, 35])]}},
        {'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [grupo(a2.get('36,0', 'Legendary Items'), range(37, 44))]}},
        *[p(x) for x in a2.get('44,0', '').split('\n') if x.strip()],
    ]}]
    return [
        {'id': 'geral', 'titulo': 'Geral', 'titulo_en': 'Overview', 'blocos': geral},
        {'id': 'runas', 'titulo': 'Runas e feitiços', 'titulo_en': 'Runes and summoners', 'blocos': [
            {'tipo': 'secao', 'titulo': a2.get('0,0', 'Summoner Spells'), 'partes': [
                {'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [{'titulo': '', 'itens': feiticos}]}}]},
            {'tipo': 'secao', 'titulo': a2.get('5,0', 'Runes'), 'partes': runas_txt}]},
        {'id': 'itens', 'titulo': 'Itens', 'titulo_en': 'Items', 'blocos': pg_itens},
    ]


def bruto_da_pasta(pasta):
    """Monta planilha_bruta.json com o que `node scripts/akali_baixar.js <pasta>` baixou."""
    import datetime
    from planilha_xlsx import publicado
    from PIL import Image
    pasta = Path(pasta)
    h1 = (pasta / 'aba1.html').read_text(encoding='utf-8')
    c1 = publicado(h1)
    c2 = publicado((pasta / 'aba2.html').read_text(encoding='utf-8'))
    # Cor de fundo de cada linha (classe CSS da primeira célula), nas 100 linhas que vêm na página.
    css = dict(re.findall(r'\.ritz \.waffle \.(s\d+)\{([^}]*)\}', h1))
    fundo = {k: (re.search(r'background-color:(#[0-9a-fA-F]{6})', v) or [None, None])[1] for k, v in css.items()}
    cor = {}
    for m in re.finditer(r'<tr[^>]*><th id="\d+R(\d+)"[^>]*>.*?</th>(.*?)</tr>', h1[h1.find('<tbody>'):], re.S):
        td = re.search(r'<td class="(s\d+)"', m.group(2))
        if td:
            cor[int(m.group(1))] = fundo.get(td.group(1))
    txt = lambda c, r, k: (c.get((r, k)) or {}).get('texto', '')
    linha = lambda r: {'nome': txt(c1, r, 0), 'fazer': txt(c1, r, 1), 'observar': txt(c1, r, 5), 'timers': txt(c1, r, 6), 'cor': cor.get(r)}
    inicio_top = next(r for (r, k), v in c1.items() if k == 0 and v['texto'].lower().startswith('toplane matchups start'))
    mid = [linha(r) for r in range(25, inicio_top) if txt(c1, r, 0)]
    top = [linha(r) for r in range(inicio_top + 1, 100) if txt(c1, r, 0)]
    # Linhas depois da 100: textos na ordem [campeão, fazer, observar, timers] e cores pelo print da coluna A
    # (a primeira faixa colorida do print é a linha 100, que já veio na página).
    t = (pasta / 'linhas_extras.txt').read_text(encoding='utf-8')
    dados = json.loads(json.loads(t[t.index('{'):t.rindex('}') + 1])['snapshot'][0][1])
    textos = []

    def anda(x):
        if isinstance(x, str):
            textos.append(x)
        elif isinstance(x, list):
            [anda(y) for y in x]
        elif isinstance(x, dict):
            [anda(y) for y in x.values()]
    anda(dados)
    fim = next((i for i, x in enumerate(textos) if x.startswith('#gid=')), len(textos))
    textos = [x for x in textos[:fim] if len(x) > 1 and not re.fullmatch(r'[\d\[\],".\s-]+', x)]
    im = Image.open(pasta / 'coluna_a.png').convert('RGB')
    faixas, antes, ini = [], None, 0
    for y in range(200, im.height):
        px = im.getpixel((60, y))
        if px != antes:
            if antes is not None and y - ini > 40 and antes != (255, 255, 255):
                faixas.append('#%02x%02x%02x' % antes)
            antes, ini = px, y
    for i in range(0, len(textos) - 3, 4):
        nome, fazer, observar, timers = textos[i:i + 4]
        top.append({'nome': nome, 'fazer': fazer, 'observar': observar, 'timers': timers, 'cor': faixas[1 + i // 4]})
    bruto = {
        '_fonte': 'SupremeG0at Akali Spreadsheet 2026 (download e cópia bloqueados pelo autor). Lida em %s pela página do '
                  'Google Sheets no navegador (scripts/akali_baixar.js). Montado sem autorização do autor, por decisão do '
                  'dono do site (GUIAS_FUTUROS.md).' % datetime.date.today().isoformat(),
        'planilha': 'https://docs.google.com/spreadsheets/d/1QSmbqRpG-caL8flzDFVQw546CSp5VBvLB96ymQd2uzQ/edit',
        'geral': {f'{r},{k}': v['texto'] for (r, k), v in c1.items() if r < 25},
        'legenda': {txt(c1, r, 0): cor.get(r) for r in range(18, 24)},
        'mid': mid, 'top': top,
        'aba2': {f'{r},{k}': v['texto'] for (r, k), v in c2.items()},
    }
    (DEST / 'planilha_bruta.json').write_text(json.dumps(bruto, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'cópia bruta: {len(mid)} mid, {len(top)} top')


def main():
    import sys
    if '--de' in sys.argv:
        bruto_da_pasta(sys.argv[sys.argv.index('--de') + 1])
    bruto = json.loads((DEST / 'planilha_bruta.json').read_text(encoding='utf-8'))
    campeoes = json.loads(baixar(f'{DD}/data/pt_BR/champion.json'))['data']
    itens = json.loads(baixar(f'{DD}/data/en_US/item.json'))['data']
    _, por_runa = montar_icones({}, json.loads(baixar(f'{DD}/data/en_US/runesReforged.json')))
    matchups = gerar_matchups(bruto, campeoes, por_runa, itens)
    paginas = gerar_paginas(bruto, itens)
    fonte = {'planilha': bruto['planilha'], 'autor': 'SupremeG0at', 'twitch': 'https://www.twitch.tv/supremeg0at'}
    for nome, valor in [('matchups.json', {'versao': VER, 'fonte': fonte, 'matchups': matchups}), ('paginas.json', paginas)]:
        (DEST / nome).write_text(json.dumps(valor, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    sem_icone = sorted({p['nome'] for m in matchups for op in m['runas'] for l in op for p in l['pecas'] if not p['icone']})
    print(f"{len(matchups)} matchups ({sum(m['rota'] == 'Mid' for m in matchups)} mid, {sum(m['rota'] == 'Top' for m in matchups)} top), "
          f"{len(paginas)} páginas" + (f'; runas sem ícone: {sem_icone}' if sem_icone else ''))


if __name__ == '__main__':
    main()
