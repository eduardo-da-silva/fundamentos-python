from dataclasses import dataclass


@dataclass(frozen=True)
class Cliente:
    id: int | None
    nome: str
    email: str
    idade: int | None
    cidade: str
    data_cadastro: str

    @property
    def identificacao(self) -> str:
        return f"#{self.id} {self.nome}"


@dataclass(frozen=True)
class Transacao:
    id: int | None
    cliente_id: int | None
    valor: float | None
    categoria: str
    data: str
    status: str

    @property
    def esta_aprovada(self) -> bool:
        return self.status == "aprovado"
