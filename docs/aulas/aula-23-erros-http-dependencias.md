# Aula 23 — Erros HTTP e injeção de dependências

## Objetivo

Nesta aula você vai:

- Distinguir os códigos `200`, `404`, `422` e `503` e saber quando cada um se aplica
- Levantar erros HTTP com `HTTPException`
- Traduzir exceções do projeto em respostas HTTP com `exception_handler`
- Usar `Depends` para entregar a fonte de dados às rotas
- Remover os caminhos fixos que a Aula 21 deixou no código

## 1. Um código de status é parte do contrato

O cliente da API não lê mensagens de erro — lê o número. Cada família de códigos diz
quem errou:

| Código | Significado                | Quem errou?          | Exemplo no projeto                         |
| ------ | -------------------------- | -------------------- | ------------------------------------------ |
| `200`  | Sucesso                    | Ninguém              | `GET /clientes`                            |
| `404`  | Recurso não encontrado     | Quem chamou          | `GET /clientes/99`                         |
| `422`  | Entrada inválida           | Quem chamou          | `?status=xyz`, corpo com `idade: "trinta"` |
| `503`  | Serviço indisponível       | O servidor / infra   | `clientes.csv` não existe                  |

Devolver `200` com `{"erro": "..."}` no corpo é um erro clássico: o cliente HTTP, o
navegador e as ferramentas de monitoramento passam a achar que deu certo.

## 2. Buscando um recurso: `404`

Adicione uma rota que procura um cliente pelo `id` (parâmetro de rota, como na Aula 21):

```python
from fastapi import HTTPException


@app.get("/clientes/{cliente_id}", response_model=ClienteSchema)
def obter_cliente(cliente_id: int):
    for cliente in carregar_resultado().clientes:
        if cliente.id == cliente_id:
            return cliente
    raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} não encontrado")
```

`raise HTTPException(...)` interrompe a função como qualquer exceção, e o FastAPI a
converte em uma resposta JSON `{"detail": "..."}` com o status pedido.

```bash
curl -i http://127.0.0.1:8000/clientes/1     # 200
curl -i http://127.0.0.1:8000/clientes/99    # 404
curl -i http://127.0.0.1:8000/clientes/abc   # 422 — id não é inteiro
```

O último caso mostra a divisão de trabalho: `abc` nem chega à função, porque a
anotação `cliente_id: int` já barra. O `404` só cobre o que passou no formato mas não
existe.

!!! note "Cliente inválido também é `404`?"

    `/clientes` lista só clientes **válidos**. O cliente 3 do dataset existe no CSV, mas
    foi descartado pelo `core` — então, para a API, ele não é um recurso. É uma decisão
    de contrato; o importante é tomá-la conscientemente.

## 3. Traduzindo exceções com `exception_handler`

Apague `clientes.csv` temporariamente (ou aponte para um caminho errado) e chame
`/metricas`. O resultado é um `500` com o rastreamento do erro: o `OSError` do `open()`
atravessou a rota sem ser tratado.

Na CLI (Aula 15) e no menu (Aula 17) você já capturava `OSError`. Na API, o equivalente
é registrar **um tratador global**, em vez de um `try/except` em cada rota:

```python
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(OSError)
def fonte_indisponivel(request: Request, erro: OSError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": f"Fonte de dados indisponível: {erro}"},
    )
```

Qualquer `OSError` que escape de qualquer rota agora vira `503` com um JSON legível.
As rotas continuam sem nenhum `try`.

!!! warning "Trate exceções específicas"

    A mesma regra da Aula 17 vale aqui: registrar um handler para `Exception` esconderia
    bugs reais do seu código. Traduza apenas as exceções que representam uma condição
    **esperada** do ambiente.

## 4. O problema dos caminhos fixos

A Aula 21 deixou `carregar_resultado()` com `"data/clientes.csv"` escrito dentro dela. Isso
atrapalha de dois jeitos:

- só funciona se o servidor for iniciado na pasta `dataprocessor/`;
- é impossível testar a rota com outra fonte sem tocar em arquivos.

A solução é **inverter a dependência**: a rota declara *do que precisa* e o framework
entrega.

## 5. `Depends`: a rota pede, o FastAPI entrega

```python
from pathlib import Path

from fastapi import Depends

from ..core.resultados import ResultadoProcessamento
from ..infra.fontes import FonteDados, fonte_a_partir_de_caminhos


def obter_fonte() -> FonteDados:
    pasta = Path("data")
    return fonte_a_partir_de_caminhos(pasta / "clientes.csv", pasta / "transacoes.csv", pasta / "config.json")


def obter_resultado(fonte: FonteDados = Depends(obter_fonte)) -> ResultadoProcessamento:
    return executar_processamento(fonte)
```

Duas funções encadeadas: `obter_resultado` depende de `obter_fonte`, que não depende de
nada. As rotas passam a declarar:

```python
@app.get("/clientes/{cliente_id}", response_model=ClienteSchema)
def obter_cliente(cliente_id: int, resultado: ResultadoProcessamento = Depends(obter_resultado)):
    for cliente in resultado.clientes:
        if cliente.id == cliente_id:
            return cliente
    raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} não encontrado")
```

Reescreva as demais rotas do mesmo jeito e apague `carregar_resultado()`.

!!! tip "Isso é a Aula 14 de novo"

    `FonteDados` é a ABC que você criou para poder trocar CSV por memória. `Depends`
    é o mecanismo que permite *trocar a implementação concreta sem mexer na rota*. A
    rota só conhece o contrato; quem escolhe a implementação é a borda da aplicação.

### Verificação 1

Rode todos os casos e confira os status:

| Chamada                                 | Status esperado |
| --------------------------------------- | --------------- |
| `GET /clientes/1`                       | 200             |
| `GET /clientes/99`                      | 404             |
| `GET /clientes/abc`                     | 422             |
| `GET /transacoes?status=xyz`            | 422             |
| `GET /metricas` sem o `clientes.csv`    | 503             |

## Desafio guiado

1. Crie `GET /clientes/{cliente_id}` com `HTTPException` 404.
2. Registre o `exception_handler` de `OSError` devolvendo 503.
3. Crie `obter_fonte()` e `obter_resultado()` com `Depends`.
4. Reescreva todas as rotas para receber `resultado` via `Depends`.
5. Confira a tabela da Verificação 1.

## Desafio extra

Crie `GET /transacoes/{transacao_id}` com o mesmo padrão de `404`. Depois, decida e
documente: uma transação **recusada** deve ser encontrada por `id`? Escreva a decisão
em um comentário de uma linha acima da rota.

## Resumo

Uma boa API distingue "você pediu errado" (4xx) de "eu falhei" (5xx), e usa o status
para dizer isso. `HTTPException` e `exception_handler` cuidam das respostas; `Depends`
cuida de onde vêm as dependências. Com a fonte de dados injetada, a próxima aula pode
testar a API inteira sem tocar em nenhum arquivo.
