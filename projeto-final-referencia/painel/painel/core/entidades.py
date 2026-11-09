from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    media_aprovacao: float
    media_recuperacao: float
    nota_maxima: float


@dataclass(frozen=True)
class Nota:
    matricula: str
    disciplina: str
    avaliacao: str
    valor: float


@dataclass
class Aluno:
    matricula: str
    nome: str
    turma: str
    notas: list[Nota] = field(default_factory=list)

    def media(self) -> float | None:
        if not self.notas:
            return None
        return sum(n.valor for n in self.notas) / len(self.notas)

    def situacao(self, config: Config) -> str:
        media = self.media()
        if media is None:
            return "sem notas"
        if media >= config.media_aprovacao:
            return "aprovado"
        if media >= config.media_recuperacao:
            return "recuperação"
        return "reprovado"
