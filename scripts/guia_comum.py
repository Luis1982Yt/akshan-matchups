"""Peças comuns aos scripts de guia (scripts/atualizar_<campeão>.py): baixar, Data Dragon, nomes de campeão e item
como as planilhas escrevem, dificuldade, gravação dos arquivos do guia. Guia novo: importar daqui em vez de copiar
de outro script (passo a passo em .claude/skills/guia-novo/SKILL.md).

    from guia_comum import Ddragon, baixar, csv_aba, dificuldade_10, gravar_guia, limpa
    dd = Ddragon()                       # campeões (pt_BR), itens e runas (en_US) da versão do site
    ch = dd.campeao('Heimer')            # apelidos comuns já reconhecidos
    nome, icone = dd.item('Swifties')    # idem para itens; None se não achar
"""
import csv
import io
import json
import math
from pathlib import Path
import re
import urllib.request

from atualizar_mordekaiser import chave, icone_fragmento, montar_icones
from versao_dd import VER

ROOT = Path(__file__).resolve().parent.parent
DD = f'https://ddragon.leagueoflegends.com/cdn/{VER}'

# Como as planilhas costumam escrever os campeões (chave() do nome escrito -> id do Data Dragon).
APELIDO_CAMPEAO = {
    'fiddle': 'Fiddlesticks', 'heimer': 'Heimerdinger', 'asol': 'AurelionSol', 'aurelion': 'AurelionSol',
    'ksante': 'KSante', 'morde': 'Mordekaiser', 'trynd': 'Tryndamere', 'nunuwillump': 'Nunu', 'nunuandwillump': 'Nunu',
    'nunu': 'Nunu', 'wukong': 'MonkeyKing', 'mundo': 'DrMundo', 'drmundo': 'DrMundo', 'chogath': 'Chogath',
    'vlad': 'Vladimir', 'tf': 'TwistedFate', 'gp': 'Gangplank', 'ganglank': 'Gangplank', 'mf': 'MissFortune',
    'j4': 'JarvanIV', 'jarvan': 'JarvanIV', 'xin': 'XinZhao', 'kogmaw': 'KogMaw', 'reksai': 'RekSai',
    'leblanc': 'Leblanc', 'lb': 'Leblanc', 'velkoz': 'Velkoz', 'kaisa': 'Kaisa', 'khazix': 'Khazix', 'belveth': 'Belveth',
    'renata': 'Renata', 'yi': 'MasterYi', 'masteryi': 'MasterYi', 'kass': 'Kassadin', 'kat': 'Katarina',
    'malz': 'Malzahar', 'naut': 'Nautilus', 'sej': 'Sejuani', 'trist': 'Tristana', 'ez': 'Ezreal', 'cass': 'Cassiopeia',
}
# Apelidos de item que aparecem nas planilhas (minúsculas -> nome em inglês do Data Dragon).
APELIDO_ITEM = {
    'swifties': 'Boots of Swiftness', 'swiftness boots': 'Boots of Swiftness', 'berserkers': "Berserker's Greaves",
    "berserker's swifties": "Berserker's Greaves", 'tabis': 'Plated Steelcaps', 'steelcaps': 'Plated Steelcaps',
    'mercs': "Mercury's Treads", 'mercury treads': "Mercury's Treads", 'mecury\'s treads': "Mercury's Treads",
    'lucidity': 'Ionian Boots of Lucidity', "sorc shoes": "Sorcerer's Shoes", 'sorcs': "Sorcerer's Shoes",
    "dead man's": "Dead Man's Plate", 'deadmans': "Dead Man's Plate", 'dmp': "Dead Man's Plate",
    "jak'sho": "Jak'Sho, The Protean", 'jaksho': "Jak'Sho, The Protean", "sterak's": "Sterak's Gage", 'steraks': "Sterak's Gage",
    "serpant's fang": "Serpent's Fang", 'serpants fang': "Serpent's Fang", "serpant's": "Serpent's Fang", 'serpants': "Serpent's Fang",
    "randuin's": "Randuin's Omen", 'randuins': "Randuin's Omen", 'rookern': 'Kaenic Rookern', 'fon': 'Force of Nature',
    'ldr': "Lord Dominik's Regards", 'refill': 'Refillable Potion', 'refill pot': 'Refillable Potion',
    'negatron': 'Negatron Cloak', 'bork': 'Blade of The Ruined King', 'botrk': 'Blade of The Ruined King',
    'chempunk': 'Chempunk Chainsword', 'exe': "Executioner's Calling", "execution's calling": "Executioner's Calling",
    "exe cutioner's calling": "Executioner's Calling", 'shojin': 'Spear of Shojin', 'cleaver': 'Black Cleaver', 'bc': 'Black Cleaver',
    'hb': 'Hullbreaker', 'qss': 'Quicksilver Sash', 'shieldbow': 'Immortal Shieldbow', 'rocketbelt': 'Hextech Rocketbelt',
    "spirit's visage": 'Spirit Visage', 'visage': 'Spirit Visage', "rylai's": "Rylai's Crystal Scepter", 'rylai': "Rylai's Crystal Scepter",
    "liandry's": "Liandry's Torment", 'liandry': "Liandry's Torment", "zhonya's": "Zhonya's Hourglass", 'zhonya': "Zhonya's Hourglass",
    'zhonyas': "Zhonya's Hourglass", "nashor's": "Nashor's Tooth", 'nashor': "Nashor's Tooth", 'rabadon': "Rabadon's Deathcap",
    'dcap': "Rabadon's Deathcap", 'void': 'Void Staff', 'tri force': 'Trinity Force', 'triforce': 'Trinity Force', 'tf item': 'Trinity Force',
    'dd': "Death's Dance", 'gunblade': 'Hextech Gunblade', 'ga': 'Guardian Angel', 'maw': 'Maw of Malmortius',
    'warmogs': "Warmog's Armor", 'warmog': "Warmog's Armor", 'thornmail': 'Thornmail', 'bramble': 'Bramble Vest',
    'pd': 'Phantom Dancer', 'rfc': 'Rapid Firecannon', 'hydra': 'Ravenous Hydra', 'rav hydra': 'Ravenous Hydra',
    'titanic': 'Titanic Hydra', 'sundered sky': 'Sundered Sky', 'eclipse': 'Eclipse', 'dshield': "Doran's Shield",
    'dorans shield': "Doran's Shield", 'dring': "Doran's Ring", 'dorans ring': "Doran's Ring", 'dblade': "Doran's Blade",
    'dorans blade': "Doran's Blade", 'tiamat': 'Tiamat',
}


def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as r:
        return r.read()


def csv_aba(id_planilha, gid):
    """Uma aba da planilha em linhas (lista de listas). Funciona mesmo com o download em xlsx bloqueado, enquanto
    a planilha estiver aberta para quem tem o link (endpoint gviz do Google). Fórmulas vêm como valor; imagens não."""
    url = f'https://docs.google.com/spreadsheets/d/{id_planilha}/gviz/tq?tqx=out:csv&gid={gid}'
    return list(csv.reader(io.StringIO(baixar(url).decode('utf-8'))))


def limpa(t):
    """Junta as quebras de linha da célula (os autores quebram no meio da frase para caber). Não muda o texto."""
    return re.sub(r'\s+', ' ', t or '').strip()


def dificuldade_10(t):
    """'6', '3-5', '4-6' (de 0 a 10) -> formato do site; overall de 1 a 5 é a nota mais alta / 2.
    No guias.json do guia: "escala": 10."""
    t = limpa(t)
    numeros = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', t)]
    if not numeros:
        return {'overall': None, 'valor': None, 'texto': t}
    alto = max(numeros)
    return {'overall': max(1, min(5, math.ceil(alto / 2))), 'valor': alto, 'texto': f'{t}/10'}


class Ddragon:
    """Campeões (títulos em pt_BR, como os outros guias), itens e runas da versão do Data Dragon do site."""

    def __init__(self):
        self.campeoes = json.loads(baixar(f'{DD}/data/pt_BR/champion.json'))['data']
        self.itens = json.loads(baixar(f'{DD}/data/en_US/item.json'))['data']
        _, self.por_runa = montar_icones(self.itens, json.loads(baixar(f'{DD}/data/en_US/runesReforged.json')))
        # Itens de Summoner's Rift primeiro (o Data Dragon repete itens com id de Arena, 22xxxx, que não servem aqui).
        self.por_item = {}
        for k, v in sorted(self.itens.items(), key=lambda kv: (not kv[1].get('maps', {}).get('11'), len(kv[0]), kv[0])):
            if v.get('gold', {}).get('purchasable'):
                self.por_item.setdefault(chave(v['name']), (v['name'], f'{DD}/img/item/{k}.png'))
        self._ch = {}
        for c in self.campeoes.values():
            self._ch[chave(c['name'])] = c
            self._ch[chave(c['id'])] = c
        for k, v in APELIDO_CAMPEAO.items():
            self._ch.setdefault(k, self.campeoes[v])

    def campeao(self, nome):
        """Campeão pelo nome escrito na planilha; KeyError se não reconhecer (melhor falhar do que errar)."""
        return self._ch[chave(limpa(nome))]

    def item(self, nome):
        """(nome em inglês, ícone) pelo nome escrito na planilha, ou None. Aceita apelido e começo único do nome."""
        base = limpa(nome).strip(' .,')
        k = chave(APELIDO_ITEM.get(base.lower(), base))
        if k in self.por_item:
            return self.por_item[k]
        achados = [v for kk, v in self.por_item.items() if kk.startswith(k) and len(k) >= 5]
        return achados[0] if len(achados) == 1 else None

    def runa(self, nome):
        return self.por_runa.get(chave(nome))

    @staticmethod
    def fragmento(nome):
        return icone_fragmento(nome)

    @staticmethod
    def feitico(arquivo):
        """'SummonerFlash' -> ícone."""
        return f'{DD}/img/spell/{arquivo}.png'


# Feitiços como as planilhas escrevem -> (nome em inglês, arquivo do ícone).
FEITICO = {'ignite': ('Ignite', 'SummonerDot'), 'flash': ('Flash', 'SummonerFlash'), 'fsh': ('Flash', 'SummonerFlash'),
           'ghost': ('Ghost', 'SummonerHaste'), 'exh': ('Exhaust', 'SummonerExhaust'), 'exhaust': ('Exhaust', 'SummonerExhaust'),
           'cleanse': ('Cleanse', 'SummonerBoost'), 'tp': ('Teleport', 'SummonerTeleport'), 'teleport': ('Teleport', 'SummonerTeleport'),
           'barrier': ('Barrier', 'SummonerBarrier'), 'heal': ('Heal', 'SummonerHeal'), 'smite': ('Smite', 'SummonerSmite')}


def gravar_guia(guia, matchups, paginas, fonte):
    """Grava src/guias/<guia>/matchups.json e paginas.json no formato que o build lê."""
    dest = ROOT / 'src/guias' / guia
    dest.mkdir(parents=True, exist_ok=True)
    for nome, valor in [('matchups.json', {'versao': VER, 'fonte': fonte, 'matchups': matchups}), ('paginas.json', paginas)]:
        (dest / nome).write_text(json.dumps(valor, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
