from datetime import date
from collections.abc import Callable, Iterable
from typing import Any

from .entidades import Cliente, Transacao
from .resultados import RegistroInvalido


def email_valido(email: str | None) -> bool:
    if not email or not email.strip():
        return False
    partes = email.strip().split("@")
    return len(partes) == 2 and bool(partes[0]) and "." in partes[1]


def idade_valida(idade: int | None) -> bool:
    return idade is not None and 0 < idade < 150


def data_valida(texto_data: str | None) -> bool:
    if not texto_data:
        return False
    try:
        date.fromisoformat(texto_data)
    except ValueError:
        return False
    return True


def validar_cliente(cliente: Cliente) -> list[str]:
    erros = []
    if not cliente.nome.strip():
        erros.append("nome vazio")
    if not email_valido(cliente.email):
        erros.append(f"email inválido: '{cliente.email}'")
    if not idade_valida(cliente.idade):
        erros.append(f"idade inválida: {cliente.idade}")
    if not data_valida(cliente.data_cadastro):
        erros.append(f"data inválida: '{cliente.data_cadastro}'")
    return erros


def validar_transacao(
    transacao: Transacao,
    ids_clientes: set[int | None],
    config: dict[str, Any],
) -> list[str]:
    erros = []
    if transacao.cliente_id not in ids_clientes:
        erros.append(f"cliente_id inexistente: {transacao.cliente_id}")

    valor_minimo = config.get("valor_minimo", 0)
    if transacao.valor is None or transacao.valor <= valor_minimo:
        erros.append(f"valor inválido: {transacao.valor}")
    if transacao.categoria not in config.get("categorias_validas", []):
        erros.append(f"categoria inválida: '{transacao.categoria}'")
    if transacao.status not in config.get("status_validos", []):
        erros.append(f"status inválido: '{transacao.status}'")
    return erros


def separar_registros(
    registros: Iterable[Any],
    funcao_validar: Callable[..., list[str]],
    **kwargs: Any,
) -> tuple[list[Any], list[RegistroInvalido]]:
    validos = []
    invalidos = []
    for registro in registros:
        erros = funcao_validar(registro, **kwargs)
        if erros:
            invalidos.append(RegistroInvalido(registro, tuple(erros)))
        else:
            validos.append(registro)
    return validos, invalidos
