"""Akshan Matchups: app de bandeja para a seleção de campeões.

Lê a sessão da seleção de campeões pela API local do cliente do LoL (LCU) e,
quando o jogador está de um campeão que tem guia no site (Akshan, Mordekaiser,
Illaoi...), abre o guia dele direto na matchup contra o inimigo mais provável
da mesma rota. Só faz leitura: nunca escolhe, bane nem aceita nada.
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
INTERVALO_POLL = 1.5        # segundos entre leituras na seleção
INTERVALO_SEM_CLIENTE = 4   # segundos entre tentativas de achar o cliente
INTERVALO_MIN_ABRIR = 5     # segundos mínimos entre duas trocas automáticas de matchup
JANELA_LARGURA, JANELA_ALTURA = 460, 900  # janela lateral estreita: o site mostra o formato compacto

URL_GUIAS = SITE + "guias-app.json"  # gerado pelo scripts/build.py: guias, rota e matchups
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
        "outro": "Na seleção (campeão sem guia)",
        "guia": "Na seleção de {c}",
        "alvo": "Matchup aberta: {c}",
        "abrir_site": "Abrir a janela",
        "navegador": "Abrir no navegador",
        "por_cima": "Sempre por cima",
        "inimigos": "Inimigos agora",
        "nenhum": "Nenhum inimigo escolhido ainda",
        "sem_guia": "{c} (sem guia)",
        "iniciar": "Iniciar com o Windows",
        "sair": "Sair",
    },
    "en": {
        "sem_cliente": "Waiting for the LoL client",
        "fora": "Not in champion select",
        "outro": "In champ select (no guide for your pick)",
        "guia": "In champ select as {c}",
        "alvo": "Matchup open: {c}",
        "abrir_site": "Open the window",
        "navegador": "Open in the browser",
        "por_cima": "Always on top",
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


def url_matchup(guia, s):
    return f"{SITE}#{guia}/{s}"


# ---------- Dados: guias do site, Data Dragon e taxa de cada rota ----------

def pasta_recursos():
    """Pasta com as cópias embutidas (no .exe) ou a raiz do repositório."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "dados")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def carrega_guias():
    guias = requests.get(URL_GUIAS, timeout=10).json()["guias"]
    if not guias:
        raise ValueError("lista de guias vazia")
    return guias


def carrega_guias_local():
    with open(os.path.join(pasta_recursos(), "guias-app.json"), encoding="utf-8") as f:
        return json.load(f)["guias"]


def carrega_ids():
    """{championId numérico: id do Data Dragon}."""
    try:
        v = requests.get(URL_VERSOES, timeout=10).json()[0]
    except Exception:
        v = VERSAO_DDRAGON
    dados = requests.get(URL_CAMPEOES.format(v=v), timeout=15).json()["data"]
    return {int(c["key"]): c["id"] for c in dados.values()}


def carrega_taxas():
    """{championId: {rota: fração das partidas do campeão nessa rota}} (TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY)."""
    dados = requests.get(URL_TAXAS, timeout=15).json()["data"]
    taxas = {}
    for k, rotas in dados.items():
        total = sum(r.get("playRate", 0) for r in rotas.values())
        if total > 0:
            taxas[int(k)] = {rota: r.get("playRate", 0) / total for rota, r in rotas.items()}
    return taxas


def com_cache(nome, carregar, chaves_int=True):
    """Busca na internet; se falhar, usa a última cópia salva."""
    caminho = os.path.join(PASTA_CONFIG, f"cache-{nome}.json")
    try:
        dados = carregar()
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump({str(k): v for k, v in dados.items()} if isinstance(dados, dict) else dados, f, ensure_ascii=False)
        except OSError:
            pass
        return dados
    except Exception as e:
        log.warning("%s falhou (%s); usando cache", nome, e)
        try:
            with open(caminho, encoding="utf-8") as f:
                d = json.load(f)
            return {int(k): v for k, v in d.items()} if isinstance(d, dict) and chaves_int else d
        except Exception:
            return None


class Dados:
    def __init__(self, guias, ids, taxas):
        self.guias = guias or []
        self.ids = ids or {}
        self.taxas = taxas or {}
        self.por_chave = {g["chave"]: g for g in self.guias if g.get("chave")}

    def guia_de(self, *cids):
        """Guia do campeão escolhido (ou só marcado), se o site tiver um."""
        return next((self.por_chave[c] for c in cids if c in self.por_chave), None)

    def inimigo(self, cid, guia):
        did = self.ids.get(cid)
        lista = guia["matchups"] if guia else []
        achado = next(((i, m) for i, m in enumerate(lista) if m[1] == did), None)
        rota = (guia or {}).get("rota") or "MIDDLE"
        taxa = self.taxas.get(cid)
        return {
            "cid": cid,
            "nome": achado[1][0] if achado else (did or f"#{cid}"),
            "slug": achado[1][2] if achado else None,
            "prob": taxa.get(rota, 0) if isinstance(taxa, dict) else None,
            "ordem": achado[0] if achado else 999,
        }


# ---------- Leitura da sessão e escolha do inimigo da rota ----------

def le_sessao(sessao, dados):
    """Devolve (guia ou None, inimigos). inimigos: dicts de Dados.inimigo()."""
    eu_cell = sessao.get("localPlayerCellId")
    eu = next((p for p in sessao.get("myTeam", []) if p.get("cellId") == eu_cell), None)
    guia = dados.guia_de(eu.get("championId"), eu.get("championPickIntent")) if eu else None
    vistos, inimigos = set(), []
    for p in sessao.get("theirTeam", []):
        cid = p.get("championId") or 0
        if cid > 0 and cid not in vistos:
            vistos.add(cid)
            inimigos.append(dados.inimigo(cid, guia))
    return guia, inimigos


def chave_rota(i):
    # Maior chance de jogar na rota do guia primeiro; sem taxa, vale a ordem do guia.
    return (i["prob"] if i["prob"] is not None else -1, -i["ordem"])


def escolhe_inimigo(inimigos, atual=None):
    """Slug do inimigo no guia com mais cara de jogar na rota. Fica no atual se ninguém o superar."""
    no_guia = [i for i in inimigos if i["slug"]]
    if not no_guia:
        return None
    melhor = max(no_guia, key=chave_rota)
    ainda = next((i for i in no_guia if i["slug"] == atual), None)
    if ainda and chave_rota(melhor) <= chave_rota(ainda):
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
        self.guia = None  # guia do campeão que o jogador pegou
        self.inimigos = []
        self.alvo = None
        self.ultimo_abrir = None

    def passo(self):
        status, sessao = self.busca_sessao()
        antes = (self.estado, self.id_guia(), [i["cid"] for i in self.inimigos], self.alvo)
        if status != "ok":
            self.estado, self.guia, self.inimigos, self.alvo = status, None, [], None
        else:
            guia, self.inimigos = le_sessao(sessao, self.dados)
            if not guia:
                self.estado, self.guia, self.alvo = "outro", None, None
            else:
                if self.id_guia() != guia["id"]:
                    self.alvo = None  # trocou de campeão: outra lista de matchups
                self.estado, self.guia = "guia", guia
                novo = escolhe_inimigo(self.inimigos, self.alvo)
                if novo and novo != self.alvo and self._pode_abrir():
                    log.info("abrindo matchup: %s/%s", guia["id"], novo)
                    self.abre(url_matchup(guia["id"], novo))
                    self.alvo, self.ultimo_abrir = novo, self.agora()
        if antes != (self.estado, self.id_guia(), [i["cid"] for i in self.inimigos], self.alvo):
            self.ao_mudar()

    def id_guia(self):
        return self.guia["id"] if self.guia else None

    def url_alvo(self):
        return url_matchup(self.guia["id"], self.alvo) if self.guia and self.alvo else None

    def _pode_abrir(self):
        return self.ultimo_abrir is None or self.agora() - self.ultimo_abrir >= INTERVALO_MIN_ABRIR

    def abre_manual(self, s):
        if not self.guia:
            return
        self.abre(url_matchup(self.guia["id"], s))
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


# ---------- Janela própria: o site dentro do app (WebView2 do Windows, via pywebview) ----------

class Janela:
    """Uma janela só, criada escondida; abrir uma matchup troca o endereço dentro dela e traz para a frente.
    Fechar no X esconde (o app continua na bandeja); só "Sair" fecha de verdade.

    Tudo o que mexe na janela vai para a fila da thread dela (BeginInvoke) e o app segue sem esperar.
    As chamadas do pywebview (evaluate_js, show, load_url...) esperam a resposta da janela, e quando
    duas dessas esperas se cruzam o processo inteiro congela; foi o que travava a troca de guia."""

    def __init__(self, cfg, salva):
        self.cfg, self.salva = cfg, salva
        self.w = None
        self.saindo = False

    def cria(self, webview):
        x, y = self.cfg.get("janela_x"), self.cfg.get("janela_y")
        if x is None:
            try:  # primeira vez: encostada na direita da tela principal
                tela = webview.screens[0]
                x, y = max(0, tela.width - JANELA_LARGURA - 24), max(0, (tela.height - JANELA_ALTURA) // 2)
            except Exception:
                x = y = None
        self.w = webview.create_window(
            NOME_APP, SITE, width=self.cfg.get("janela_l", JANELA_LARGURA), height=self.cfg.get("janela_a", JANELA_ALTURA),
            x=x, y=y, min_size=(360, 560), hidden=True, on_top=bool(self.cfg.get("por_cima")), background_color="#0c0b09")
        self.w.events.closing += self._fechando

    def _form(self):
        from webview.platforms.winforms import BrowserView
        return BrowserView.instances.get(self.w.uid) if self.w else None

    def _na_janela(self, fn):
        """Põe fn na fila da thread da janela e volta na hora."""
        from System import Action
        f = self._form()
        if f is None:
            return False

        def seguro():
            try:
                fn(f)
            except Exception:
                log.exception("janela")
        f.BeginInvoke(Action(seguro))
        return True

    def _guarda_tamanho(self, f):
        try:
            if f.WindowState.ToString() == "Normal":
                self.cfg.update(janela_l=f.Width, janela_a=f.Height, janela_x=f.Left, janela_y=f.Top)
                self.salva(self.cfg)
        except Exception:
            pass

    def _fechando(self):
        if self.saindo:
            return True
        self._na_janela(lambda f: (self._guarda_tamanho(f), f.Hide()))
        return False  # cancela o fechamento: só esconde

    def mostra(self, url=None):
        if not self.w:
            return

        def faz(f):
            from System import Uri
            from System.Windows.Forms import FormWindowState
            wv = f.browser.webview
            if url:
                atual = str(wv.Source) if wv.Source is not None else ""
                if atual.startswith(SITE) and wv.CoreWebView2 is not None:
                    # Já está no site: troca só o #, sem recarregar (o site escuta a mudança).
                    alvo = url.split("#", 1)[1] if "#" in url else ""
                    wv.CoreWebView2.ExecuteScriptAsync(f"location.hash = {json.dumps('#' + alvo)}")
                elif wv.CoreWebView2 is not None:
                    wv.Source = Uri(url)
                else:
                    self.w.real_url = url  # o WebView2 ainda está iniciando: abre direto nesse endereço
            f.Show()
            if f.WindowState == FormWindowState.Minimized:
                f.WindowState = FormWindowState.Normal
            f.Activate()
            if not self.cfg.get("por_cima"):
                # Traz para a frente sem deixar fixo por cima.
                f.TopMost = True
                f.TopMost = False
        self._na_janela(faz)

    def por_cima(self, ligar):
        self._na_janela(lambda f: setattr(f, "TopMost", bool(ligar)))

    def fecha(self):
        self.saindo = True
        if self.w:
            def faz(f):
                self._guarda_tamanho(f)
                f.Close()
            if not self._na_janela(faz):
                self.w.destroy()


# ---------- Bandeja ----------

def uma_instancia():
    ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\AkshanMatchupsApp")
    return ctypes.windll.kernel32.GetLastError() != 183  # ERROR_ALREADY_EXISTS


def main():
    os.makedirs(PASTA_CONFIG, exist_ok=True)
    logging.basicConfig(filename=os.path.join(PASTA_CONFIG, "log.txt"), filemode="w", encoding="utf-8", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    import pystray
    import webview
    from PIL import Image

    if "--testar" in sys.argv:
        # Confere o .exe sem bandeja e sem mexer no registro: lê dados e uma sessão e anota no log.
        d = Dados(carrega_guias(), carrega_ids(), carrega_taxas())
        log.info("teste: guias %s, %d campeões, %d taxas, sessão: %s, ícone: %s", [g["id"] for g in d.guias], len(d.ids),
                 len(d.taxas), Lcu().sessao()[0], os.path.exists(os.path.join(pasta_recursos(), "icone-64.png")))
        return
    if "--testar-janela" in sys.argv:
        # Confere a janela própria no .exe: abre numa matchup, troca de guia duas vezes e fecha sozinho (sem bandeja nem registro).
        jt = Janela({}, lambda c: None)

        def endereco():
            ok = threading.Event()
            lido = []
            jt._na_janela(lambda f: (lido.append(str(f.browser.webview.Source)), ok.set()))
            ok.wait(5)
            return lido[0] if lido else "(sem resposta)"

        def roteiro():
            try:
                log.info("teste janela: começou")
                time.sleep(4)
                for g, s_ in (("akshan", "ahri"), ("illaoi", "darius"), ("mordekaiser", "aatrox"), ("akshan", "zoe")):
                    jt.mostra(url_matchup(g, s_))
                    time.sleep(4)
                    log.info("teste janela: %s/%s -> %s", g, s_, endereco())
            except Exception:
                log.exception("teste janela falhou")
            finally:
                jt.fecha()
        jt.cria(webview)
        webview.start(lambda: threading.Thread(target=roteiro, daemon=True).start(), private_mode=False,
                      storage_path=os.path.join(PASTA_CONFIG, "janela-teste"), gui="edgechromium")
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
    janela = Janela(cfg, salva_config)
    monitor = Monitor(dados, lcu.sessao, abre=janela.mostra, ao_mudar=lambda: icone and icone.update_menu())

    def carrega():
        guias = com_cache("guias", carrega_guias, chaves_int=False) or carrega_guias_local()
        ids = com_cache("ids", carrega_ids)
        taxas = com_cache("taxas-rotas", carrega_taxas)
        monitor.dados = Dados(guias, ids, taxas)
        log.info("dados: guias %s, %d campeões, %d taxas", [g["id"] for g in monitor.dados.guias], len(monitor.dados.ids), len(monitor.dados.taxas))

    def laco():
        carrega()
        while not parar.is_set():
            try:
                monitor.passo()
            except Exception:
                log.exception("erro no passo")
            parar.wait(INTERVALO_SEM_CLIENTE if monitor.estado == "sem_cliente" else INTERVALO_POLL)

    def texto_estado(_):
        return T[monitor.estado].format(c=monitor.guia["campeao"] if monitor.guia else "")

    def texto_alvo(_):
        lista = monitor.guia["matchups"] if monitor.guia else []
        nome = next((m[0] for m in lista if m[2] == monitor.alvo), monitor.alvo)
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

    def alterna_por_cima(_icone, _item):
        cfg["por_cima"] = not cfg.get("por_cima")
        salva_config(cfg)
        janela.por_cima(cfg["por_cima"])

    def sair(icone_, _item):
        parar.set()
        icone_.stop()
        janela.fecha()

    menu = pystray.Menu(
        pystray.MenuItem(texto_estado, None, enabled=False),
        pystray.MenuItem(texto_alvo, None, enabled=False, visible=lambda _: bool(monitor.alvo)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(T["abrir_site"], lambda: janela.mostra(monitor.url_alvo()), default=True),
        pystray.MenuItem(T["inimigos"], pystray.Menu(itens_inimigos)),
        pystray.MenuItem(T["navegador"], lambda: webbrowser.open(monitor.url_alvo() or SITE)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(T["por_cima"], alterna_por_cima, checked=lambda _: bool(cfg.get("por_cima"))),
        pystray.MenuItem(T["iniciar"], alterna_iniciar, checked=lambda _: cfg["iniciar"]),
        pystray.MenuItem(T["sair"], sair),
    )
    imagem = Image.open(os.path.join(pasta_recursos(), "icone-64.png")) if getattr(sys, "frozen", False) \
        else Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "icone", "icone-64.png"))
    icone = pystray.Icon("akshan-matchups", imagem, NOME_APP, menu)
    parar = threading.Event()
    threading.Thread(target=icone.run, daemon=True).start()
    # Guarda skin, tema, língua etc. do site entre uma abertura e outra (o padrão do pywebview é modo anônimo).
    janela.cria(webview)
    webview.start(lambda: threading.Thread(target=laco, daemon=True).start(), private_mode=False,
                  storage_path=os.path.join(PASTA_CONFIG, "janela"), gui="edgechromium")


if __name__ == "__main__":
    main()
