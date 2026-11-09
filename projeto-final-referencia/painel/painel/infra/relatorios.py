import json
from abc import ABC, abstractmethod
from pathlib import Path

from painel.core.resultados import ResultadoProcessamento


class GeradorRelatorio(ABC):
    extensao: str

    @abstractmethod
    def render(self, resultado: ResultadoProcessamento) -> str: ...

    def salvar(self, resultado: ResultadoProcessamento, pasta: Path) -> Path:
        pasta.mkdir(parents=True, exist_ok=True)
        destino = pasta / f"relatorio.{self.extensao}"
        destino.write_text(self.render(resultado), encoding="utf-8")
        return destino


class RelatorioTexto(GeradorRelatorio):
    extensao = "txt"

    def render(self, r: ResultadoProcessamento) -> str:
        linhas = [
            "PAINEL DE NOTAS — RESUMO",
            f"Alunos processados: {len(r.alunos)}",
            f"Registros de nota válidos: {r.notas_validas} | inválidos: {r.notas_invalidas}",
            "",
            "Situação dos alunos",
        ]
        for a in r.alunos:
            media = a.media()
            texto = "   —" if media is None else f"{media:.2f}"
            linhas.append(f"  {a.nome:<22} {a.turma}  média {texto}  {a.situacao(r.config)}")
        linhas += ["", "Média por disciplina"]
        linhas += [f"  {d:<12} {m:.2f}" for d, m in r.medias_disciplinas.items()]
        linhas += ["", f"Erros encontrados ({len(r.erros)})"]
        linhas += [f"  {e.arquivo}:{e.linha}  {e.motivo}" for e in r.erros]
        return "\n".join(linhas) + "\n"


class RelatorioJSON(GeradorRelatorio):
    extensao = "json"

    def render(self, r: ResultadoProcessamento) -> str:
        dados = {
            "resumo": {
                "alunos_processados": len(r.alunos),
                "notas_validas": r.notas_validas,
                "notas_invalidas": r.notas_invalidas,
                "situacoes": r.contagem_situacoes(),
            },
            "alunos": [
                {
                    "matricula": a.matricula,
                    "nome": a.nome,
                    "turma": a.turma,
                    "media": None if a.media() is None else round(a.media(), 2),
                    "situacao": a.situacao(r.config),
                }
                for a in r.alunos
            ],
            "disciplinas": [
                {"disciplina": d, "media": round(m, 2)} for d, m in r.medias_disciplinas.items()
            ],
            "erros": [
                {"arquivo": e.arquivo, "linha": e.linha, "tipo": e.tipo, "motivo": e.motivo}
                for e in r.erros
            ],
        }
        return json.dumps(dados, indent=2, ensure_ascii=False) + "\n"


GERADORES = {"texto": RelatorioTexto, "json": RelatorioJSON}
