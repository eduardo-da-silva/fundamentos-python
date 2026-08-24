from collections.abc import Iterable

from .entidades import Cliente, Transacao


def media_idade(clientes: Iterable[Cliente]) -> float:
    idades = [cliente.idade for cliente in clientes if cliente.idade is not None and cliente.idade > 0]
    return sum(idades) / len(idades) if idades else 0


def total_aprovado(transacoes: Iterable[Transacao]) -> float:
    return sum(
        transacao.valor
        for transacao in transacoes
        if transacao.esta_aprovada and transacao.valor is not None and transacao.valor > 0
    )
