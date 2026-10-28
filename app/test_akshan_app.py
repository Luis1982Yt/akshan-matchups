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
       84: "Akali", 96: "KogMaw", 7: "Leblanc", 82: "Mordekaiser", 420: "Illaoi", 122: "Darius", 266: "Aatrox", 36: "DrMundo"}
# fração de partidas em cada rota (inventada, para o teste ser estável)
TAXAS = {103: {"MIDDLE": 0.97}, 238: {"MIDDLE": 0.80, "TOP": 0.1}, 157: {"MIDDLE": 0.55, "TOP": 0.35}, 99: {"MIDDLE": 0.30, "UTILITY": 0.7},
         222: {"BOTTOM": 1.0}, 412: {"UTILITY": 1.0}, 84: {"MIDDLE": 0.60, "TOP": 0.4},
         122: {"TOP": 0.95}, 266: {"TOP": 0.98}, 36: {"TOP": 0.7, "JUNGLE": 0.3}}


def sessao(eu=0, intent=0, inimigos=(), travado=True, turnos=True):
    """Seleção com turnos: a ação "pick" do jogador fica concluída quando ele trava (lock-in).
    turnos=False imita os modos sem escolha (ARAM), em que o campeão já vem dado."""
    s = {
        "localPlayerCellId": 2,
        "myTeam": [{"cellId": 0, "championId": 222}, {"cellId": 2, "championId": eu, "championPickIntent": intent}],
        "theirTeam": [{"cellId": 5 + i, "championId": c} for i, c in enumerate(inimigos)],
    }
    if turnos:
        s["actions"] = [[{"actorCellId": 0, "type": "pick", "championId": 222, "completed": True}],
                        [{"actorCellId": 2, "type": "pick", "championId": eu or intent, "completed": travado and bool(eu)}]]
    return s


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestApp(unittest.TestCase):
    def setUp(self):
        self.dados = app.Dados(app.carrega_guias_local(), IDS, TAXAS)
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

    def test_lista_de_guias_do_site(self):
        ids = {g["id"]: (g["chave"], g["rota"]) for g in self.dados.guias}
        self.assertEqual(ids["akshan"], (166, "MIDDLE"))
        self.assertEqual(ids["mordekaiser"], (82, "TOP"))
        self.assertEqual(ids["illaoi"], (420, "TOP"))

    def test_fora_da_selecao(self):
        self.roda(("fora", None))
        self.assertEqual(self.m.estado, "fora")
        self.assertEqual(self.abertos, [])
        self.roda(("sem_cliente", None))
        self.assertEqual(self.m.estado, "sem_cliente")

    def test_campeao_sem_guia(self):
        self.roda(("ok", sessao(eu=99, inimigos=[103])))
        self.assertEqual(self.m.estado, "outro")
        self.assertEqual(self.abertos, [])

    def test_akshan_com_um_inimigo_no_guia(self):
        self.roda(("ok", sessao(eu=166, inimigos=[222, 412, 103])))
        self.assertEqual(self.m.estado, "guia")
        self.assertEqual(self.abertos, [app.url_matchup("akshan", "ahri")])
        # repetir a mesma sessão não abre de novo
        self.roda(("ok", sessao(eu=166, inimigos=[222, 412, 103])))
        self.assertEqual(len(self.abertos), 1)

    def test_so_abre_depois_do_lock(self):
        # Só marcado ou com o mouse em cima: não abre nada.
        self.roda(("ok", sessao(intent=166, inimigos=[238])), ("ok", sessao(eu=166, inimigos=[238], travado=False)))
        self.assertEqual(self.abertos, [])
        self.assertEqual(self.m.estado, "outro")
        self.roda(("ok", sessao(eu=166, inimigos=[238])))
        self.assertEqual(self.abertos, ["https://akshan-matchups.vercel.app/#akshan/zed"])

    def test_sem_turnos_vale_o_campeao_recebido(self):
        self.roda(("ok", sessao(eu=82, inimigos=[122], turnos=False)))
        self.assertEqual(self.abertos, [app.url_matchup("mordekaiser", "darius")])

    def test_partida_comecou_esconde_e_nao_abre(self):
        escondidas = []
        self.m.esconde = lambda: escondidas.append(1)
        self.roda(("ok", sessao(eu=166, inimigos=[103])), ("jogo", None), ("jogo", None))
        self.assertEqual(len(escondidas), 1)  # esconde uma vez, quando a partida começa
        self.assertEqual(self.m.estado, "jogo")
        self.assertEqual(len(self.abertos), 1)

    def test_varios_inimigos_escolhe_maior_taxa_de_mid(self):
        self.roda(("ok", sessao(eu=166, inimigos=[99, 157, 238])))
        self.assertEqual(self.abertos, [app.url_matchup("akshan", "zed")])

    def test_mordekaiser_escolhe_o_top(self):
        self.roda(("ok", sessao(eu=82, inimigos=[103, 122, 222])))
        self.assertEqual(self.m.estado, "guia")
        self.assertEqual(self.abertos, [app.url_matchup("mordekaiser", "darius")])

    def test_illaoi_escolhe_o_top_e_usa_o_slug_do_guia(self):
        self.roda(("ok", sessao(eu=420, inimigos=[103, 36])))
        self.assertEqual(self.abertos, [app.url_matchup("illaoi", "dr-mundo")])

    def test_trocar_de_campeao_troca_de_guia(self):
        # Troca de campeão com um aliado (ARAM ou troca no fim da seleção).
        self.roda(("ok", sessao(eu=166, inimigos=[157], turnos=False)), ("ok", sessao(eu=82, inimigos=[157], turnos=False)))
        self.assertEqual(self.abertos, [app.url_matchup("akshan", "yasuo"), app.url_matchup("mordekaiser", "yasuo")])

    def test_aparece_inimigo_com_mais_cara_de_mid(self):
        self.roda(("ok", sessao(eu=166, inimigos=[157])),
                  ("ok", sessao(eu=166, inimigos=[157, 99])),
                  ("ok", sessao(eu=166, inimigos=[157, 99, 103])))
        self.assertEqual(self.abertos, [app.url_matchup("akshan", "yasuo"), app.url_matchup("akshan", "ahri")])

    def test_inimigo_trocado(self):
        self.roda(("ok", sessao(eu=166, inimigos=[103, 157])))
        # trocaram a Ahri por um campeão fora do guia: vai para o Yasuo
        self.roda(("ok", sessao(eu=166, inimigos=[222, 157])))
        self.assertEqual(self.abertos, [app.url_matchup("akshan", "ahri"), app.url_matchup("akshan", "yasuo")])

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
        self.assertEqual(self.abertos[-1], app.url_matchup("akshan", "ahri"))

    def test_sem_taxas_usa_ordem_do_guia(self):
        self.m.dados = app.Dados(self.dados.guias, IDS, {})
        self.roda(("ok", sessao(eu=166, inimigos=[238, 103])))
        self.assertEqual(self.abertos, [app.url_matchup("akshan", "ahri")])  # Ahri vem antes do Zed no guia

    def test_nomes_diferentes_do_ddragon(self):
        self.m.dados = app.Dados(self.dados.guias, IDS, {})
        self.roda(("ok", sessao(eu=166, inimigos=[96])))
        self.assertEqual(self.abertos, [app.url_matchup("akshan", "kogmaw")])

    def test_nova_selecao_reabre(self):
        self.roda(("ok", sessao(eu=166, inimigos=[103])), ("fora", None), ("ok", sessao(eu=166, inimigos=[103])))
        self.assertEqual(len(self.abertos), 2)

    def test_lista_de_inimigos(self):
        self.roda(("ok", sessao(eu=166, inimigos=[103, 222])))
        self.assertEqual([(i["nome"], i["slug"]) for i in self.m.inimigos], [("Ahri", "ahri"), ("Jinx", None)])
        self.m.abre_manual("ahri")
        self.assertEqual(self.m.alvo, "ahri")
        self.assertEqual(self.m.url_alvo(), app.url_matchup("akshan", "ahri"))


class LcuFalso(app.Lcu):
    """Cliente de mentira: guarda as chamadas e responde como a API do LoL (runas e conjuntos de itens)."""

    def __init__(self, paginas, total=2, conjuntos=None, fechado=False):
        super().__init__()
        self.paginas, self.total, self.conjuntos, self.fechado = paginas, total, conjuntos or [], fechado
        self.chamadas = []

    def _pede(self, metodo, caminho, **kw):
        if self.fechado:
            raise RuntimeError("cliente fechado")
        self.chamadas.append((metodo, caminho))
        if caminho == "/lol-perks/v1/pages" and metodo == "GET":
            return self.paginas
        if caminho == "/lol-perks/v1/inventory":
            return {"ownedPageCount": self.total}
        if metodo == "DELETE":
            self.paginas = [p for p in self.paginas if p["id"] != int(caminho.rsplit("/", 1)[1])]
            return None
        if metodo == "POST":
            nova = {**kw["json"], "id": 900, "isDeletable": True}
            self.paginas.append(nova)
            return nova
        if caminho == "/lol-summoner/v1/current-summoner":
            return {"summonerId": 7, "accountId": 70}
        if metodo == "GET":
            return {"accountId": 70, "itemSets": self.conjuntos, "timestamp": 1}
        if metodo == "PUT":
            self.conjuntos = kw["json"]["itemSets"]
        return None


PRESET = {"id": 50, "name": "Padrão", "isDeletable": False}


class TestImportar(unittest.TestCase):
    def setUp(self):
        self.guias = {g["id"]: g for g in app.carrega_guias_local()}

    def test_dados_de_importacao_no_guias_app(self):
        aatrox = self.guias["mordekaiser"]["importar"]["aatrox"]
        self.assertEqual(len(aatrox["runas"][0]["selectedPerkIds"]), 9)
        self.assertEqual(aatrox["runas"][0]["primaryStyleId"], 8000)  # Conquistador
        self.assertIn("3076", aatrox["itens"][0]["itens"])  # Colete Espinhoso
        self.assertEqual(len(self.guias["illaoi"]["importar"]["darius"]["runas"]), 2)  # Opção 1 e Opção 2
        ahri = self.guias["akshan"]["importar"]["ahri"]["runas"][0]
        self.assertEqual(ahri["selectedPerkIds"][:4], [8005, 8009, 9104, 8017])  # PTA, Presença de Espírito, Espontaneidade, Dilacerar

    def test_com_espaco_cria_pagina_sem_apagar(self):
        lcu = LcuFalso([PRESET, {"id": 1, "isDeletable": True, "current": True}], total=2)
        novo = lcu.grava_runas({"primaryStyleId": 8000}, "Mordekaiser vs Aatrox", None)
        self.assertEqual(novo, 900)
        self.assertNotIn("DELETE", [m for m, _ in lcu.chamadas])
        self.assertTrue(lcu.paginas[-1]["current"])

    def test_cheia_troca_a_pagina_atual(self):
        lcu = LcuFalso([PRESET, {"id": 1, "isDeletable": True}, {"id": 2, "isDeletable": True, "current": True}], total=2)
        lcu.grava_runas({"primaryStyleId": 8000}, "x", None)
        self.assertIn(("DELETE", "/lol-perks/v1/pages/2"), lcu.chamadas)

    def test_reaproveita_a_pagina_do_app(self):
        lcu = LcuFalso([{"id": 1, "isDeletable": True}, {"id": 9, "isDeletable": True, "current": True}], total=5)
        lcu.grava_runas({"primaryStyleId": 8000}, "x", 1)
        self.assertIn(("DELETE", "/lol-perks/v1/pages/1"), lcu.chamadas)
        self.assertNotIn(("DELETE", "/lol-perks/v1/pages/9"), lcu.chamadas)

    def test_conjunto_troca_so_o_do_app(self):
        dele = {"uid": "meu-conjunto", "title": "Meu"}
        velho = {"uid": "akshan-matchups-mordekaiser", "title": "Mordekaiser vs Fiora"}
        lcu = LcuFalso([], conjuntos=[dele, velho])
        guia = self.guias["mordekaiser"]
        lcu.grava_itens(app.conjunto_itens(guia, "Aatrox", guia["importar"]["aatrox"]["itens"], "pt"))
        self.assertEqual([c["title"] for c in lcu.conjuntos], ["Meu", "Mordekaiser vs Aatrox"])
        novo = lcu.conjuntos[-1]
        self.assertEqual(novo["associatedChampions"], [82])
        self.assertTrue(novo["blocks"][0]["type"].startswith("Se o Aatrox"))  # rótulo em português

    def test_importador_usa_a_opcao_e_guarda_a_pagina(self):
        lcu, cfg, salvos = LcuFalso([PRESET], total=2), {}, []
        imp = app.Importador(lcu, cfg, salvos.append, "pt")
        feito = imp.importa(self.guias["illaoi"], "darius", 1)
        self.assertEqual(feito, {"runas": True, "itens": True})
        self.assertEqual(lcu.paginas[-1]["selectedPerkIds"], self.guias["illaoi"]["importar"]["darius"]["runas"][1]["selectedPerkIds"])
        self.assertEqual(lcu.paginas[-1]["name"], "Illaoi vs Darius")
        self.assertEqual(cfg["pagina_runas"], 900)
        self.assertTrue(salvos)

    def test_cliente_fechado_nao_quebra(self):
        imp = app.Importador(LcuFalso([], fechado=True), {}, lambda c: None, "pt")
        self.assertEqual(imp.importa(self.guias["mordekaiser"], "aatrox"), {"runas": False, "itens": False})

    def test_monitor_importa_quando_abre_a_matchup(self):
        importados = []
        m = app.Monitor(app.Dados(app.carrega_guias_local(), IDS, TAXAS), lambda: ("ok", sessao(eu=82, inimigos=[122])),
                        abre=lambda u: None, agora=Relogio(), importa=lambda g, s: importados.append((g["id"], s)))
        m.passo()
        m.passo()  # mesma matchup: não importa de novo
        self.assertEqual(importados, [("mordekaiser", "darius")])


class TestAceitar(unittest.TestCase):
    def test_so_aceita_partida_esperando_resposta(self):
        self.assertTrue(app.deve_aceitar({"state": "InProgress", "playerResponse": "None"}))
        self.assertFalse(app.deve_aceitar({"state": "InProgress", "playerResponse": "Accepted"}))
        self.assertFalse(app.deve_aceitar({"state": "InProgress", "playerResponse": "Declined"}))
        self.assertFalse(app.deve_aceitar({"state": "Invalid", "playerResponse": "None"}))
        self.assertFalse(app.deve_aceitar(None))

    def test_aceitador_aceita_uma_vez(self):
        chamadas = []

        class Lcu:
            def __init__(self):
                self.rc = {"state": "InProgress", "playerResponse": "None"}

            def _pede(self, metodo, caminho, **kw):
                chamadas.append((metodo, caminho))
                if metodo == "POST":
                    self.rc = {"state": "InProgress", "playerResponse": "Accepted"}
                    return None
                return self.rc
        a = app.Aceitador(Lcu())
        self.assertTrue(a.passo())
        self.assertFalse(a.passo())
        self.assertEqual([c for c in chamadas if c[0] == "POST"], [("POST", "/lol-matchmaking/v1/ready-check/accept")])

    def test_sem_partida_encontrada(self):
        class Lcu:
            def _pede(self, metodo, caminho, **kw):
                raise RuntimeError("GET /lol-matchmaking/v1/ready-check: 404")
        self.assertFalse(app.Aceitador(Lcu()).passo())


if __name__ == "__main__":
    unittest.main()
