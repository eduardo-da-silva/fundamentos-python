from pydantic import BaseModel, ConfigDict


class ClienteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    nome: str
    email: str
    idade: int | None
    cidade: str
    data_cadastro: str


class TransacaoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    cliente_id: int | None
    valor: float | None
    categoria: str
    data: str
    status: str


class MetricasSchema(BaseModel):
    clientes_validos: int
    clientes_invalidos: int
    transacoes_validas: int
    transacoes_invalidas: int
    media_idade: float
    total_aprovado: float


class ClienteEntrada(BaseModel):
    id: int
    nome: str
    email: str = ""
    idade: int | None = None
    cidade: str = ""
    data_cadastro: str = ""


class TransacaoEntrada(BaseModel):
    id: int
    cliente_id: int
    valor: float
    categoria: str
    data: str
    status: str


class ConfigEntrada(BaseModel):
    categorias_validas: list[str]
    status_validos: list[str]
    valor_minimo: float = 0


class ProcessamentoEntrada(BaseModel):
    clientes: list[ClienteEntrada]
    transacoes: list[TransacaoEntrada]
    config: ConfigEntrada
