# Aula 24 — Testando a API sem subir servidor

## Objetivo

Nesta aula você vai:

- Testar rotas HTTP com `TestClient`, sem `uvicorn` e sem rede
- Substituir a fonte de dados nos testes com `dependency_overrides`
- Escrever testes para sucesso, `404`, `422` e `503`
- Testar o `POST /processar` com corpos válidos e inválidos
- Entender o que cada camada de teste do projeto garante

## 1. Por que testar pela API, se o `core` já tem testes?

Os testes das Aulas 12 a 18 garantem que as regras estão certas. Eles **não** garantem
que:

- a rota `/clientes/{id}` devolve `404` e não `200` com corpo vazio;
- `?status=xyz` é recusado com `422`;
- o `Content-Type` do relatório CSV é `text/csv`;
- um `OSError` vira `503` e não um rastreamento de pilha.

Esses comportamentos pertencem à porta de entrada, e portanto precisam de testes na
porta de entrada.

## 2. O `TestClient`

O FastAPI acompanha um cliente que chama a aplicação **dentro do mesmo processo**:

```python
from fastapi.testclient import TestClient

from dataprocessor.interfaces.api import app

client = TestClient(app)
resposta = client.get("/metricas")
print(resposta.status_code, resposta.json())
```

Não há servidor, porta nem `curl`. Ele depende do pacote `httpx`, que já está na lista
`api` do `pyproject.toml` (Aula 25) — por ora, `pip install httpx` no ambiente virtual.

## 3. Trocando a fonte de dados: `dependency_overrides`

Com a Aula 23, as rotas pedem a fonte via `Depends(obter_fonte)`. Em um teste, você
diz ao FastAPI: *"sempre que alguém pedir `obter_fonte`, entregue esta função no lugar"*:

```python
app.dependency_overrides[obter_fonte] = fonte_de_teste
```

E `fonte_de_teste` usa a `FonteDadosMemoria` da Aula 14:

```python
from dataprocessor.core.entidades import Cliente, Transacao
from dataprocessor.infra.fontes import FonteDadosMemoria

CONFIG = {
    "categorias_validas": ["eletronicos", "livros"],
    "status_validos": ["aprovado", "pendente", "recusado"],
    "valor_minimo": 0,
}


def fonte_de_teste():
    return FonteDadosMemoria(
        clientes=[
            Cliente(1, "Ana Lima", "ana@email.com", 40, "Joinville", "2023-01-10"),
            Cliente(2, "Bia Souza", "bia@email.com", 20, "Blumenau", "2023-02-15"),
            Cliente(3, "Sem Email", "", 30, "Curitiba", "2023-03-20"),
        ],
        transacoes=[
            Transacao(1, 1, 100.0, "livros", "2023-05-10", "aprovado"),
            Transacao(2, 2, 50.0, "eletronicos", "2023-05-11", "pendente"),
            Transacao(3, 1, 25.0, "livros", "2023-05-12", "aprovado"),
        ],
        config=CONFIG,
    )
```

Os dados são pequenos e controlados: você sabe de cabeça que o total aprovado é `125.0`
e que um dos três clientes é inválido (sem e-mail). Testes com dataset real escondem a
conta; testes com dados mínimos a mostram.

## 4. Estrutura do arquivo de testes

```python
import unittest

from fastapi.testclient import TestClient

from dataprocessor.interfaces.api import app, obter_fonte


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[obter_fonte] = fonte_de_teste
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
```

O `tearDown` é obrigatório: `app` é um objeto global, e um *override* esquecido vazaria
para os outros testes — a clássica causa de teste que passa sozinho e falha em
conjunto.

## 5. Os testes

Cada status da tabela da Aula 23 ganha um teste:

```python
    def test_metricas(self):
        corpo = self.client.get("/metricas").json()
        self.assertEqual(corpo["clientes_validos"], 2)
        self.assertEqual(corpo["clientes_invalidos"], 1)
        self.assertEqual(corpo["total_aprovado"], 125.0)

    def test_cliente_inexistente_devolve_404(self):
        resposta = self.client.get("/clientes/99")
        self.assertEqual(resposta.status_code, 404)
        self.assertIn("99", resposta.json()["detail"])

    def test_id_nao_numerico_devolve_422(self):
        self.assertEqual(self.client.get("/clientes/abc").status_code, 422)

    def test_filtra_transacoes_por_status(self):
        corpo = self.client.get("/transacoes", params={"status": "aprovado"}).json()
        self.assertEqual([t["id"] for t in corpo], [1, 3])

    def test_relatorio_csv_tem_content_type(self):
        resposta = self.client.get("/relatorio/csv")
        self.assertTrue(resposta.headers["content-type"].startswith("text/csv"))
```

Para o `503`, o teste troca a fonte por uma que aponta para arquivos inexistentes —
a única situação em que a fonte *real* é útil:

```python
    def test_fonte_indisponivel_devolve_503(self):
        from dataprocessor.infra.fontes import FonteDadosArquivos

        app.dependency_overrides[obter_fonte] = lambda: FonteDadosArquivos("x.csv", "y.csv", "z.json")
        resposta = self.client.get("/metricas")
        self.assertEqual(resposta.status_code, 503)
```

### Verificação 1

Rode a suíte completa de dentro de `dataprocessor/`:

```bash
python -m unittest discover -s tests -v
```

Sem `fastapi` instalado, os testes da API aparecem como `skipped` (o arquivo de testes
trata o `ImportError`) e os demais continuam passando — a API é uma dependência
opcional do projeto, e a suíte respeita isso.

## 6. Testando o `POST`

Para o `POST /processar`, não é preciso `dependency_overrides`: a rota já recebe os
dados no corpo. Monte o corpo em um método auxiliar e varie só o que importa em cada
teste:

```python
class ProcessarTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def corpo(self, **mudancas):
        base = {
            "clientes": [{"id": 1, "nome": "Ana", "email": "ana@email.com", "idade": 30,
                          "cidade": "Joinville", "data_cadastro": "2023-01-10"}],
            "transacoes": [{"id": 1, "cliente_id": 1, "valor": 10.5, "categoria": "livros",
                            "data": "2023-05-10", "status": "aprovado"}],
            "config": CONFIG,
        }
        base.update(mudancas)
        return base

    def test_processa_corpo_valido(self):
        resposta = self.client.post("/processar", json=self.corpo())
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["total_aprovado"], 10.5)

    def test_regra_de_negocio_ainda_vem_do_core(self):
        transacao = {"id": 1, "cliente_id": 1, "valor": 10.5, "categoria": "inexistente",
                     "data": "2023-05-10", "status": "aprovado"}
        corpo = self.client.post("/processar", json=self.corpo(transacoes=[transacao])).json()
        self.assertEqual(corpo["transacoes_invalidas"], 1)

    def test_corpo_mal_formado_devolve_422(self):
        resposta = self.client.post("/processar", json={"clientes": "nao-e-lista"})
        self.assertEqual(resposta.status_code, 422)
```

O segundo e o terceiro teste, lado a lado, documentam a separação da Aula 22: formato
ruim → `422`; formato certo e regra de negócio violada → `200` com a contagem de
inválidos.

!!! tip "Um bug que o teste revela"

    Se você removeu `"data_cadastro"` do cliente de exemplo, o `total_aprovado` volta
    `0.0`. O Pydantic aceitou (o campo tem valor padrão `""`), mas o `core` rejeita um
    cliente sem data — e, sem cliente válido, a transação perde o vínculo. Dados mínimos
    nos testes ajudam a enxergar esse tipo de dependência entre regras.

## Desafio guiado

1. Instale `httpx` e crie `tests/test_api.py`.
2. Escreva `fonte_de_teste()` com `FonteDadosMemoria`.
3. Configure `setUp`/`tearDown` com `dependency_overrides`.
4. Escreva os testes de métricas, `404`, `422`, filtro e `Content-Type`.
5. Escreva os três testes do `POST /processar`.
6. Rode a suíte inteira e confirme que todos passam.

## Desafio extra

Escreva um teste que compara `GET /metricas` com o resultado direto de
`executar_processamento(fonte_de_teste())`. Se os dois divergirem, algum dos adaptadores
(API ou service) está fazendo contas que não deveria.

## Resumo

Cada camada do projeto tem sua suíte: o `core` é testado com dados, o `service` com
`FonteDadosMemoria`, a API com `TestClient`. Nenhum teste precisa de servidor, rede ou
arquivo em disco — e foi a arquitetura das aulas anteriores que tornou isso possível.
