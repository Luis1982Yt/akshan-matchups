"""Testes do contrato e preservação; Excel original opcional em KAYLE_XLSX ou TEMP."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atualizar_kayle import CABECALHOS_MATCHUPS, CONVITES, ROOT, dificuldade, itens_iniciais, runas, salvar_imagem
from planilha_xlsx import Planilha


def strings(valor):
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, dict):
        for v in valor.values():
            yield from strings(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from strings(v)


class ImportadorKayle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pasta = ROOT / 'src/guias/kayle'
        cls.dados = json.loads((pasta / 'matchups.json').read_text(encoding='utf-8'))
        cls.matchups = cls.dados['matchups']
        cls.paginas = json.loads((pasta / 'paginas.json').read_text(encoding='utf-8'))

    def test_dificuldades(self):
        for n in range(1, 11):
            d = dificuldade(f'{n}.0')
            self.assertEqual(d, {'overall': (n + 1) // 2, 'valor': n, 'texto': f'{n}/10'})
        self.assertIsNone(dificuldade('Stop Playing Normals')['overall'])
        with self.assertRaises(ValueError):
            dificuldade('11')

    def test_171_e_yone(self):
        self.assertEqual(len(self.matchups), 171)
        self.assertEqual(len({m['id'] for m in self.matchups}), 171)
        yone = next(m for m in self.matchups if m['id'] == 'Yone')
        self.assertEqual(yone['dificuldade'], {
            'overall': 5, 'valor': 10, 'texto': '8 if midlane. 10 if toplane.'})
        for m in self.matchups:
            self.assertEqual(bool(m['feiticos']), m['id'] != 'Kayle')
            self.assertTrue(all(p['icone'] for p in m['feiticos']))
            self.assertEqual(len(m['imagens_runas']), 0 if m['id'] == 'Kayle' else 1)

    def test_imagem_ausente_somente_no_espelho_kayle(self):
        ausentes = [m['id'] for m in self.matchups if not m['imagens_runas']]
        self.assertEqual(len(ausentes), 1)
        self.assertEqual(ausentes, ['Kayle'])
        self.assertEqual(sum(len(m['imagens_runas']) for m in self.matchups), 170)

    def test_nao_completa_runas(self):
        rs = runas('Press the Attack.', 'Sorcery w/Celerity & GS.', {})[0]
        self.assertEqual(len(rs[0]['pecas']), 1)
        self.assertEqual([p['nome'] for p in rs[1]['pecas']], ['Celerity', 'Gathering Storm'])
        self.assertEqual(runas('Lethal Tempo.', 'Resolve', {})[0][1]['pecas'], [])

    def test_iniciais_e_alternativas_preservam_nota(self):
        original = "Doran's Shield or Ring."
        linhas = itens_iniciais(original)
        self.assertEqual(linhas[0]['texto'], original)
        self.assertEqual(len(linhas[1]['passos']), 1)
        self.assertEqual([p['nome'] for p in linhas[1]['passos'][0]], ["Doran's Shield", "Doran's Ring"])
        linhas = itens_iniciais('Cloth Armour + 4 Health Potions Start')
        self.assertEqual(len(linhas[1]['passos']), 2)
        self.assertEqual(itens_iniciais('Rush Tier 2 boots')[0]['texto'], 'Rush Tier 2 boots')
        self.assertEqual(len(itens_iniciais('Rush Tier 2 boots')), 1)

    def test_paginas_e_imagens(self):
        self.assertEqual([p['id'] for p in self.paginas], [
            'geral', 'runas', 'itens', 'macro', 'dicas', 'habilidades', 'ameacas', 'inspiracao', 'notas'])
        for p in self.paginas:
            self.assertTrue(p['titulo_en'])
            self.assertTrue(p['titulo'])
            self.assertTrue(all(b['tipo'] == 'secao' for b in p['blocos']))
            self.assertTrue(all(x['tipo'] in {'p', 'sub', 'lista', 'imagens', 'bloco'} for b in p['blocos'] for x in b['partes']))
        self.assertEqual(self.dados['fonte']['aviso'], 'September 2026: The spreadsheet is NOT up to date.')
        for p in self.paginas:
            for b in p['blocos']:
                for x in b['partes']:
                    for img in x.get('imagens', []):
                        self.assertEqual(img['alt'], f'{p["titulo_en"]} — UJard')
                        self.verificar_imagem(img)
        for m in self.matchups:
            for img in m['imagens_runas']:
                self.verificar_imagem(img)
        itens = next(p for p in self.paginas if p['id'] == 'itens')
        bloco = next(x['bloco'] for b in itens['blocos'] for x in b['partes'] if x['tipo'] == 'bloco' and 'codigo_importacao' in x['bloco'])
        conjunto = json.loads(bloco['codigo_importacao'])
        self.assertEqual([[i['id'] for i in g['itens']] for g in bloco['grupos']],
                         [[i['id'] for i in g['items']] for g in conjunto['blocks']])
        self.assertFalse(any(i['nome'].startswith('Item ') for g in bloco['grupos'] for i in g['itens']))

    def verificar_imagem(self, img):
        arq = ROOT / img['src']
        self.assertTrue(img['alt'])
        self.assertEqual(arq.stem, hashlib.sha256(arq.read_bytes()).hexdigest())
        with Image.open(arq) as im:
            self.assertEqual(im.format, 'PNG')
            self.assertEqual(im.size, (img['largura'], img['altura']))

    def test_png_sem_perdas_e_deduplicacao(self):
        im = Image.new('RGBA', (17, 13), (37, 64, 90, 120))
        buf = io.BytesIO()
        im.save(buf, 'PNG')
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            a = salvar_imagem(buf.getvalue(), 'Original A', pasta)
            b = salvar_imagem(buf.getvalue(), 'Original B', pasta)
            self.assertEqual(a['src'], b['src'])
            self.assertEqual(len(list(pasta.iterdir())), 1)
            with Image.open(next(pasta.iterdir())) as gravada:
                self.assertEqual(gravada.tobytes(), im.tobytes())

    def test_todas_celulas_originais(self):
        arquivo = Path(os.environ.get('KAYLE_XLSX', Path(os.environ.get('TEMP', tempfile.gettempdir())) / 'kayle-ujard.xlsx'))
        if not arquivo.exists():
            self.skipTest('Defina KAYLE_XLSX para conferir contra o original')
        xl = Planilha(arquivo.read_bytes())
        abas = list(xl.abas)
        c = xl.celulas(abas[0])
        for r, m in enumerate(self.matchups, 6):
            self.assertEqual(m['planilha'], c[r, 2])
            self.assertEqual(m['feiticos_texto'], c.get((r, 4), ''))
            self.assertEqual(m['runas_texto'], c.get((r, 5), ''))
            self.assertEqual(m['secundarias_texto'], c.get((r, 6), ''))
            if (r, 8) in c:
                self.assertEqual(m['itens'][0]['linhas'][0]['texto'], c[r, 8])
            if (r, 9) in c:
                self.assertEqual(m['secoes'][0]['blocos'][0]['texto'], c[r, 9])
        textos = set(strings(self.paginas))
        for aba in abas[1:]:
            for pos, original in xl.celulas(aba).items():
                # Convites repetidos (o link fica só na Geral) e frases com ícone de runa no meio (o nome entra no buraco).
                if not CONVITES.match(original.strip()) and '    ' not in original.strip():
                    self.assertIn(original, textos, (aba, pos, original))
        for (r, col), original in c.items():
            if (r < 6 or col > 9 or r >= 177) and not original.startswith(CABECALHOS_MATCHUPS):
                self.assertIn(original, textos)


if __name__ == '__main__':
    unittest.main()
