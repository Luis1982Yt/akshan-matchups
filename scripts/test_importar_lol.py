"""Testes do importar_lol.py sem internet: fragmentos e montagem da página de runas.

Rode com: python -m unittest scripts/test_importar_lol.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importar_lol as imp  # noqa: E402

AF, AS, AH, MS, HPN, HP, TEN = 5008, 5005, 5007, 5010, 5001, 5011, 5013


def runa(id_, arvore, linha):
    return {"id": id_, "arvore": arvore, "linha": linha, "nome": str(id_)}


# Precisão (8000) e Determinação (8400), com os ids do jogo.
CONQ, TRIUNFO, ALACRIDADE, ATE_A_MORTE = runa(8010, 8000, 0), runa(9111, 8000, 1), runa(9104, 8000, 2), runa(8014, 8000, 3)
PRESENCA = runa(8009, 8000, 1)
GOLPE, OSSO, VENTOS, REVIT = runa(8401, 8400, 1), runa(8473, 8400, 2), runa(8444, 8400, 2), runa(8453, 8400, 3)


class TestFragmentos(unittest.TestCase):
    def test_ordem_das_linhas(self):
        self.assertEqual(imp.fragmentos(["Attack Speed", "Movement Speed", "Flat Health"]), [AS, MS, HP])

    def test_dupla_e_seta_no_mesmo_nome(self):
        self.assertEqual(imp.fragmentos(["Double Adaptive -> Flat Health"]), [AF, AF, HP])
        self.assertEqual(imp.fragmentos(["Double Adaptive", "Scaling Health"]), [AF, AF, HPN])

    def test_fora_de_ordem_encaixa_todos(self):
        self.assertEqual(imp.fragmentos(["Tenacity / Slow Resist", "Adaptive Force", "Attack Speed"]), [AS, AF, TEN])

    def test_nomes_da_illaoi(self):
        self.assertEqual(imp.fragmentos(["Adp force", "Adp force", "Scaling Health"]), [AF, AF, HPN])
        self.assertEqual(imp.fragmentos(["Adp force", "Movement Speed Shard", "Scaling health"]), [AF, MS, HPN])

    def test_sem_fragmento_usa_o_padrao(self):
        self.assertEqual(imp.fragmentos([]), imp.FRAG_PADRAO)


class TestPagina(unittest.TestCase):
    def test_pagina_completa(self):
        pg = imp.pagina([CONQ, TRIUNFO, ALACRIDADE, ATE_A_MORTE], [GOLPE, OSSO], [AS, MS, HP])
        self.assertEqual(pg, {"primaryStyleId": 8000, "subStyleId": 8400,
                              "selectedPerkIds": [8010, 9111, 9104, 8014, 8401, 8473, AS, MS, HP]})

    def test_alternativas_vale_a_primeira_de_cada_linha(self):
        # "Second Wind OR Bone Plating": duas da mesma linha na secundária -> fica a primeira e entra a da outra linha.
        pg = imp.pagina([CONQ, TRIUNFO, PRESENCA, ALACRIDADE, ATE_A_MORTE], [VENTOS, OSSO, REVIT], [AF, AF, HP])
        self.assertEqual(pg["selectedPerkIds"][:6], [8010, 9111, 9104, 8014, 8444, 8453])

    def test_incompleta_nao_vira_pagina(self):
        self.assertIsNone(imp.pagina([CONQ, TRIUNFO], [GOLPE, OSSO], [AF, AF, HP]))
        self.assertIsNone(imp.pagina([CONQ, TRIUNFO, ALACRIDADE, ATE_A_MORTE], [GOLPE], [AF, AF, HP]))
        self.assertIsNone(imp.pagina([CONQ, TRIUNFO, ALACRIDADE, ATE_A_MORTE], [PRESENCA, GOLPE], [AF, AF, HP]))


if __name__ == "__main__":
    unittest.main()
