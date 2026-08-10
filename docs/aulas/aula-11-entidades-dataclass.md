# Aula 11 — Entidades com `dataclass`

## Objetivo

Nesta aula você vai:

- Substituir os dicionários de dados por entidades explícitas (`Cliente`, `Transacao`)
- Usar `@dataclass` para declarar dados com contrato claro
- Entender o que o Python gera de graça: `__init__`, `__repr__` e `__eq__`
- Trabalhar com entidades imutáveis usando `frozen=True` e `replace()`
- Manter o comportamento funcional idêntico ao da Aula 10

---

## 1. O problema do dicionário solto

Até aqui, um cliente é isto:

```python linenums="1"
cliente = {
    "id": 1,
    "nome": "João Silva",
    "email": "joao.silva@email.com",
    "idade": 34,
    "cidade": "Joinville",
    "data_cadastro": "2023-01-10",
}
```

Funciona. Mas o dicionário não tem contrato nenhum:

- `cliente["nomee"]` só quebra em tempo de execução, na hora errada
- nada impede um cliente chegar sem `email` em um trecho e com `email` em outro
- o editor não sabe quais campos existem, então não ajuda com autocomplete
- ler `validar_cliente()` não diz qual é o formato esperado do parâmetro

!!! warning "Cheiro de código"

    Quando um dicionário sempre tem as mesmas chaves e circula por todas as camadas,
    ele já é uma entidade do domínio — só que sem nome e sem contrato.

---

## 2. `@dataclass`: contrato com pouco código

O módulo `dataclasses` já apareceu na Aula 10, em `AppConfig`. Agora ele vira a forma
padrão de representar os dados do domínio.

```python linenums="1" title="dataprocessor/dataprocessor/core/entidades.py"
from dataclasses import dataclass


@dataclass(frozen=True)
class Cliente:
    id: int
    nome: str
    email: str
    idade: int
    cidade: str
    data_cadastro: str


@dataclass(frozen=True)
class Transacao:
    id: int
    cliente_id: int
    valor: float
    categoria: str
    data: str
    status: str
```

Isso é uma classe — a primeira do domínio. Repare no que **não** foi escrito: nenhum
`__init__`, nenhum `self.nome = nome`. O decorador `@dataclass` gera isso a partir dos
campos declarados.

O que o Python gera de graça:

| Método gerado | O que dá na prática |
| ------------- | ------------------- |
| `__init__` | `Cliente(id=1, nome="João Silva", ...)` |
| `__repr__` | `print(cliente)` mostra todos os campos, ótimo para depurar |
| `__eq__` | `cliente_a == cliente_b` compara campo a campo, não identidade |

```python linenums="1"
>>> cliente
Cliente(id=1, nome='João Silva', email='joao.silva@email.com', idade=34, cidade='Joinville', data_cadastro='2023-01-10')
```

!!! note "Anotação de tipo não valida nada"

    `idade: int` é documentação para você e para o editor. O Python **não** rejeita
    `idade="abc"` em tempo de execução. Quem valida continua sendo o `core/validador.py`.
    Type hints entram para valer no Módulo 7.

---

## 3. `frozen=True`: entidade que não muda por acidente

`frozen=True` bloqueia atribuição depois da criação:

```python linenums="1"
>>> cliente.nome = "Outro Nome"
FrozenInstanceError: cannot assign to field 'nome'
```

Parece limitação, mas resolve um problema real do pipeline: hoje, qualquer função que
receba um cliente pode alterá-lo em silêncio e ninguém descobre onde. Com `frozen=True`,
transformar um dado exige **devolver uma nova entidade** — que é exatamente o que
`transformador.py` já fazia com dicionários.

---

## 4. A leitura passa a produzir entidades

A fronteira entre "dado externo" e "domínio" é a camada `infra`. É lá que o dicionário
do `csv.DictReader` vira entidade:

```python linenums="1" title="dataprocessor/dataprocessor/infra/arquivos.py" hl_lines="5 19"
import csv
import json
import os

from ..core.entidades import Cliente, Transacao

# ... _para_int e _para_float continuam iguais ...


def carregar_clientes(caminho):
    if not os.path.exists(caminho):
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return []

    clientes = []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            cliente = Cliente(
                id=_para_int(linha["id"]),
                nome=linha["nome"].strip(),
                email=linha["email"].strip(),
                idade=_para_int(linha["idade"]),
                cidade=linha["cidade"].strip(),
                data_cadastro=linha["data_cadastro"].strip(),
            )
            clientes.append(cliente)
    return clientes
```

`carregar_transacoes()` muda do mesmo jeito, montando `Transacao(...)`.

!!! tip "Regra de fronteira"

    Dicionário é formato de arquivo. Entidade é formato de domínio.
    A conversão acontece uma vez só, na entrada — nunca espalhada pelo `core`.

---

## 5. O `core` passa a usar atributos

A mudança no `core` é mecânica: `registro["campo"]` vira `registro.campo`.

```python linenums="1" title="dataprocessor/dataprocessor/core/validador.py"
def validar_cliente(cliente):
    erros = []
    if not cliente.nome.strip():
        erros.append("nome vazio")
    if not email_valido(cliente.email):
        erros.append(f"email inválido: '{cliente.email}'")
    if not idade_valida(cliente.idade):
        erros.append(f"idade inválida: {cliente.idade}")
    if not data_valida(cliente.data_cadastro):
        erros.append(f"data inválida: '{cliente.data_cadastro}'")
    return erros
```

Note que os `.get("nome", "")` sumiram. Com entidade, o campo **existe sempre** — o que
pode faltar é o valor, não a chave. Some uma classe inteira de bug.

O mesmo vale para as métricas:

```python linenums="1" title="dataprocessor/dataprocessor/core/metricas.py"
def transacoes_aprovadas(transacoes):
    return [t for t in transacoes if t.status == "aprovado" and t.valor > 0]


def total_aprovado(transacoes):
    return sum(t.valor for t in transacoes_aprovadas(transacoes))
```

E em `services/processamento.py` muda uma linha:

```python linenums="1"
ids_validos = {c.id for c in clientes_validos}
```

---

## 6. Transformar sem mutar: `replace()`

Como a entidade é imutável, `transformador.py` usa `dataclasses.replace()`, que cria uma
cópia trocando só os campos indicados:

```python linenums="1" title="dataprocessor/dataprocessor/core/transformador.py" hl_lines="2 8"
import unicodedata
from dataclasses import replace

# ... normalizar_nome, normalizar_email, normalizar_cidade continuam iguais ...


def transformar_cliente(cliente):
    return replace(
        cliente,
        nome=normalizar_nome(cliente.nome),
        email=normalizar_email(cliente.email),
        cidade=normalizar_cidade(cliente.cidade),
        data_cadastro=cliente.data_cadastro.strip(),
    )
```

Compare com a versão da Aula 10: antes era preciso reescrever **todos** os campos no
dicionário novo, inclusive `id` e `idade`, que não mudam. Agora só aparecem os campos que
de fato são normalizados — o resto é copiado.

Na prática:

```python linenums="1"
>>> c = Cliente(id=7, nome="  ana LIMA ", email="ANA@Email.COM", idade=45,
...             cidade=" Joinville ", data_cadastro="2023-01-25")
>>> transformar_cliente(c)
Cliente(id=7, nome='Ana Lima', email='ana@email.com', idade=45, cidade='Joinville', data_cadastro='2023-01-25')
```

---

## 7. Estrutura após esta aula

```text
dataprocessor/
    main.py
    dataprocessor/
        __init__.py
        config.py
        core/
            __init__.py
            entidades.py      ← novo
            validador.py
            transformador.py
            metricas.py
        infra/
            __init__.py
            arquivos.py
        services/
            __init__.py
            processamento.py
```

`main.py` e `config.py` não mudam nesta aula.

---

## 8. Comparação com JavaScript

Em JS, o equivalente mais próximo é o objeto literal com uma `class` ou uma factory.

=== "Python"

    ```python linenums="1"
    from dataclasses import dataclass, replace

    @dataclass(frozen=True)
    class Cliente:
        id: int
        nome: str

    c = Cliente(id=1, nome="joão silva")
    c2 = replace(c, nome="João Silva")
    ```

=== "JavaScript"

    ```javascript linenums="1"
    class Cliente {
      constructor(id, nome) {
        this.id = id;
        this.nome = nome;
        Object.freeze(this);
      }
    }

    const c = new Cliente(1, "joão silva");
    const c2 = new Cliente(c.id, "João Silva");
    ```

Diferença prática: em Python, `__init__`, `__repr__`, `__eq__` e a cópia com `replace()`
vêm prontos. Em JS, cada um desses precisa ser escrito à mão (`toString`, comparação
campo a campo, spread).

---

## 9. Por que essa mudança melhora o software?

- o domínio ganha vocabulário: existe `Cliente`, não "aquele dicionário com seis chaves"
- erro de nome de campo aparece como `AttributeError` claro, não como `KeyError` distante
- o editor passa a sugerir os campos e a apontar erro de digitação
- imutabilidade elimina mutação acidental no meio do pipeline
- `__eq__` gerado deixa comparação de registros trivial — base direta para os testes do Módulo 7

!!! note "Invariante do módulo"

    O Módulo 6 muda a forma de representar e organizar o comportamento.
    Os números do relatório continuam exatamente os mesmos.

---

## Desafio guiado (em sala)

**Migrar o DataProcessor de dicionários para entidades**

1. Crie `core/entidades.py` com `Cliente` e `Transacao` usando `@dataclass(frozen=True)`
2. Ajuste `infra/arquivos.py` para montar entidades em vez de dicionários
3. Troque `registro["campo"]` por `registro.campo` em `core/validador.py` e `core/metricas.py`
4. Reescreva `transformar_cliente()` e `transformar_transacao()` com `replace()`
5. Ajuste `ids_validos` em `services/processamento.py`
6. Rode e confirme que a saída não mudou

Critério de aceite:

```text
Clientes válidos: 2
Clientes inválidos: 3
Transações válidas: 2
Transações inválidas: 3
Média de idade: 39.5
Total aprovado: R$ 150.50
Ticket médio aprovado: R$ 150.50
```

!!! tip "Se aparecer `TypeError: 'Cliente' object is not subscriptable`"

    Sobrou algum `registro["campo"]` em cima de uma entidade. Procure por `["` nos
    arquivos do `core`.

---

## Desafio extra (para casa)

O relatório de inválidos hoje mostra a entidade inteira. Adicione um campo calculado à
entidade `Cliente` para melhorar essa saída:

```python
@property
def identificacao(self):
    ...
```

Requisitos:

1. devolver algo como `#5 Pedro Santos` (id e nome)
2. usar `@property` — o valor é derivado, não um campo do `dataclass`
3. não fazer leitura de arquivo nem `print()` dentro da entidade
4. usar essa propriedade ao listar os registros inválidos no `main.py`

Reflexão:

- `identificacao` é regra de negócio ou formatação de saída? Se for formatação, ela
  deveria mesmo morar na entidade, ou na camada que exibe o resultado?
