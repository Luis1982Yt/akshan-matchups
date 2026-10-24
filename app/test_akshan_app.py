"""Testes sem o cliente do LoL: sessões de exemplo da seleção de campeões.

Rode com: python -m unittest app/test_akshan_app.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import akshan_app as app  # noqa: E402

# championId -> id do Data Dragon (só os usados aqui)
IDS = {166: "Akshan", 103: "Ahri", 238: "Zed", 157: "Yasuo", 99: "Lux", 222: "Jinx", 412: "Thresh",
       84: "Akali", 96: "KogMaw", 7: "Leblanc"}
# fração de partidas no mid (inventada, para o teste ser estável)
TAXAS = {103: 0.97, 238: 0.80, 157: 0.55, 99: 0.30, 222: 0.0, 412: 0.0, 84: 0.60}


def sessao(eu=0, intent=0, inimigos=()):
    return {
        "localPlayerCellId": 2,
        "myTeam": [{"cellId": 0, "championId": 222}, {"cellId": 2, "championId": eu, "championPickIntent": intent}],
        "theirTeam": [{"cellId": 5 + i, "championId": c} for i, c in enumerate(inimigos)],
    }


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestApp(unittest.TestCase):
    def setUp(self):
        self.dados = app.Dados(app.carrega_guia_local(), IDS, TAXAS)
        self.respostas = []
        self.abertos = []
        self.relogio = Relogio()
        self.m = app.Monitor(self.dados, lambda: self.respostas.pop(0), abre=self.abertos.append, agora=self.relogio)

    def roda(self, *respostas):
        for r in respostas:
            self.respostas.append(r)
            self.m.passo()
            self.relogio.t += 10

    def test_slug_igual_ao_site(self):
        self.assertEqual(app.slug("Kog'Maw"), "kogmaw")
        self.assertEqual(app.slug("Aurelion Sol"), "aurelion-sol")
        self.assertEqual(app.slug("Vel'Koz"), "velkoz")
        self.assertEqual(app.slug("LeBlanc"), "leblanc")
        self.assertEqual(app.slug("Dr. Mundo"), "dr-mundo")
        self.assertEqual(app.slug("Nunu & Willump"), "nunu-&-willump")
        self.assertEqual(app.slug("Gália Ção"), "galia-cao")

    def test_fora_da_selecao(self):
        self.roda(("fora", None))
        self.assertEqual(self.m.estado, "fora")
        self.assertEqual(self.abertos, [])
        self.roda(("sem_cliente", None))
        self.assertEqual(self.m.estado, "sem_cliente")

    def test_jogador_sem_akshan(self):
        self.roda(("ok", sessao(eu=99, inimigos=[103])))
        self.assertEqual(self.m.estado, "outro")
        self.assertEqual(self.abertos, [])

    def test_akshan_com_um_inimigo_no_guia(self):
        self.roda(("ok", sessao(eu=166, inimigos=[222, 412, 103])))
        self.assertEqual(self.m.estado, "akshan")
        self.assertEqual(self.abertos, [app.url_matchup("ahri")])
        # repetir a mesma sessão não abre de novo
        self.roda(("ok", sessao(eu=166, inimigos=[222, 412, 103])))
        self.assertEqual(len(self.abertos), 1)

    def test_pick_intent_conta(self):
        self.roda(("ok", sessao(eu=0, intent=166, inimigos=[238])))
        self.assertEqual(self.abertos, ["https://akshan-matchups.vercel.app/#akshan/zed"])

    def test_varios_inimigos_escolhe_maior_taxa_de_mid(self):
        self.roda(("ok", sessao(eu=166, inimigos=[99, 157, 238])))
        self.assertEqual(self.abertos, [app.url_matchup("zed")])

    def test_aparece_inimigo_com_mais_cara_de_mid(self):
        self.roda(("ok", sessao(eu=166, inimigos=[157])),
                  ("ok", sessao(eu=166, inimigos=[157, 99])),
                  ("ok", sessao(eu=166, inimigos=[157, 99, 103])))
        self.assertEqual(self.abertos, [app.url_matchup("yasuo"), app.url_matchup("ahri")])

    def test_inimigo_trocado(self):
        self.roda(("ok", sessao(eu=166, inimigos=[103, 157])))
        # trocaram a Ahri por um campeão fora do guia: vai para o Yasuo
        self.roda(("ok", sessao(eu=166, inimigos=[222, 157])))
        self.assertEqual(self.abertos, [app.url_matchup("ahri"), app.url_matchup("yasuo")])

    def test_intervalo_minimo(self):
        self.respostas.append(("ok", sessao(eu=166, inimigos=[157])))
        self.m.passo()
        self.relogio.t += 1
        self.respostas.append(("ok", sessao(eu=166, inimigos=[157, 103])))
        self.m.passo()
        self.assertEqual(len(self.abertos), 1)  # cedo demais
        self.relogio.t += 10
        self.respostas.append(("ok", sessao(eu=166, inimigos=[157, 103])))
        self.m.passo()
        self.assertEqual(self.abertos[-1], app.url_matchup("ahri"))

    def test_sem_taxas_usa_ordem_do_guia(self):
        self.m.dados = app.Dados(self.dados.guia, IDS, {})
        self.roda(("ok", sessao(eu=166, inimigos=[238, 103])))
        self.assertEqual(self.abertos, [app.url_matchup("ahri")])  # Ahri vem antes do Zed no guia

    def test_nomes_diferentes_do_ddragon(self):
        self.m.dados = app.Dados(self.dados.guia, IDS, {})
        self.roda(("ok", sessao(eu=166, inimigos=[96])))
        self.assertEqual(self.abertos, [app.url_matchup("kogmaw")])

    def test_nova_selecao_reabre(self):
        self.roda(("ok", sessao(eu=166, inimigos=[103])), ("fora", None), ("ok", sessao(eu=166, inimigos=[103])))
        self.assertEqual(len(self.abertos), 2)

    def test_lista_de_inimigos(self):
        self.roda(("ok", sessao(eu=166, inimigos=[103, 222])))
        self.assertEqual([(i["nome"], i["slug"]) for i in self.m.inimigos], [("Ahri", "ahri"), ("Jinx", None)])
        self.m.abre_manual("ahri")
        self.assertEqual(self.m.alvo, "ahri")

    def test_le_rows_com_virgula_no_fim(self):
        self.assertEqual(app.le_rows('[\n["Ahri",1],\n["Zed",0],\n]\n'), [["Ahri", 1], ["Zed", 0]])


if __name__ == "__main__":
    unittest.main()
