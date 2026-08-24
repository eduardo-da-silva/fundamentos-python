import csv
import json
from pathlib import Path

from ..core.entidades import Cliente, Transacao


def _para_int(valor: str, padrao: int | None = None) -> int | None:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return padrao


def _para_float(valor: str, padrao: float | None = None) -> float | None:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


def carregar_clientes(caminho: str | Path) -> list[Cliente]:
    with Path(caminho).open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        return [
            Cliente(
                id=_para_int(linha.get("id", "")),
                nome=linha.get("nome", "").strip(),
                email=linha.get("email", "").strip(),
                idade=_para_int(linha.get("idade", "")),
                cidade=linha.get("cidade", "").strip(),
                data_cadastro=linha.get("data_cadastro", "").strip(),
            )
            for linha in leitor
        ]


def carregar_transacoes(caminho: str | Path) -> list[Transacao]:
    with Path(caminho).open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        return [
            Transacao(
                id=_para_int(linha.get("id", "")),
                cliente_id=_para_int(linha.get("cliente_id", "")),
                valor=_para_float(linha.get("valor", "")),
                categoria=linha.get("categoria", "").strip(),
                data=linha.get("data", "").strip(),
                status=linha.get("status", "").strip(),
            )
            for linha in leitor
        ]


def carregar_config(caminho: str | Path) -> dict:
    with Path(caminho).open(encoding="utf-8") as arquivo:
        return json.load(arquivo)
