import unicodedata
from dataclasses import replace

from .entidades import Cliente, Transacao


def _remover_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(caractere for caractere in nfkd if not unicodedata.combining(caractere))


def normalizar_nome(nome: str) -> str:
    return nome.strip().title() if nome else ""


def normalizar_email(email: str) -> str:
    return email.strip().lower() if email else ""


def normalizar_cidade(cidade: str) -> str:
    return _remover_acentos(cidade.strip()).title() if cidade else ""


def transformar_cliente(cliente: Cliente) -> Cliente:
    return replace(
        cliente,
        nome=normalizar_nome(cliente.nome),
        email=normalizar_email(cliente.email),
        cidade=normalizar_cidade(cliente.cidade),
        data_cadastro=cliente.data_cadastro.strip(),
    )


def transformar_transacao(transacao: Transacao) -> Transacao:
    return replace(
        transacao,
        categoria=transacao.categoria.strip().lower(),
        data=transacao.data.strip(),
        status=transacao.status.strip().lower(),
    )


def transformar_clientes(clientes: list[Cliente]) -> list[Cliente]:
    return [transformar_cliente(cliente) for cliente in clientes]


def transformar_transacoes(transacoes: list[Transacao]) -> list[Transacao]:
    return [transformar_transacao(transacao) for transacao in transacoes]
