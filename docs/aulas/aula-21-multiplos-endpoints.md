# Aula 21 — Múltiplos endpoints, parâmetros de rota e de consulta

## Objetivo

Nesta aula você vai:

- Transformar o endpoint único da Aula 19 em uma API com vários recursos
- Usar **parâmetros de consulta** (`?status=aprovado`) para filtrar listas
- Usar **parâmetros de rota** (`/relatorio/{formato}`) para escolher uma variação
- Devolver um corpo que não é JSON (texto e CSV) com o `Content-Type` correto
- Ver a documentação interativa que o FastAPI gera sozinho

!!! note "Daqui em diante, a API é o assunto"

    Os Módulos 5 a 7 construíram o `core`, os `services` e as portas de entrada. A
    partir desta aula, o foco muda: `interfaces/api.py` passa a ser o objeto de estudo
    — e o resto do projeto continua **intocado**.

## 1. Ponto de partida

Confirme que você está com o ambiente da Aula 19 ativo e que o endpoint antigo ainda
responde:

```bash
cd dataprocessor
source .venv/bin/activate
uvicorn dataprocessor.interfaces.api:app --reload
```

Abra `http://127.0.0.1:8000/docs`. O FastAPI gera, a partir do seu código, uma página
Swagger onde cada rota pode ser testada com um clique. Você vai usá-la a aula inteira.

## 2. Evitando repetir o carregamento

Cada endpoint novo precisa de um `ResultadoProcessamento`. Em vez de copiar as três
linhas da Aula 19 em todas as rotas, extraia uma função:

```python
from dataclasses import asdict

from fastapi import FastAPI

from ..infra.fontes import fonte_a_partir_de_caminhos
from ..services.processamento import executar_processamento

app = FastAPI(title="DataProcessor API")


def carregar_resultado():
    fonte = fonte_a_partir_de_caminhos(
        "data/clientes.csv",
        "data/transacoes.csv",
        "data/config.json",
    )
    return executar_processamento(fonte)
```

Esta versão ainda tem caminhos fixos no código. A Aula 23 resolve isso de um jeito
melhor — por enquanto, o objetivo é só não duplicar.

## 3. Um recurso por rota

Em REST, a URL nomeia um **recurso** (um substantivo no plural) e o verbo HTTP diz o
que fazer com ele. Para leitura, o verbo é sempre `GET`:

```python
@app.get("/clientes")
def listar_clientes():
    resultado = carregar_resultado()
    return [asdict(cliente) for cliente in resultado.clientes]


@app.get("/metricas")
def metricas():
    resultado = carregar_resultado()
    return {
        "media_idade": resultado.media_idade,
        "total_aprovado": resultado.total_aprovado,
    }
```

`asdict` vem da biblioteca padrão e funciona com qualquer `dataclass` — as entidades
das Aulas 11 e 12 já eram compatíveis com isso.

### Verificação 1

```bash
curl http://127.0.0.1:8000/clientes
curl http://127.0.0.1:8000/metricas
```

`/clientes` deve listar só os **clientes válidos** (2 no dataset padrão) e `/metricas`
deve mostrar `"total_aprovado": 150.5`.

## 4. Parâmetros de consulta: filtrando transações

Tudo que vem depois do `?` na URL é *query string*. No FastAPI, um parâmetro da função
que **não** aparece no caminho da rota vira automaticamente um parâmetro de consulta:

```python
@app.get("/transacoes")
def listar_transacoes(status: str | None = None, categoria: str | None = None):
    transacoes = carregar_resultado().transacoes
    if status is not None:
        transacoes = [t for t in transacoes if t.status == status]
    if categoria is not None:
        transacoes = [t for t in transacoes if t.categoria == categoria]
    return [asdict(t) for t in transacoes]
```

O valor padrão `None` torna o parâmetro **opcional**. Os filtros se combinam:

```bash
curl "http://127.0.0.1:8000/transacoes"
curl "http://127.0.0.1:8000/transacoes?status=aprovado"
curl "http://127.0.0.1:8000/transacoes?status=aprovado&categoria=eletronicos"
```

!!! tip "Olhe a anotação de tipos"

    `status: str | None = None` não é decoração. É assim que o FastAPI sabe o tipo do
    parâmetro e se ele é obrigatório. Os type hints que você escreve desde a Aula 11
    agora têm consequência em tempo de execução.

## 5. Parâmetros de rota: escolhendo o formato

Quando o valor faz parte da identidade do recurso, ele vai no caminho, entre chaves:

```python
from fastapi import Response

from ..infra.relatorios import criar_gerador

MEDIA_TYPES = {"texto": "text/plain", "json": "application/json", "csv": "text/csv"}


@app.get("/relatorio/{formato}")
def relatorio_formatado(formato: str):
    conteudo = criar_gerador(formato).render(carregar_resultado())
    return Response(content=conteudo, media_type=MEDIA_TYPES[formato])
```

Aqui o polimorfismo da Aula 13 aparece de novo: a rota não sabe como cada relatório é
construído, só pede um gerador e chama `render`. Devolver `Response` em vez de um
`dict` evita que o FastAPI tente converter o texto em JSON — e o `media_type` diz ao
navegador o que ele recebeu.

```bash
curl -i http://127.0.0.1:8000/relatorio/csv
```

Procure no cabeçalho a linha `content-type: text/csv`.

### Verificação 2

Teste um formato que não existe:

```bash
curl -i http://127.0.0.1:8000/relatorio/xml
```

Você recebe `500 Internal Server Error` — um `KeyError` vazou do `criar_gerador`. Isso
é um **defeito**: o erro foi de quem chamou a API, não do servidor. As Aulas 22 e 23
corrigem isso de dois jeitos diferentes.

## 6. Convenções que valem a pena

| Pergunta                       | Convenção                                         |
| ------------------------------ | ------------------------------------------------- |
| Como nomear a rota?            | Substantivo no plural: `/clientes`, `/transacoes` |
| Quando usar parâmetro de rota? | Quando identifica *qual* recurso: `/clientes/7`   |
| Quando usar consulta?          | Para filtrar, ordenar ou paginar uma coleção      |
| O que a função devolve?        | Dados simples — o FastAPI serializa para JSON     |

## Desafio guiado

1. Extraia `carregar_resultado()` e use-a em todas as rotas.
2. Crie `GET /clientes` e `GET /metricas`.
3. Crie `GET /transacoes` com os filtros `status` e `categoria`.
4. Crie `GET /relatorio/{formato}` devolvendo `Response` com o `media_type` certo.
5. Teste todas as rotas pela página `/docs`.

## Desafio extra

Adicione o filtro `cliente_id: int | None = None` em `/transacoes`. Depois, tente
`?cliente_id=abc` e observe o que o FastAPI responde sem que você escreva uma linha de
validação.

## Resumo

Uma API REST de leitura é uma coleção de funções pequenas, cada uma associada a uma URL.
Todas as regras de negócio continuam em `core` e `services`: as rotas só traduzem
"pedido HTTP" em "chamada de função" e de volta. A Aula 22 dá estrutura aos dados que
entram e saem dessas rotas.
