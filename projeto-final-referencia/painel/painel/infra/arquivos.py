import csv
import json
from pathlib import Path

from painel.core.entidades import Config


def ler_csv(caminho: Path) -> list[tuple[int, dict]]:
    """Devolve (número da linha no arquivo, registro). O cabeçalho é a linha 1."""
    with open(caminho, newline="", encoding="utf-8") as f:
        return [(n, linha) for n, linha in enumerate(csv.DictReader(f), start=2)]


def ler_config(caminho: Path) -> Config:
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    return Config(
        media_aprovacao=float(dados["media_aprovacao"]),
        media_recuperacao=float(dados["media_recuperacao"]),
        nota_maxima=float(dados["nota_maxima"]),
    )
