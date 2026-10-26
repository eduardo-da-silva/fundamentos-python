# Aula 22 — Schemas Pydantic: validação de entrada e saída

## Objetivo

Nesta aula você vai:

- Entender o que o Pydantic faz e por que ele não substitui o `core`
- Descrever o formato das respostas com `response_model`
- Restringir parâmetros a valores válidos com `Literal`
- Receber dados no corpo de uma requisição `POST` e processá-los sem arquivos
- Separar **validação de formato** (Pydantic) de **validação de negócio** (`core`)

## 1. Dois tipos de validação

Até aqui o projeto validou dados em um único lugar: `core/validador.py`, que decide se
um e-mail é válido, se a idade é positiva, se a categoria existe na configuração. Isso
é **validação de negócio** e continua lá.

Uma API acrescenta uma pergunta anterior: o que chegou tem *forma* de cliente? O campo
`idade` é um número ou um texto? Faltou algum campo obrigatório? Isso é **validação de
formato**, e o Pydantic resolve.

| Pergunta                                   | Quem responde         |
| ------------------------------------------ | --------------------- |
| `idade` veio como número?                  | Pydantic (porta)      |
| `idade` é maior que zero?                  | `core/validador.py`   |
| `categoria` existe em `config.json`?       | `core/validador.py`   |
| O corpo é uma lista de objetos?            | Pydantic (porta)      |

!!! warning "Não copie regra de negócio para o schema"

    Se você escrever `Field(gt=0)` na idade, a mesma regra passa a existir em dois
    lugares. O schema descreve a **forma**; a regra continua com um único dono.

## 2. Schemas de saída

Crie `dataprocessor/interfaces/schemas.py`:

```python
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
```

`from_attributes=True` permite que o Pydantic leia os campos de **qualquer objeto**,
inclusive as `dataclass` do `core` — por isso as rotas podem devolver `Cliente`
diretamente, sem `asdict`.

!!! note "Por que não usar a `dataclass` como schema?"

    As entidades do `core` não podem depender de FastAPI nem de Pydantic (isso quebraria
    a regra do núcleo da Aula 08). O schema é a representação **da porta**; a entidade é
    a representação **do núcleo**. Elas se parecem, mas evoluem por motivos diferentes.

## 3. Declarando o `response_model`

```python
from .schemas import ClienteSchema, MetricasSchema, TransacaoSchema


@app.get("/clientes", response_model=list[ClienteSchema])
def listar_clientes():
    return carregar_resultado().clientes
```

Agora a rota devolve a tupla de `Cliente` e o FastAPI converte, valida e documenta a
resposta com base no schema. Na página `/docs`, o exemplo de resposta já mostra os campos
e tipos. Aplique o mesmo em `/transacoes` (`list[TransacaoSchema]`).

Para `/metricas`, monte o schema a partir do resultado:

```python
def resumir(resultado) -> MetricasSchema:
    return MetricasSchema(
        clientes_validos=len(resultado.clientes),
        clientes_invalidos=len(resultado.clientes_invalidos),
        transacoes_validas=len(resultado.transacoes),
        transacoes_invalidas=len(resultado.transacoes_invalidas),
        media_idade=resultado.media_idade,
        total_aprovado=resultado.total_aprovado,
    )


@app.get("/metricas", response_model=MetricasSchema)
def metricas():
    return resumir(carregar_resultado())
```

## 4. Restringindo valores com `Literal`

O problema deixado pela Aula 21 (`/relatorio/xml` devolvendo 500) tem solução na própria
anotação de tipo:

```python
from typing import Literal


@app.get("/relatorio/{formato}")
def relatorio_formatado(formato: Literal["texto", "json", "csv"]):
    ...
```

Faça o mesmo com o status das transações:

```python
@app.get("/transacoes", response_model=list[TransacaoSchema])
def listar_transacoes(
    status: Literal["aprovado", "pendente", "recusado"] | None = None,
    categoria: str | None = None,
    cliente_id: int | None = None,
):
    ...
```

```bash
curl -i http://127.0.0.1:8000/relatorio/xml
curl -i "http://127.0.0.1:8000/transacoes?status=xyz"
```

Ambos agora devolvem **`422 Unprocessable Entity`**, com um corpo JSON que diz qual
parâmetro falhou e quais valores eram aceitos. O código de status certo (erro de quem
pediu) e uma mensagem útil, sem nenhum `if`.

## 5. Recebendo dados: `POST /processar`

Até agora a API só *lê* arquivos do servidor. Vamos permitir que quem chama envie os
dados no corpo da requisição. Primeiro, os schemas de entrada:

```python
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
```

E a rota. Repare que ela usa `FonteDadosMemoria`, criada na Aula 14 justamente para
este tipo de situação:

```python
from ..core.entidades import Cliente, Transacao
from ..infra.fontes import FonteDadosMemoria
from .schemas import ProcessamentoEntrada


@app.post("/processar", response_model=MetricasSchema)
def processar(entrada: ProcessamentoEntrada):
    fonte = FonteDadosMemoria(
        clientes=[Cliente(**c.model_dump()) for c in entrada.clientes],
        transacoes=[Transacao(**t.model_dump()) for t in entrada.transacoes],
        config=entrada.config.model_dump(),
    )
    return resumir(executar_processamento(fonte))
```

`executar_processamento` não percebeu a mudança: antes lia CSVs, agora recebe objetos
da memória. É a promessa da arquitetura hexagonal (Aula 20) cumprida pela quarta vez.

### Verificação 1

Pela página `/docs`, abra `POST /processar`, clique em *Try it out* e envie:

```json
{
  "clientes": [
    {"id": 1, "nome": "Ana", "email": "ana@email.com", "idade": 30,
     "cidade": "Joinville", "data_cadastro": "2023-01-10"}
  ],
  "transacoes": [
    {"id": 1, "cliente_id": 1, "valor": 10.5, "categoria": "livros",
     "data": "2023-05-10", "status": "aprovado"}
  ],
  "config": {
    "categorias_validas": ["livros"],
    "status_validos": ["aprovado", "pendente", "recusado"]
  }
}
```

Esperado: `"total_aprovado": 10.5`.

Depois, quebre de dois jeitos diferentes e compare as respostas:

1. Troque `"idade": 30` por `"idade": "trinta"` → **422**, barrado pelo Pydantic.
2. Troque a categoria por `"inexistente"` → **200**, com `"transacoes_invalidas": 1`.
   O formato estava certo; quem rejeitou foi a regra de negócio do `core`.

## Desafio guiado

1. Crie `interfaces/schemas.py` com os três schemas de saída.
2. Aplique `response_model` em `/clientes`, `/transacoes` e `/metricas`.
3. Troque `str` por `Literal[...]` em `formato` e `status`.
4. Crie os schemas de entrada e a rota `POST /processar`.
5. Reproduza as duas falhas da Verificação 1.

## Desafio extra

Acrescente ao `MetricasSchema` uma lista `motivos_invalidos` com os textos de erro de
`resultado.clientes_invalidos`. Atenção: você precisará mexer apenas no schema e em
`resumir()` — o `core` já guarda esses motivos desde a Aula 12.

## Resumo

O Pydantic cuida da *forma* dos dados que cruzam a fronteira da API; o `core` continua
decidindo o que é *válido*. Manter essas duas camadas separadas é o que impede que a
regra de negócio se espalhe pelas rotas. Na Aula 23, o foco passa a ser o que fazer
quando algo dá errado de verdade.
