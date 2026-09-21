# Aula 19 — Trailer: a mesma regra de negócio atrás de um endpoint REST

## Objetivo

Nesta aula você vai:

- Confirmar, na prática, que `processar_caminhos()` não sabe (nem precisa saber) quem a
  chama
- Instalar uma dependência externa pela primeira vez no curso, conscientemente
- Criar um endpoint HTTP mínimo com FastAPI que devolve o `ResultadoProcessamento`
- Entender o que essa aula antecipa da Fase 2 (curso de FastAPI) e o que fica para lá

!!! warning "Esta aula quebra uma regra do curso, de propósito"

    Desde a Aula 01 o projeto usa só a biblioteca padrão. Hoje instalamos uma
    dependência externa (`fastapi` + `uvicorn`) porque o objetivo não é ensinar FastAPI
    a fundo — é provar, com poucas linhas, que o `core`/`services` que você construiu
    está pronto para virar uma API de verdade na próxima fase da trilha.

## 1. Ambiente isolado para o experimento

Não instale nada no Python do sistema. Crie um ambiente virtual só para esta aula:

```bash
cd dataprocessor
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install fastapi uvicorn
```

Um `pyproject.toml` com gerenciamento de dependências completo é assunto da Fase 2 —
aqui o `pip install` direto é suficiente para o experimento.

## 2. O endpoint mais simples possível

Novo módulo, ao lado do menu:

```text
dataprocessor/
    dataprocessor/
        interfaces/
            menu.py
            api.py
```

```python
from fastapi import FastAPI

from ..infra.fontes import fonte_a_partir_de_caminhos
from ..services.processamento import executar_processamento

app = FastAPI()


@app.get("/relatorio")
def relatorio():
    fonte = fonte_a_partir_de_caminhos(
        "data/clientes.csv",
        "data/transacoes.csv",
        "data/config.json",
    )
    resultado = executar_processamento(fonte)
    return resultado.to_dict()
```

Repare: nenhuma linha nova de regra de negócio. `executar_processamento` e `to_dict()`
já existiam desde as Aulas 09 e 13.

!!! note "`@app.get(...)` é só um decorator"

    Você já usa `@dataclass`, `@property` e `@abstractmethod` desde a Aula 11. Um
    decorator de rota do FastAPI faz a mesma coisa conceitualmente: registra a função
    logo abaixo dele para ser chamada em uma circunstância especial — aqui, uma
    requisição `GET /relatorio` — em vez de escondê-la atrás de mágica.

## 3. Rodando o servidor

```bash
uvicorn dataprocessor.interfaces.api:app --reload
```

Acesse (navegador ou `curl`):

```bash
curl http://127.0.0.1:8000/relatorio
```

Você deve ver o mesmo conteúdo que `RelatorioJson.render()` produz na CLI — só que
entregue por HTTP, sem terminal, sem argumentos de linha de comando.

### Verificação 1

Compare as duas saídas para o mesmo dataset:

```bash
python -m dataprocessor --clientes data/clientes.csv --transacoes data/transacoes.csv \
  --config data/config.json --formato json --output output/
curl http://127.0.0.1:8000/relatorio
```

O campo `metricas.total_aprovado` deve ser `150.5` nos dois casos.

## 4. Três adaptadores, um núcleo

```text
main.py (CLI)          interfaces/menu.py (interativo)     interfaces/api.py (REST)
argparse                input()                              requisição HTTP
        \                       |                                /
         \                      |                               /
          -----------  fonte_a_partir_de_caminhos  ---------------
                                 |
                       executar_processamento()
                                 |
                         ResultadoProcessamento
```

Três formas de entrar, uma forma de processar.

## 5. O que fica para a Fase 2

Esta aula é deliberadamente mínima. O curso de FastAPI vai cobrir o que aqui foi
ignorado de propósito:

- múltiplos endpoints e verbos HTTP (`POST`, `PUT`, `DELETE`)
- validação de entrada com Pydantic
- tratamento de erros HTTP (`404`, `422`, etc.)
- autenticação e configuração por ambiente
- persistência em banco de dados (Fase 3)

O que você já tem pronto: as regras de negócio, os testes e a separação de camadas que
tornam tudo isso possível sem reescrever o `core`.

## Desafio guiado

1. Crie o ambiente virtual e instale `fastapi`/`uvicorn`.
2. Escreva `interfaces/api.py` com o endpoint `/relatorio`.
3. Rode com `uvicorn` e confirme a resposta no navegador ou com `curl`.
4. Compare o JSON retornado com o gerado pela CLI no mesmo dataset.

## Desafio extra

Adicione um segundo endpoint, `/relatorio/csv`, que devolve a mesma informação usando
`RelatorioCsv` em vez de `to_dict()`. Preste atenção ao cabeçalho de conteúdo
(`Content-Type`) da resposta.

## Resumo

Uma API REST, para o `core`, é só mais uma pergunta chegando de um lugar diferente. Se a
Aula 18 não tivesse isolado `processar_caminhos()`/`fonte_a_partir_de_caminhos()` da
leitura de teclado, esta aula não existiria em poucas linhas de endpoint — existiria
como uma reescrita.
