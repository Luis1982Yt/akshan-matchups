"""Importa o "r/KSanteMains Matchup Guide" (planilha pública do Google), sem OCR.

Uso: python scripts/atualizar_ksante.py [caminho.xlsx]
Sem argumento, baixa a planilha original. O texto vem do xlsx; os links (VoDs) vêm da versão publicada (htmlview),
porque a exportação em xlsx perde os hyperlinks.

Aba "Matchups": um bloco por campeão (nome na coluna A, nota de 0 a 10 na C; quanto maior, melhor para o inimigo),
com runas e itens recomendados na coluna D e as seções Short Version, Laning Overview, Trading / Fighting, Level 6+ e
Additional Information (rótulo na G, texto na H). Em cima, a página de runas e a build gerais. Aba "Difficulties":
a nota de cada um dos dois autores.
"""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re
import urllib.request

from atualizar_mordekaiser import chave, icone_item, montar_icones
from planilha_xlsx import Planilha, publicado
from versao_dd import VER

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'src/guias/ksante'
PLANILHA = '1ArJkfy78AtJ7l5pUQxxCBGYp1pioa0TOu6E9hKpb1gc'
GID_MATCHUPS = '1875627373'
FONTE = f'https://docs.google.com/spreadsheets/d/{PLANILHA}/export?format=xlsx'
PUBLICADA = f'https://docs.google.com/spreadsheets/d/{PLANILHA}/htmlview/sheet?headers=true&gid={GID_MATCHUPS}'
DD = f'https://ddragon.leagueoflegends.com/cdn/{VER}'
SECOES = ['Laning Overview', 'Trading / Fighting', 'Level 6+', 'Additional Information']
RESUMO = 'Short Version'
# A aba Difficulties só repete a média de cada matchup (as notas por autor citam nomes e o autor pediu para não ser
# citado), então ela fica fora do site; True traz de volta como página.
INCLUIR_DIFICULDADES = False
# Abreviações de runa escritas na planilha.
APELIDO_RUNA = {'grasp': 'Grasp of the Undying', 'pom': 'Presence of Mind', 'hob': 'Hail of Blades'}
# Itens que aparecem só como imagem no cabeçalho (md5 -> id), conferidos com o Data Dragon.
CORE_MD5 = {'4521ed9ea895187a77163dc4090f5a64': '1031', 'e444ae6e7c8b92695fd6b57b6abaa6b9': '6662',
            '93a46b807030bc7236a8d22d6710df40': '3065'}
EVITAR_MD5 = {'04f0df4379957bd407a40fbc510d7a25': '6664', '6aaf7db9b84ea3cacd5d5d8864f77d44': '3068'}
INICIAIS_MD5 = {'daf8fc468a6ff95456bcbbb8d08a7c72': '1120', '90dee3899f41e41c88d556938d61139a': '2003'}


def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as r:
        return r.read()


def limpa(t):
    return re.sub(r'[ \t]+', ' ', (t or '').replace('\r', '')).strip()


def runa(nome, por_runa):
    n = limpa(nome).strip('.')
    n = APELIDO_RUNA.get(n.lower(), n)
    return {'nome': n, 'icone': por_runa.get(chave(n)) or por_runa.get(chave(n.split(':')[-1]))}


def primeira(alts):
    """'Overgrowth/Unflinching' -> 'Overgrowth' (a primeira opção; a nota mostra as outras)."""
    return re.split(r'\s*[/>]\s*', alts.strip())[0]


def paginas_runas(principal, secundaria, opcional, por_runa):
    """Uma página por runa principal ("Aftershock/Grasp" = duas) com a secundária da planilha; a secundária opcional
    ("(optional) Sudden Impact + Ultimate Hunter") vira mais uma página com a primeira runa principal."""
    linhas = [l for l in principal.split('\n') if l.strip()]
    if not linhas:
        return []
    keystones = [k for k in re.split(r'\s*[/>]\s*', linhas[0]) if k.strip()]
    # Runas separadas por "+" ou por quebra de linha.
    menores = [primeira(x) for x in re.split(r'\s*[+\n]\s*', '\n'.join(linhas[1:])) if x.strip()]
    sec = [primeira(x) for x in re.split(r'\s*[+\n]\s*', secundaria) if x.strip()]
    opc = re.sub(r'^\(optional\)\s*', '', opcional.split('\n')[0], flags=re.I) if opcional else ''
    opc = [primeira(x) for x in re.split(r'\s*\+\s*', opc) if x.strip()]
    nota = ' · '.join(limpa(x).replace('\n', ' ') for x in (principal, secundaria) if x)

    def pagina(k, s, txt):
        return [{'rotulo': 'Principal', 'pecas': [runa(n, por_runa) for n in [k] + menores]},
                {'rotulo': 'Secundária', 'pecas': [runa(n, por_runa) for n in s], 'nota': txt}]
    saida = [pagina(k, sec, nota) for k in keystones]
    if opc:
        saida.append(pagina(keystones[0], opc, limpa(opcional).replace('\n', ' ')))
    return saida


def item(nome, por_item):
    n = re.sub(r'^(?:\d+x|x\d+)\s+|\s+(?:x\d+|\(x\d+\))$|^(?:finish|rush)\s+', '', limpa(nome).rstrip('.'), flags=re.I).strip()
    n = {'ibg': 'Iceborn Gauntlet', 'randuins omen': "Randuin's Omen", 'dorans helm': "Doran's Helm", 'bramble': 'Bramble Vest',
         'kaenic': 'Kaenic Rookern', 'negatron': 'Negatron Cloak', 'zekes': "Zeke's Convergence"}.get(n.lower(), n)
    return {'nome': n, 'icone': icone_item(n, por_item)}


def linha_build(texto, por_item):
    """'2x Chain Vest > finish Iceborn Gauntlet > Bramble Vest' -> passos; ',' e '/' separam alternativas e '+' junta
    compras (cada uma vira um passo)."""
    t = re.sub(r'^\((?:optional|alt\.?)\)\s*|^starting items:\s*', '', limpa(texto).replace('\n', ' '), flags=re.I)
    t = re.sub(r'^starting items:\s*', '', t, flags=re.I)
    passos = []
    for passo in re.split(r'\s*(?:>|\+)\s*', t):
        alts = [a for a in re.split(r'\s*[/,]\s*|\s+or\s+', passo) if a.strip()]
        if alts:
            passos.append([item(a, por_item) for a in alts])
    return {'tipo': 'item', 'texto': limpa(texto), 'passos': passos}


def vod(texto):
    """'Aatreus (Patch 25.05 | Midlane)' -> 'VOD (Patch 25.05 | Midlane)': sem o nome de quem jogou (pedido do autor)."""
    m = re.search(r'\(.*\)\s*$', limpa(texto))
    return f'VOD {m.group(0)}' if m else 'VOD'


def blocos_por_coluna(c, inicio, fim, col_rotulo, col_texto):
    """{rótulo: [textos]} das seções de um bloco (rótulo na coluna G, textos na H até o próximo rótulo)."""
    out, atual = defaultdict(list), None
    for r in range(inicio, fim):
        if (r, col_rotulo) in c:
            atual = limpa(c[r, col_rotulo])
        if atual and (r, col_texto) in c:
            out[atual].append(c[r, col_texto].strip())
    return out


def gerar_matchups(xl, links_por_texto, campeoes, por_runa, por_item):
    c = xl.celulas('Matchups')
    inicios = sorted(r for (r, k) in c if k == 0 and r >= 60 and (r, 2) in c and re.fullmatch(r'\d+(\.\d+)?', c[r, 2].strip()))
    por_nome = {}
    for ch in campeoes.values():
        por_nome[chave(ch['name'])] = ch
        por_nome[chave(ch['id'])] = ch
    saida = []
    for i, r0 in enumerate(inicios):
        fim = inicios[i + 1] if i + 1 < len(inicios) else max(r for r, _ in c) + 1
        nome = limpa(c[r0, 0])
        ch = por_nome[chave(nome)]  # falha se um campeão não for reconhecido
        valor = float(c[r0, 2])
        col3 = [(r, c[r, 3].strip()) for r in range(r0, fim) if (r, 3) in c]
        # Os VoDs ficam na coluna D, a partir da linha do rótulo "VoD's/Clips" (coluna A).
        vods_desde = next((r for r in range(r0, fim) if c.get((r, 0), '').strip().lower().startswith('vod')), None)
        # Coluna D: rótulos e o texto logo abaixo de cada um.
        rot = defaultdict(list)
        atual = None
        for r, t in col3:
            if vods_desde is not None and r >= vods_desde:
                rot['vods'].append(t)
            elif t in ('Recommended Runes', 'Secondary Rune Path(s)', 'Recommended Items'):
                atual = t
            else:
                rot[atual].append(t)
        runas_txt = rot['Recommended Runes']
        sec_txt = [t for t in rot['Secondary Rune Path(s)'] if not t.lower().startswith('(optional)')]
        opc_txt = [t for t in rot['Secondary Rune Path(s)'] if t.lower().startswith('(optional)')]
        runas = paginas_runas(runas_txt[0] if runas_txt else '', sec_txt[0] if sec_txt else '', opc_txt[0] if opc_txt else '', por_runa)
        linhas_itens = []
        for t in rot['Recommended Items']:
            if re.match(r'^\((?:optional|alt\.?)\)', t, re.I):
                rotulo = 'Optional' if t.lower().startswith('(optional') else 'Alternative'
                if re.search(r'starting items:', t, re.I):
                    rotulo = 'Alternative starting items'
                linhas_itens.append({'tipo': 'rotulo', 'texto': rotulo})
                linhas_itens.append(linha_build(t, por_item))
            elif not linhas_itens:
                linhas_itens.append(linha_build(t, por_item))
            else:
                linhas_itens.append({'tipo': 'nota', 'texto': limpa(t)})
        secs = blocos_por_coluna(c, r0, vods_desde or fim, 6, 7)
        secoes = [{'titulo': s, 'blocos': [{'tipo': 'p', 'texto': p} for t in secs[s] for p in t.split('\n') if p.strip()]}
                  for s in SECOES if secs.get(s)]
        if rot['vods']:
            secoes.append({'titulo': "VoD's/Clips", 'blocos': [{'tipo': 'links', 'itens': [
                {'texto': vod(t), 'url': (links_por_texto.get(limpa(t)) or [{}])[0].get('url')} for t in rot['vods']]}]})
        saida.append({
            'nome': ch['name'], 'planilha': nome, 'id': ch['id'], 'titulo': ch['title'],
            'dificuldade': {'overall': max(1, min(5, math.ceil(valor / 2))), 'valor': valor, 'texto': f'{valor:g}/10'},
            'tldr': [p for t in secs.get(RESUMO, []) for p in t.split('\n') if p.strip()],
            'runas': runas, 'imagens_runas': [],
            'itens': [{'rotulo': '', 'linhas': linhas_itens}] if linhas_itens else [],
            'secoes': secoes,
        })
    return saida


def p(texto):
    return {'tipo': 'p', 'texto': texto, 'links': []}


def gerar_paginas(xl, itens):
    """Página Geral com a página de runas, a build e a legenda das notas do cabeçalho; página Dificuldades com a nota
    de cada autor (aba "Difficulties", só os campeões com nota)."""
    c = xl.celulas('Matchups')
    imgs = xl.imagens('Matchups')
    pega = lambda r, k: limpa(c.get((r, k), ''))
    peca = lambda iid: {'nome': itens[iid]['name'], 'icone': f'{DD}/img/item/{iid}.png', 'id': iid}
    runas = {'tipo': 'secao', 'titulo': pega(9, 9) or 'Runes', 'partes': [
        p(pega(11, 9)), {'tipo': 'sub', 'texto': pega(11, 3)}, p(c[12, 3].strip()),
        {'tipo': 'sub', 'texto': pega(14, 3)}, p(c[15, 3].strip()), p(c[17, 3].strip()),
        {'tipo': 'sub', 'texto': pega(11, 14)}, {'tipo': 'sub', 'texto': pega(12, 14)}, p(pega(13, 14)),
        {'tipo': 'sub', 'texto': pega(16, 14)}, p(pega(17, 14)), p(pega(18, 14)),
        {'tipo': 'sub', 'texto': pega(19, 14)}, p(pega(20, 14)), p(pega(21, 14)),
        {'tipo': 'sub', 'texto': pega(23, 14)}, p(pega(24, 14)),
        {'tipo': 'sub', 'texto': pega(31, 14)},
        *[x for r in (32, 34, 36) for x in ({'tipo': 'p', 'texto': f'{c[r, 14].strip()}: {pega(r, 16)}', 'links': []},)],
    ]}
    core = [CORE_MD5[m] for r, k, _, m, _ in imgs if m in CORE_MD5]
    evitar = list(dict.fromkeys(EVITAR_MD5[m] for r, k, _, m, _ in imgs if m in EVITAR_MD5))
    iniciais = list(dict.fromkeys(INICIAIS_MD5[m] for r, k, _, m, _ in imgs if m in INICIAIS_MD5))
    outros = [pega(r, k) for r in range(47, 52) for k in (12, 13) if pega(r, k)]
    build = {'tipo': 'secao', 'titulo': pega(32, 8), 'partes': [
        {'tipo': 'sub', 'texto': pega(34, 8)},
        {'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [{'titulo': '', 'itens': [peca(i) for i in iniciais]}]}},
        p(pega(35, 10)), p(pega(37, 10)),
        {'tipo': 'sub', 'texto': pega(39, 8)},
        {'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [{'titulo': '', 'itens': [peca(i) for i in core]}]}},
        p(pega(46, 8)),
        {'tipo': 'sub', 'texto': pega(45, 12)},
        {'tipo': 'lista', 'itens': [{'texto': o.replace('\n', ' '), 'links': []} for o in outros]},
        {'tipo': 'sub', 'texto': pega(52, 8)},
        {'tipo': 'bloco', 'bloco': {'tipo': 'pecas', 'grupos': [{'titulo': '', 'itens': [peca(i) for i in evitar]}]}},
        p(pega(54, 9)), p(c.get((54, 11), '').strip()),
    ]}
    legenda = {'tipo': 'secao', 'titulo': pega(9, 3), 'partes': [
        p(pega(13, 0)), p(pega(11, 6)), p(pega(13, 6)), p(pega(15, 6)), p(pega(17, 6)), p(pega(22, 6)), p(pega(24, 6)),
        {'tipo': 'sub', 'texto': f'{pega(16, 0)} · {pega(16, 1)}'},
        {'tipo': 'lista', 'itens': [{'texto': f'{pega(r, 0)}: {pega(r, 1)}', 'links': []} for r in range(17, 22)]},
        p(pega(22, 0)),
    ]}
    atualizado = {'tipo': 'secao', 'titulo': pega(0, 16).replace('\n', ' '), 'partes': [
        {'tipo': 'lista', 'itens': [{'texto': l.lstrip('-> ').strip(), 'links': []} for l in c.get((5, 16), '').split('\n') if l.strip()]}]}
    # Aba Difficulties: Toplane (colunas B-E) e Midlane (J-M); só as linhas com nota de verdade.
    d = xl.celulas('Difficulties')
    tabelas = []
    for c0, rotulo in ((1, d.get((1, 1), 'Toplane')), (9, d.get((1, 9), 'Midlane'))):
        # Só campeão e média: as colunas de cada autor citam nomes, e o autor pediu para não ser citado.
        cab = [d.get((3, c0 + k), '') for k in range(2)]
        linhas = []
        for r in range(4, max(rr for rr, _ in d) + 1):
            nome, media = d.get((r, c0), ''), d.get((r, c0 + 1), '')
            if nome and re.fullmatch(r'\d+(\.\d+)?', media.strip()):
                linhas.append([{'texto': d.get((r, c0 + k), ''), 'links': []} for k in range(2)])
        if linhas:
            tabelas.append({'tipo': 'tabela', 'titulo': rotulo, 'colunas': cab, 'linhas': linhas})
    return [
        {'id': 'geral', 'titulo': 'Geral', 'titulo_en': 'Overview', 'blocos': [atualizado, runas, build, legenda]},
    ] + ([{'id': 'dificuldades', 'titulo': 'Dificuldades', 'titulo_en': 'Difficulties', 'blocos': tabelas}] if INCLUIR_DIFICULDADES else [])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xlsx', nargs='?', type=Path)
    args = parser.parse_args()
    xl = Planilha(args.xlsx.read_bytes() if args.xlsx else baixar(FONTE))
    if set(xl.abas) != {'Matchups', 'Difficulties'}:
        raise ValueError(f'Estrutura inesperada: abas {list(xl.abas)} (esperadas Matchups e Difficulties).')
    links_por_texto = {}
    try:
        for cel in publicado(baixar(PUBLICADA).decode('utf-8')).values():
            if cel['links']:
                links_por_texto.setdefault(limpa(cel['texto']), cel['links'])
    except OSError as e:
        print(f'  aviso: sem a versão publicada ({e}); os VoDs ficam sem link')
    campeoes = json.loads(baixar(f'{DD}/data/pt_BR/champion.json'))['data']
    itens = json.loads(baixar(f'{DD}/data/en_US/item.json'))['data']
    por_item, por_runa = montar_icones(itens, json.loads(baixar(f'{DD}/data/en_US/runesReforged.json')))
    matchups = gerar_matchups(xl, links_por_texto, campeoes, por_runa, por_item)
    paginas = gerar_paginas(xl, itens)
    DEST.mkdir(parents=True, exist_ok=True)
    # O autor autorizou o guia pedindo que nada faça referência a ele: só o link da planilha (2026-10-29).
    fonte = {'planilha': f'https://docs.google.com/spreadsheets/d/{PLANILHA}/edit'}
    for nome, valor in [('matchups.json', {'versao': VER, 'fonte': fonte, 'matchups': matchups}), ('paginas.json', paginas)]:
        (DEST / nome).write_text(json.dumps(valor, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    sem_icone = sorted({p['nome'] for m in matchups for g in m['itens'] for l in g['linhas'] if l['tipo'] == 'item'
                        for passo in l['passos'] for p in passo if not p['icone']}
                       | {p['nome'] for m in matchups for op in m['runas'] for l in op for p in l['pecas'] if not p['icone']})
    print(f'{len(matchups)} matchups, {len(paginas)} páginas; {sum(1 for m in matchups if m["runas"])} com runas; '
          f'{sum(1 for m in matchups for s in m["secoes"] if s["titulo"].startswith("VoD"))} com VoDs.')
    if sem_icone:
        print('  sem ícone:', sem_icone)


if __name__ == '__main__':
    main()
