# Aula 14 — ABC para fontes de dados

## Objetivo

Nesta aula você vai:

- Identificar o acoplamento do service com arquivos
- Criar uma abstração com `ABC`
- Implementar fontes concretas por herança
- Usar uma fonte em memória nos testes
- Entender injeção de dependência na prática

## 1. O problema do service acoplado

Quando o service chama diretamente funções de leitura, o caso de uso depende do
filesystem:

```python
clientes = carregar_clientes("data/clientes.csv")
```

Isso dificulta testes. Para testar uma regra de negócio, seria necessário criar ou
alterar arquivos. Vamos inverter a dependência: o service receberá uma fonte de dados.

## 2. Definindo o contrato abstrato

Crie a classe-base em `infra/fontes.py`:

```python
from abc import ABC, abstractmethod


class FonteDados(ABC):
    @abstractmethod
    def carregar_clientes(self) -> list[Cliente]:
        ...

    @abstractmethod
    def carregar_transacoes(self) -> list[Transacao]:
        ...

    @abstractmethod
    def carregar_config(self) -> dict:
        ...
```

A ABC não sabe de CSV, JSON ou memória. Ela apenas declara o que uma fonte precisa
oferecer.

### Verificação 1

Antes de criar implementações, teste o contrato:

```python
def test_fonte_dados_e_uma_abc(self):
    with self.assertRaises(TypeError):
        FonteDados()
```

Uma classe que não implementar os três métodos também não poderá ser instanciada.

## 3. Fonte de arquivos

Faça a classe que já lê CSV e JSON herdar da abstração:

```python
class FonteDadosArquivos(FonteDados):
    def __init__(self, caminho_clientes, caminho_transacoes, caminho_config):
        self.caminho_clientes = caminho_clientes
        self.caminho_transacoes = caminho_transacoes
        self.caminho_config = caminho_config

    def carregar_clientes(self):
        return carregar_clientes(self.caminho_clientes)

    def carregar_transacoes(self):
        return carregar_transacoes(self.caminho_transacoes)

    def carregar_config(self):
        return carregar_config(self.caminho_config)
```

Observe a divisão de responsabilidades:

```text
arquivos.py       sabe converter CSV/JSON em entidades
FonteDadosArquivos guarda os caminhos e delega a leitura
services          apenas usa as operações da fonte
```

## 4. Fonte em memória

Para testar o service, crie uma implementação que recebe entidades prontas:

```python
class FonteDadosMemoria(FonteDados):
    def __init__(self, clientes=(), transacoes=(), config=None):
        self._clientes = tuple(clientes)
        self._transacoes = tuple(transacoes)
        self._config = dict(config or {})

    def carregar_clientes(self):
        return list(self._clientes)

    def carregar_transacoes(self):
        return list(self._transacoes)

    def carregar_config(self):
        return dict(self._config)
```

A cópia dos dados de entrada evita que a fonte altere acidentalmente a coleção recebida.

## 5. Injetando a fonte no service

Altere a assinatura do caso de uso:

```python
def executar_processamento(fonte: FonteDados) -> ResultadoProcessamento:
    clientes_raw = fonte.carregar_clientes()
    transacoes_raw = fonte.carregar_transacoes()
    config = fonte.carregar_config()
    # validação, transformação e métricas continuam no core
```

O service agora recebe o objeto pronto. Ele não decide se os dados vieram de arquivo,
memória ou outra origem.

## 6. O mesmo caso de uso com duas fontes

Fonte real:

```python
fonte = FonteDadosArquivos(
    "data/clientes.csv",
    "data/transacoes.csv",
    "data/config.json",
)
resultado = executar_processamento(fonte)
```

Fonte de teste:

```python
fonte = FonteDadosMemoria(
    clientes=[cliente],
    transacoes=[transacao],
    config={"valor_minimo": 0, "categorias_validas": ["livros"]},
)
resultado = executar_processamento(fonte)
```

O código do service não muda entre os dois casos. Essa substituição é o ganho prático
da abstração.

### Verificação 2

Execute:

```bash
python -m unittest tests.test_processamento -v
```

O teste em memória deve confirmar a normalização e a métrica de uma transação aprovada.

## Desafio guiado

1. Crie `FonteDados(ABC)`.
2. Marque os três métodos com `@abstractmethod`.
3. Faça `FonteDadosArquivos` herdar da ABC.
4. Crie `FonteDadosMemoria`.
5. Altere o service para receber `FonteDados`.
6. Teste o service sem abrir arquivos.

## Desafio extra

Implemente uma fonte em memória filtrada por cidade. Ela deve cumprir o mesmo contrato,
mas não pode duplicar as regras de validação do `core`.

## Resumo

A ABC permite ensinar explicitamente quais operações uma fonte deve oferecer. As classes
concretas ensinam herança e implementação, enquanto o service aprende a depender de uma
abstração em vez de depender de um arquivo específico.
