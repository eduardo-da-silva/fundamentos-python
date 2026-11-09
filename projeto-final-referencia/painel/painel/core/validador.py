import math
from dataclasses import dataclass

from painel.core.entidades import Aluno, Config, Nota


@dataclass(frozen=True)
class ErroValidacao:
    arquivo: str
    linha: int
    tipo: str
    motivo: str


def _limpar(registro: dict) -> dict[str, str]:
    return {chave: (valor or "").strip() for chave, valor in registro.items()}


def validar_aluno(
    linha: int, registro: dict, vistos: set[str]
) -> Aluno | ErroValidacao:
    dados = _limpar(registro)
    for campo in ("matricula", "nome", "turma"):
        if not dados.get(campo):
            return ErroValidacao("alunos.csv", linha, "campo_vazio", f"campo '{campo}' vazio")
    if not dados["matricula"].isdigit():
        return ErroValidacao(
            "alunos.csv", linha, "matricula_invalida", f"matrícula '{dados['matricula']}' não é numérica"
        )
    if dados["matricula"] in vistos:
        return ErroValidacao(
            "alunos.csv", linha, "matricula_duplicada", f"matrícula {dados['matricula']} já cadastrada"
        )
    return Aluno(dados["matricula"], dados["nome"], dados["turma"])


def validar_nota(
    linha: int,
    registro: dict,
    matriculas: set[str],
    vistas: set[tuple[str, str, str]],
    config: Config,
) -> Nota | ErroValidacao:
    dados = _limpar(registro)
    for campo in ("matricula", "disciplina", "avaliacao", "nota"):
        if not dados.get(campo):
            return ErroValidacao("notas.csv", linha, "campo_vazio", f"campo '{campo}' vazio")

    try:
        valor = float(dados["nota"])
        if not math.isfinite(valor):
            raise ValueError
    except ValueError:
        return ErroValidacao("notas.csv", linha, "nota_invalida", f"nota inválida ({dados['nota']!r})")

    if not 0 <= valor <= config.nota_maxima:
        return ErroValidacao(
            "notas.csv", linha, "nota_fora_do_intervalo", f"nota fora do intervalo ({valor})"
        )
    if dados["matricula"] not in matriculas:
        return ErroValidacao(
            "notas.csv", linha, "matricula_inexistente", f"matrícula inexistente ({dados['matricula']})"
        )
    chave = (dados["matricula"], dados["disciplina"], dados["avaliacao"])
    if chave in vistas:
        return ErroValidacao(
            "notas.csv", linha, "avaliacao_duplicada",
            f"{dados['disciplina']}/{dados['avaliacao']} já lançada para {dados['matricula']}",
        )
    return Nota(dados["matricula"], dados["disciplina"], dados["avaliacao"], valor)
