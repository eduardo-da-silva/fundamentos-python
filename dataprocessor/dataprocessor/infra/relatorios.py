from abc import ABC, abstractmethod
import csv
import io
import json

from ..core.resultados import ResultadoProcessamento


class GeradorRelatorio(ABC):
    @abstractmethod
    def render(self, resultado: ResultadoProcessamento) -> str: ...


class RelatorioTexto(GeradorRelatorio):
    def render(self, resultado: ResultadoProcessamento) -> str:
        return "\n".join(
            [
                "=== DataProcessor CLI ===",
                "",
                "[VALIDAÇÃO]",
                f"Clientes válidos: {len(resultado.clientes)}",
                f"Clientes inválidos: {len(resultado.clientes_invalidos)}",
                f"Transações válidas: {len(resultado.transacoes)}",
                f"Transações inválidas: {len(resultado.transacoes_invalidas)}",
                "",
                "[RELATÓRIO]",
                f"Média de idade: {resultado.media_idade:.1f}",
                f"Total aprovado: R$ {resultado.total_aprovado:.2f}",
            ]
        )


class RelatorioJson(GeradorRelatorio):
    def render(self, resultado: ResultadoProcessamento) -> str:
        return json.dumps(resultado.to_dict(), ensure_ascii=False, indent=2) + "\n"


class RelatorioCsv(GeradorRelatorio):
    def render(self, resultado: ResultadoProcessamento) -> str:
        arquivo = io.StringIO()
        escritor = csv.writer(arquivo, lineterminator="\n")
        escritor.writerow(("id", "nome", "email", "idade", "cidade", "data_cadastro"))
        for cliente in resultado.clientes:
            escritor.writerow(
                (cliente.id, cliente.nome, cliente.email, cliente.idade, cliente.cidade, cliente.data_cadastro)
            )
        return arquivo.getvalue()


def criar_gerador(formato: str) -> GeradorRelatorio:
    geradores = {
        "texto": RelatorioTexto,
        "json": RelatorioJson,
        "csv": RelatorioCsv,
    }
    return geradores[formato]()
