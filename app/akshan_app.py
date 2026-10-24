"""Akshan Matchups: app de bandeja para a seleção de campeões.

Lê a sessão da seleção de campeões pela API local do cliente do LoL (LCU) e,
quando o jogador está de Akshan, abre o site direto na matchup contra o mid
inimigo mais provável. Só faz leitura: nunca escolhe, bane nem aceita nada.
"""

import ctypes
import json
import logging
import os
import re
import sys
import threading
import time
import unicodedata
import webbrowser
from ctypes import wintypes

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NOME_APP = "Akshan Matchups"
SITE = "https://akshan-matchups.vercel.app/"
AKSHAN = 166
INTERVALO_POLL = 1.5        # segundos entre leituras na seleção
INTERVALO_SEM_CLIENTE = 4   # segundos entre tentativas de achar o cliente
INTERVALO_MIN_ABRIR = 5     # segundos mínimos entre duas aberturas do navegador

URL_DADOS = "https://raw.githubusercontent.com/Luis1982Yt/akshan-matchups/main/src/guias/akshan/"
URL_VERSOES = "https://ddragon.leagueoflegends.com/api/versions.json"
URL_CAMPEOES = "https://ddragon.leagueoflegends.com/cdn/{v}/data/pt_BR/champion.json"
VERSAO_DDRAGON = "16.20.1"
URL_TAXAS = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"

PASTA_LOL = r"C:\Riot Games\League of Legends"
CHAVE_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"

PASTA_CONFIG = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AkshanMatchups")
log = logging.getLogger("akshan")


# ---------- Textos (português; inglês se o Windows estiver em inglês) ----------

TXT = {
    "pt": {
        "sem_cliente": "Aguardando o cliente do LoL",
        "fora": "Fora da seleção de campeões",
        "outro": "Na seleção (sem Akshan)",
        "akshan": "Na seleção de Akshan",
        "alvo": "Matchup aberta: {c}",
        "abrir_site": "Abrir o site",
        "inimigos": "Inimigos agora",
        "nenhum": "Nenhum inimigo escolhido ainda",
        "sem_guia": "{c} (sem guia)",
        "iniciar": "Iniciar com o Windows",
        "sair": "Sair",
    },
    "en": {
        "sem_cliente": "Waiting for the LoL client",
        "fora": "Not in champion select",
        "outro": "In champ select (not Akshan)",
        "akshan": "In champ select as Akshan",
        "alvo": "Matchup open: {c}",
        "abrir_site": "Open the site",
        "inimigos": "Current enemies",
        "nenhum": "No enemy picked yet",
        "sem_guia": "{c} (no guide)",
        "iniciar": "Start with Windows",
        "sair": "Quit",
    },
}


def lingua():
    try:
        return "en" if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x09 else "pt"
    except Exception:
        return "pt"


# ---------- Slug: a mesma regra da função slug() do src/template.html ----------

def slug(nome):
    s = unicodedata.normalize("NFD", nome.lower())
    s = re.sub("[\u0300-\u036f]", "", s)
    s = re.sub("['\u2019.]", "", s)
    return re.sub(r"\s+", "-", s)


def url_matchup(s):
    return f"{SITE}#akshan/{s}"


# ---------- Dados: guia, Data Dragon e taxa de mid ----------

def pasta_recursos():
    """Pasta com as cópias embutidas (no .exe) ou o src/ do repositório."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "dados")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "guias", "akshan")


def le_rows(texto):
    # rows.js é um array JS com vírgula sobrando no fim.
    return json.loads(re.sub(r",\s*\]\s*$", "]", texto.strip()))


def monta_guia(rows, meta):
    """Lista na ordem do guia: [(nome, id do Data Dragon), ...]."""
    champs = meta.get("champs", {})
    return [(r[0], champs.get(r[0], {}).get("id", r[0].replace("'", "").replace(" ", ""))) for r in rows]


def carrega_guia():
    try:
        rows = le_rows(requests.get(URL_DADOS + "rows.js", timeout=10).text)
        meta = requests.get(URL_DADOS + "meta.json", timeout=10).json()
        guia = monta_guia(rows, meta)
        if guia:
            return guia
    except Exception as e:
        log.warning("guia online falhou: %s", e)
    return carrega_guia_local()


def carrega_guia_local():
    p = pasta_recursos()
    with open(os.path.join(p, "rows.js"), encoding="utf-8") as f:
        rows = le_rows(f.read())
    with open(os.path.join(p, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    return monta_guia(rows, meta)


def carrega_ids():
    """{championId numérico: id do Data Dragon}."""
    try:
        v = requests.get(URL_VERSOES, timeout=10).json()[0]
    except Exception:
        v = VERSAO_DDRAGON
    dados = requests.get(URL_CAMPEOES.format(v=v), timeout=15).json()["data"]
    return {int(c["key"]): c["id"] for c in dados.values()}


def carrega_taxas():
    """{championId: fração das partidas do campeão que são no mid}."""
    dados = requests.get(URL_TAXAS, timeout=15).json()["data"]
    taxas = {}
    for k, rotas in dados.items():
        total = sum(r.get("playRate", 0) for r in rotas.values())
        if total > 0:
            taxas[int(k)] = rotas.get("MIDDLE", {}).get("playRate", 0) / total
    return taxas


def com_cache(nome, carregar):
    """Busca na internet; se falhar, usa a última cópia salva."""
    caminho = os.path.join(PASTA_CONFIG, f"cache-{nome}.json")
    try:
        dados = carregar()
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados if not isinstance(dados, dict) else {str(k): v for k, v in dados.items()}, f, ensure_ascii=False)
        except OSError:
            pass
        return dados
    except Exception as e:
        log.warning("%s falhou (%s); usando cache", nome, e)
        try:
            with open(caminho, encoding="utf-8") as f:
                d = json.load(f)
            return {int(k): v for k, v in d.items()} if isinstance(d, dict) else [tuple(x) for x in d]
        except Exception:
            return None


class Dados:
    def __init__(self, guia, ids, taxas):
        self.guia = guia or []
        self.ids = ids or {}
        self.taxas = taxas or {}
        self.ordem = {did: i for i, (_, did) in enumerate(self.guia)}
        self.nome_guia = {did: nome for nome, did in self.guia}

    def inimigo(self, cid):
        did = self.ids.get(cid)
        nome = self.nome_guia.get(did)
        return {
            "cid": cid,
            "nome": nome or did or f"#{cid}",
            "slug": slug(nome) if nome else None,
            "prob": self.taxas.get(cid),
            "ordem": self.ordem.get(did, 999),
        }


# ---------- Leitura da sessão e escolha do mid ----------

def le_sessao(sessao, dados):
    """Devolve (eh_akshan, inimigos). inimigos: dicts de Dados.inimigo()."""
    eu_cell = sessao.get("localPlayerCellId")
    eu = next((p for p in sessao.get("myTeam", []) if p.get("cellId") == eu_cell), None)
    eh_akshan = bool(eu) and AKSHAN in (eu.get("championId"), eu.get("championPickIntent"))
    vistos, inimigos = set(), []
    for p in sessao.get("theirTeam", []):
        cid = p.get("championId") or 0
        if cid > 0 and cid not in vistos:
            vistos.add(cid)
            inimigos.append(dados.inimigo(cid))
    return eh_akshan, inimigos


def chave_mid(i):
    # Maior chance de mid primeiro; sem taxa, vale a ordem do guia.
    return (i["prob"] if i["prob"] is not None else -1, -i["ordem"])


def escolhe_mid(inimigos, atual=None):
    """Slug do inimigo no guia com mais cara de mid. Fica no atual se ninguém o superar."""
    no_guia = [i for i in inimigos if i["slug"]]
    if not no_guia:
        return None
    melhor = max(no_guia, key=chave_mid)
    ainda = next((i for i in no_guia if i["slug"] == atual), None)
    if ainda and chave_mid(melhor) <= chave_mid(ainda):
        return atual
    return melhor["slug"]


# ---------- LCU (API local do cliente) ----------

def _exe_processos(nome):
    """Caminhos dos executáveis abertos com esse nome (sem psutil)."""
    k32 = ctypes.windll.kernel32

    class PE(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD),
                    ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD),
                    ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]

    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.Process32FirstW.argtypes = k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PE)]
    k32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    caminhos = []
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    if not snap or snap == wintypes.HANDLE(-1).value:
        return caminhos
    try:
        pe = PE()
        pe.dwSize = ctypes.sizeof(PE)
        ok = k32.Process32FirstW(snap, ctypes.byref(pe))
        while ok:
            if pe.szExeFile.lower() == nome.lower():
                h = k32.OpenProcess(0x1000, False, pe.th32ProcessID)
                if h:
                    buf = ctypes.create_unicode_buffer(1024)
                    n = wintypes.DWORD(1024)
                    if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
                        caminhos.append(buf.value)
                    k32.CloseHandle(h)
            ok = k32.Process32NextW(snap, ctypes.byref(pe))
    finally:
        k32.CloseHandle(snap)
    return caminhos


class Lcu:
    def __init__(self):
        self.pasta = None
        self.porta = self.senha = None
        self.http = requests.Session()
        self.http.verify = False  # certificado próprio da Riot

    def _pastas(self):
        if self.pasta:
            yield self.pasta
        yield PASTA_LOL
        try:
            for exe in _exe_processos("LeagueClientUx.exe"):
                yield os.path.dirname(exe)
        except Exception as e:
            log.debug("processos: %s", e)

    def conecta(self):
        for pasta in self._pastas():
            try:
                with open(os.path.join(pasta, "lockfile"), encoding="utf-8") as f:
                    partes = f.read().strip().split(":")
                self.pasta, self.porta, self.senha = pasta, partes[2], partes[3]
                self.http.auth = ("riot", self.senha)
                return True
            except (OSError, IndexError):
                continue
        self.porta = None
        return False

    def sessao(self):
        """(status, json): status 'sem_cliente', 'fora' ou 'ok'. Só GET."""
        if not self.porta and not self.conecta():
            return "sem_cliente", None
        try:
            r = self.http.get(f"https://127.0.0.1:{self.porta}/lol-champ-select/v1/session", timeout=3)
        except requests.RequestException:
            self.porta = None  # cliente fechou ou trocou de porta
            return "sem_cliente", None
        if r.status_code == 200:
            return "ok", r.json()
        if r.status_code in (401, 403):
            self.porta = None
            return "sem_cliente", None
        return "fora", None


# ---------- Monitor: decide quando abrir o navegador ----------

class Monitor:
    def __init__(self, dados, busca_sessao, abre=webbrowser.open, agora=time.monotonic, ao_mudar=None):
        self.dados = dados
        self.busca_sessao = busca_sessao
        self.abre = abre
        self.agora = agora
        self.ao_mudar = ao_mudar or (lambda: None)
        self.estado = "sem_cliente"
        self.inimigos = []
        self.alvo = None
        self.ultimo_abrir = None

    def passo(self):
        status, sessao = self.busca_sessao()
        antes = (self.estado, [i["cid"] for i in self.inimigos], self.alvo)
        if status != "ok":
            self.estado, self.inimigos, self.alvo = status, [], None
        else:
            eh_akshan, self.inimigos = le_sessao(sessao, self.dados)
            if not eh_akshan:
                self.estado, self.alvo = "outro", None
            else:
                self.estado = "akshan"
                novo = escolhe_mid(self.inimigos, self.alvo)
                if novo and novo != self.alvo and self._pode_abrir():
                    log.info("abrindo matchup: %s", novo)
                    self.abre(url_matchup(novo))
                    self.alvo, self.ultimo_abrir = novo, self.agora()
        if antes != (self.estado, [i["cid"] for i in self.inimigos], self.alvo):
            self.ao_mudar()

    def _pode_abrir(self):
        return self.ultimo_abrir is None or self.agora() - self.ultimo_abrir >= INTERVALO_MIN_ABRIR

    def abre_manual(self, s):
        self.abre(url_matchup(s))
        self.alvo, self.ultimo_abrir = s, self.agora()
        self.ao_mudar()


# ---------- Iniciar com o Windows (HKCU\...\Run, só no .exe) ----------

def config():
    try:
        with open(os.path.join(PASTA_CONFIG, "config.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def salva_config(c):
    with open(os.path.join(PASTA_CONFIG, "config.json"), "w", encoding="utf-8") as f:
        json.dump(c, f)


def inicia_com_windows(ligar):
    if not getattr(sys, "frozen", False):
        return  # rodando como script: não mexe no registro
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_RUN, 0, winreg.KEY_SET_VALUE) as k:
        if ligar:
            winreg.SetValueEx(k, NOME_APP, 0, winreg.REG_SZ, f'"{sys.executable}"')
        else:
            try:
                winreg.DeleteValue(k, NOME_APP)
            except FileNotFoundError:
                pass


# ---------- Bandeja ----------

def uma_instancia():
    ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\AkshanMatchupsApp")
    return ctypes.windll.kernel32.GetLastError() != 183  # ERROR_ALREADY_EXISTS


def main():
    os.makedirs(PASTA_CONFIG, exist_ok=True)
    logging.basicConfig(filename=os.path.join(PASTA_CONFIG, "log.txt"), filemode="w", encoding="utf-8", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    import pystray
    from PIL import Image

    if "--testar" in sys.argv:
        # Confere o .exe sem bandeja e sem mexer no registro: lê dados e uma sessão e anota no log.
        d = Dados(carrega_guia(), carrega_ids(), carrega_taxas())
        log.info("teste: %d no guia, %d campeões, %d taxas, sessão: %s, ícone: %s", len(d.guia), len(d.ids),
                 len(d.taxas), Lcu().sessao()[0], os.path.exists(os.path.join(pasta_recursos(), "icone-64.png")))
        return
    if not uma_instancia():
        return

    T = TXT[lingua()]
    cfg = config()
    if "iniciar" not in cfg:
        cfg["iniciar"] = True  # ligado por padrão
        salva_config(cfg)
    try:
        inicia_com_windows(cfg["iniciar"])
    except OSError as e:
        log.warning("registro: %s", e)

    lcu = Lcu()
    dados = Dados([], {}, {})
    icone = None
    monitor = Monitor(dados, lcu.sessao, ao_mudar=lambda: icone and icone.update_menu())

    def carrega():
        guia = com_cache("guia", carrega_guia)
        ids = com_cache("ids", carrega_ids)
        taxas = com_cache("taxas", carrega_taxas)
        monitor.dados = Dados(guia, ids, taxas)
        log.info("dados: %d no guia, %d campeões, %d taxas", len(monitor.dados.guia), len(monitor.dados.ids), len(monitor.dados.taxas))

    def laco():
        carrega()
        while not parar.is_set():
            try:
                monitor.passo()
            except Exception:
                log.exception("erro no passo")
            parar.wait(INTERVALO_SEM_CLIENTE if monitor.estado == "sem_cliente" else INTERVALO_POLL)

    def texto_estado(_):
        return T[monitor.estado]

    def texto_alvo(_):
        nome = next((n for n, _ in monitor.dados.guia if slug(n) == monitor.alvo), monitor.alvo)
        return T["alvo"].format(c=nome)

    def itens_inimigos():
        if not monitor.inimigos:
            yield pystray.MenuItem(T["nenhum"], None, enabled=False)
        for i in monitor.inimigos:
            if i["slug"]:
                yield pystray.MenuItem(i["nome"], (lambda s: lambda: monitor.abre_manual(s))(i["slug"]),
                                       checked=(lambda s: lambda _: monitor.alvo == s)(i["slug"]), radio=True)
            else:
                yield pystray.MenuItem(T["sem_guia"].format(c=i["nome"]), None, enabled=False)

    def alterna_iniciar(_icone, _item):
        cfg["iniciar"] = not cfg["iniciar"]
        salva_config(cfg)
        try:
            inicia_com_windows(cfg["iniciar"])
        except OSError as e:
            log.warning("registro: %s", e)

    def sair(icone_, _item):
        parar.set()
        icone_.stop()

    menu = pystray.Menu(
        pystray.MenuItem(texto_estado, None, enabled=False),
        pystray.MenuItem(texto_alvo, None, enabled=False, visible=lambda _: bool(monitor.alvo)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(T["abrir_site"], lambda: webbrowser.open(url_matchup(monitor.alvo) if monitor.alvo else SITE), default=True),
        pystray.MenuItem(T["inimigos"], pystray.Menu(itens_inimigos)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(T["iniciar"], alterna_iniciar, checked=lambda _: cfg["iniciar"]),
        pystray.MenuItem(T["sair"], sair),
    )
    imagem = Image.open(os.path.join(pasta_recursos(), "icone-64.png")) if getattr(sys, "frozen", False) \
        else Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "icone", "icone-64.png"))
    icone = pystray.Icon("akshan-matchups", imagem, NOME_APP, menu)
    parar = threading.Event()
    threading.Thread(target=laco, daemon=True).start()
    icone.run()


if __name__ == "__main__":
    main()
