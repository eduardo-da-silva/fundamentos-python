from dataclasses import dataclass, field

from painel.core.entidades import Aluno, Config
from painel.core.validador import ErroValidacao


@dataclass
class ResultadoProcessamento:
    config: Config
    alunos: list[Aluno]
    medias_disciplinas: dict[str, float]
    erros: list[ErroValidacao] = field(default_factory=list)
    notas_validas: int = 0
    notas_invalidas: int = 0

    def contagem_situacoes(self) -> dict[str, int]:
        contagem: dict[str, int] = {}
        for aluno in self.alunos:
            situacao = aluno.situacao(self.config)
            contagem[situacao] = contagem.get(situacao, 0) + 1
        return contagem
