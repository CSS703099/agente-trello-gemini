import os
import unicodedata
from datetime import date, datetime, time, timezone
from functools import wraps
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")
STATUS = {
    "a fazer": "A fazer",
    "em andamento": "Em andamento",
    "concluido": "Concluído",
}
ALIASES = {"fazendo": "em andamento", "feito": "concluido", "feita": "concluido"}


class ErroDeTarefa(ValueError):
    """Erro seguro para apresentar ao usuário."""


def _normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto)
    return " ".join("".join(c for c in sem_acento if not unicodedata.combining(c))
                    .casefold().split())


def _status(texto):
    normal = _normalizar(texto)
    normal = ALIASES.get(normal, normal)
    if normal not in STATUS:
        raise ErroDeTarefa("Use A fazer, Em andamento ou Concluído.")
    return normal


def _quadro():
    configuracao = [os.getenv(k, "").strip() for k in (
        "TRELLO_API_KEY", "TRELLO_API_TOKEN", "TRELLO_BOARD_ID"
    )]
    if not all(configuracao):
        raise ErroDeTarefa("Configure a chave, o token e o ID do quadro Trello no .env.")
    from trello import TrelloClient

    chave, token, quadro = configuracao
    return TrelloClient(api_key=chave, token=token).get_board(quadro)


def _listas(quadro):
    encontradas = {}
    for lista in quadro.open_lists():
        nome = _normalizar(lista.name)
        if nome in STATUS:
            if nome in encontradas:
                raise ErroDeTarefa("O quadro tem duas listas com o mesmo status.")
            encontradas[nome] = lista
    if set(encontradas) != set(STATUS):
        raise ErroDeTarefa("O quadro precisa ter A fazer, Em andamento e Concluído.")
    return encontradas


def _cartao(card, status):
    return {"id": card.id, "nome": card.name, "status": STATUS[status]}


def _ferramenta(func):
    @wraps(func)
    def executar(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ErroDeTarefa as erro:
            return {"ok": False, "erro": str(erro)}
        except Exception:
            return {
                "ok": False,
                "erro": "O Trello não confirmou a operação. Confira o quadro antes de tentar de novo.",
            }
    return executar


def data_de_hoje() -> dict:
    """Retorna a data local de hoje em ISO no fuso de São Paulo."""
    return {"data": datetime.now(FUSO).date().isoformat(), "fuso": FUSO.key}


@_ferramenta
def criar_tarefa(nome: str, descricao: str, data: str) -> dict:
    """Cria uma tarefa em A fazer com nome, descrição e data de vencimento YYYY-MM-DD."""
    nome, descricao = nome.strip(), descricao.strip()
    if not nome or len(nome) > 150 or not descricao or len(descricao) > 1000:
        raise ErroDeTarefa("Informe nome de até 150 e descrição de até 1.000 caracteres.")
    try:
        local = date.fromisoformat(data)
        if local.isoformat() != data:
            raise ValueError
    except ValueError:
        raise ErroDeTarefa("Informe uma data no formato AAAA-MM-DD.") from None

    vencimento = datetime.combine(local, time(12), FUSO).astimezone(timezone.utc)
    lista = _listas(_quadro())["a fazer"]
    card = lista.add_card(nome, desc=descricao, due=vencimento.isoformat())
    return {"ok": True, "card": _cartao(card, "a fazer"), "data": data}


@_ferramenta
def listar_tarefas(status: str = "todas") -> dict:
    """Lista cards abertos de todos os status ou de um status selecionado."""
    listas = _listas(_quadro())
    if _normalizar(status) not in ("todos", "todas"):
        chave = _status(status)
        listas = {chave: listas[chave]}
    cards = [
        _cartao(card, chave)
        for chave, lista in listas.items()
        for card in lista.list_cards()
    ]
    return {"ok": True, "cards": cards}


@_ferramenta
def mover_tarefa(card_id: str, destino: str) -> dict:
    """Move um card pelo ID retornado na listagem para um status do mesmo quadro."""
    alvo = _status(destino)
    listas = _listas(_quadro())
    for origem, lista in listas.items():
        for card in lista.list_cards():
            if card.id == card_id.strip():
                if alvo != origem:
                    card.change_list(listas[alvo].id)
                return {"ok": True, "card": _cartao(card, alvo)}
    raise ErroDeTarefa("Esse ID não foi encontrado entre os cards abertos do quadro configurado.")
