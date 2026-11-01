"""Monta o guia do Azir mid a partir dos slides do Eleyte e do Lord Laki ("Azir guide", Google Slides, season 11).

Uso: python scripts/atualizar_azir.py
Os slides abrem para quem tem o link e o Google entrega o .pptx (export). Gera src/guias/azir/matchups.json e paginas.json.

Cada matchup é um slide: nome + título do campeão, "Difficulty : <rótulo>" e uma caixa de dicas. As dicas em rosa são as
que os autores marcaram como de jogo agressivo (explicado no slide "Aggressive Azir playstyle"); as laranja são as normais.
A fonte é de 2021 (season 11, itens míticos): por decisão do dono (2026-11-01) entram só a dificuldade e as dicas de rota;
as runas, feitiços e itens de cada matchup e as páginas de build ficam de fora. "About us", o painel de recados e o
anúncio do app deles também (são sobre os autores).
"""
import io
import re

from pptx import Presentation

from guia_comum import Ddragon, baixar, gravar_guia

ID = '1NpY9_GkE0qtJVqomq_CsvBntYKug1B0LGbzq1a6J_Zw'
SLIDES = f'https://docs.google.com/presentation/d/{ID}/edit'
PPTX = f'https://docs.google.com/presentation/d/{ID}/export/pptx'
ROSA = {'EA9999', 'E06666'}  # cor das dicas de jogo agressivo
# Rótulo dos autores -> nota de 1 a 5. "Buy a bed and go to sleep" (Heimerdinger) é a piada deles para "fácil demais".
NOTAS = {'very easy': 1, 'buy a bed and go to sleep': 1, 'easy': 2, 'easy/medium': 2, 'easy/moderate': 2,
         'medium': 3, 'medium/hard': 4, 'hard': 5}


def textos(slide):
    return [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]


def cor(par):
    for r in par.runs:
        try:
            if r.text.strip() and r.font.color and r.font.color.type is not None:
                return str(r.font.color.rgb)
        except AttributeError:
            pass
    return None


def dicas(caixa):
    """Parágrafos da caixa de dicas -> [(dica, agressiva?)]. Cada dica começa com '-'; quebra de linha manual (\\x0b)
    e '- ' no meio do parágrafo também abrem dica nova. O texto da dica não muda."""
    saida = []
    for par in caixa.text_frame.paragraphs:
        agressiva = cor(par) in ROSA
        for linha in re.split(r'\x0b|\n|(?<=[.!?)])\s*(?=-\s?[A-Z/])', par.text):
            t = linha.strip()
            if not t:
                continue
            if t.startswith('-') or not saida:
                saida.append([t.lstrip('-').strip(), agressiva])
            else:
                saida[-1][0] += ' ' + t
    return [(t, a) for t, a in saida if t]


def gerar_matchups(p, dd):
    saida = []
    for slide in list(p.slides)[17:]:
        caixas = textos(slide)
        # Cabeçalho: a caixa curta cuja primeira linha é um campeão (a ordem das caixas muda de slide para slide).
        cab, ch = None, None
        for c in caixas:
            primeira = c.text_frame.text.strip().split('\n')[0].strip()
            if len(c.text_frame.text) < 60 and not primeira.startswith(('Difficulty', 'BACK')):
                try:
                    cab, ch = c, dd.campeao(primeira)
                    break
                except KeyError:
                    pass
        if not ch:
            raise KeyError('slide sem campeão reconhecido: ' + ' | '.join(c.text_frame.text[:30] for c in caixas))
        nome = cab.text_frame.text.strip().split('\n')[0].strip()
        rotulo = next((re.sub(r'^Difficulty\s*:\s*', '', c.text_frame.text).strip() for c in caixas
                       if re.match(r'(Difficulty\s*:|(Very )?(Easy|Medium|Hard))', c.text_frame.text.strip())), '')
        corpo = [c for c in caixas if c is not cab and len(c.text_frame.text) > 60]
        if not corpo:
            continue  # slide ainda em construção pelos autores (Akshan, Vex)
        todas = [d for c in corpo for d in dicas(c)]
        normais = [t for t, a in todas if not a]
        agressivas = [t for t, a in todas if a]
        secoes = [{'titulo': 'Tips', 'blocos': [{'tipo': 'lista', 'itens': normais}]}] if normais else []
        if agressivas:
            secoes.append({'titulo': 'Aggressive playstyle', 'blocos': [{'tipo': 'lista', 'itens': agressivas}]})
        saida.append({
            'nome': ch['name'], 'planilha': nome, 'id': ch['id'], 'titulo': ch['title'], 'rota': 'Mid',
            'dificuldade': {'overall': NOTAS[rotulo.lower()], 'texto': rotulo},
            'tldr': [], 'feiticos': [], 'runas': [], 'imagens_runas': [], 'itens': [], 'secoes': secoes,
        })
    return saida


def gerar_paginas(p):
    def caixa(i, comeco):
        return next(c.text_frame.text for c in textos(p.slides[i]) if c.text_frame.text.startswith(comeco))
    sobre = caixa(3, 'Azir is')
    gerais = [re.sub(r'^\d+\.\s*', '', l).strip() for l in caixa(4, '1.').split('\n') if l.strip()]
    agressivo = caixa(8, '- /Laki').lstrip('- ').strip()
    p_ = lambda t: {'tipo': 'p', 'texto': t, 'links': []}
    return [{'id': 'geral', 'titulo': 'Geral', 'titulo_en': 'Overview', 'blocos': [
        {'tipo': 'secao', 'titulo': 'About Champion', 'partes': [p_(sobre)]},
        {'tipo': 'secao', 'titulo': 'General tips', 'partes': [
            {'tipo': 'lista', 'numerada': True, 'itens': [{'texto': t, 'links': []} for t in gerais]}]},
        {'tipo': 'secao', 'titulo': 'Aggressive Azir playstyle', 'partes': [p_(agressivo)]},
    ]}]


def main():
    p = Presentation(io.BytesIO(baixar(PPTX)))
    dd = Ddragon()
    matchups = gerar_matchups(p, dd)
    paginas = gerar_paginas(p)
    gravar_guia('azir', matchups, paginas, {'planilha': SLIDES, 'autor': 'Eleyte e Lord Laki'})
    print(f'{len(matchups)} matchups, {len(paginas)} páginas')


if __name__ == '__main__':
    main()
