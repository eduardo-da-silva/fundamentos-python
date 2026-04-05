# Aula 04 — Validação de dados

## Objetivo

Nesta aula você vai:

- Escrever funções de validação para cada campo do dataset
- Usar `try/except` para tratar exceções de forma controlada
- Separar registros válidos de inválidos
- Gerar um relatório de erros de validação
- Integrar a camada de validação no **DataProcessor**

---

## 1. Por que validar?

No mundo real, dados chegam sujos. O CSV que o cliente manda, o JSON da API, o export do ERP — todos têm problemas. O sistema que não valida vai quebrar em produção de formas inesperadas.

Olhe os problemas que existem no nosso dataset:

| Registro              | Campo           | Problema                                      |
| --------------------- | --------------- | --------------------------------------------- |
| Maria Souza (ID 2)    | `email`         | `maria@email` — sem domínio válido            |
| Carlos Pereira (ID 3) | `idade`         | `-5` — valor negativo                         |
| Pedro Santos (ID 5)   | `email`         | vazio                                         |
| Pedro Santos (ID 5)   | `data_cadastro` | `2023-02-30` — dia 30 em fevereiro não existe |
| Transação 3           | `valor`         | `-50.00` — valor negativo                     |
| Transação 5           | `cliente_id`    | `10` — cliente inexistente                    |

A validação tem dois objetivos:

1. **Identificar** o que está errado (e gerar log)
2. **Separar** dados válidos dos inválidos para processar apenas o que faz sentido

---

## 2. Exceptions em Python

Python usa `try/except` para tratar erros — equivalente ao `try/catch` do JavaScript.

=== "Python"

    ```python linenums="1"
    import json

    try:
        resultado = json.loads(texto_invalido)
    except json.JSONDecodeError as e:
        print(f"Erro ao parsear JSON: {e}")
    ```

=== "JavaScript"

    ```javascript linenums="1"
    try {
        const resultado = JSON.parse(textoInvalido);
    } catch (error) {
        console.error("Erro ao parsear JSON:", error.message);
    }
    ```

### Capturando tipos específicos de erro

Python tem uma hierarquia de exceptions. Capture o tipo mais específico possível:

```python linenums="1"
def converter_idade(valor):
    try:
        idade = int(valor)
        return idade
    except ValueError:
        # valor não é um número (ex: "abc", "")
        return None
    except TypeError:
        # valor é None
        return None
```

Você pode capturar múltiplos tipos de uma vez:

```python linenums="1"
def converter_idade(valor):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return None
```

### Lançando exceptions

```python linenums="1"
def validar_email(email):
    if not email:
        raise ValueError("Email não pode ser vazio")
    if "@" not in email:
        raise ValueError(f"Email inválido: '{email}'")
    partes = email.split("@")
    if len(partes) != 2 or "." not in partes[1]:
        raise ValueError(f"Domínio inválido no email: '{email}'")
    return True
```

---

## 3. Funções de validação

A estratégia do DataProcessor é ter uma função de validação para cada campo. Cada função:

- Recebe o valor
- Retorna `True` se válido
- Retorna `False` (ou levanta exception) se inválido

### Validação de email

```python linenums="1"
def email_valido(email):
    if not email or not email.strip():
        return False
    if "@" not in email:
        return False
    partes = email.strip().split("@")
    if len(partes) != 2:
        return False
    dominio = partes[1]
    if "." not in dominio:
        return False
    return True

# Testes
print(email_valido("joao.silva@email.com"))  # True
print(email_valido("maria@email"))           # False — sem .com
print(email_valido(""))                      # False — vazio
print(email_valido(None))                    # False
```

### Validação de idade

```python linenums="1"
def idade_valida(idade):
    if idade is None:
        return False
    return 0 < idade < 150

print(idade_valida(34))   # True
print(idade_valida(-5))   # False
print(idade_valida(None)) # False
print(idade_valida(200))  # False
```

### Validação de data

```python linenums="1"
from datetime import date

def data_valida(texto_data):
    if not texto_data:
        return False
    try:
        date.fromisoformat(texto_data)
        return True
    except ValueError:
        return False

print(data_valida("2023-01-10"))  # True
print(data_valida("2023-02-30"))  # False — fevereiro não tem dia 30
print(data_valida(""))            # False
print(data_valida("10/01/2023"))  # False — formato errado
```

!!! note "ISO 8601"

    `date.fromisoformat()` aceita apenas o formato `YYYY-MM-DD`. Datas no formato `DD/MM/YYYY` vão falhar — isso é intencional. O DataProcessor vai normalizar formatos na Aula 05.

### Validação de valor de transação

```python linenums="1"
def valor_valido(valor, minimo=0):
    if valor is None:
        return False
    return valor > minimo

print(valor_valido(150.50))   # True
print(valor_valido(-50.00))   # False
print(valor_valido(0))        # False (se minimo=0, precisa ser > 0)
```

### Validação de categoria

```python linenums="1"
def categoria_valida(categoria, categorias_permitidas):
    return categoria in categorias_permitidas

categorias = ["eletronicos", "roupas", "alimentacao", "livros"]
print(categoria_valida("eletronicos", categorias))  # True
print(categoria_valida("games", categorias))        # False
```

---

## 4. Validação de um registro completo

Agora combinamos as funções para validar um cliente inteiro:

```python linenums="1"
def validar_cliente(cliente):
    erros = []

    if not cliente.get("nome", "").strip():
        erros.append("nome vazio")

    if not email_valido(cliente.get("email")):
        erros.append(f"email inválido: '{cliente.get('email')}'")

    if not idade_valida(cliente.get("idade")):
        erros.append(f"idade inválida: {cliente.get('idade')}")

    if not data_valida(cliente.get("data_cadastro")):
        erros.append(f"data inválida: '{cliente.get('data_cadastro')}'")

    return erros  # lista vazia = sem erros
```

Uso:

```python linenums="1"
for cliente in clientes:
    erros = validar_cliente(cliente)
    if erros:
        print(f"[INVÁLIDO] ID {cliente['id']} ({cliente['nome']}): {', '.join(erros)}")
    else:
        print(f"[OK] ID {cliente['id']} ({cliente['nome']})")
```

Saída esperada:

```
[OK] ID 1 (João Silva)
[INVÁLIDO] ID 2 (Maria Souza): email inválido: 'maria@email'
[INVÁLIDO] ID 3 (Carlos Pereira): idade inválida: -5
[OK] ID 4 (Ana Lima)
[INVÁLIDO] ID 5 (Pedro Santos): email inválido: '', data inválida: '2023-02-30'
```

---

## 5. Separar válidos de inválidos

Para o DataProcessor, precisamos de duas listas: clientes que passaram na validação e os que falharam.

```python linenums="1"
def separar_clientes(clientes):
    validos = []
    invalidos = []

    for cliente in clientes:
        erros = validar_cliente(cliente)
        if erros:
            invalidos.append({
                "registro": cliente,
                "erros": erros
            })
        else:
            validos.append(cliente)

    return validos, invalidos

validos, invalidos = separar_clientes(clientes)

print(f"Válidos: {len(validos)}")
print(f"Inválidos: {len(invalidos)}")
print()
print("Registros inválidos:")
for item in invalidos:
    nome = item["registro"]["nome"]
    erros = ", ".join(item["erros"])
    print(f"  {nome}: {erros}")
```

---

## 6. Validação cruzada — transações x clientes

Um dos problemas do dataset é a transação com `cliente_id: 10`, que não corresponde a nenhum cliente.

```python linenums="1"
def validar_transacao(transacao, clientes, config):
    erros = []

    # Verificar se o cliente existe
    ids_clientes = {c["id"] for c in clientes}
    if transacao.get("cliente_id") not in ids_clientes:
        erros.append(f"cliente_id inexistente: {transacao.get('cliente_id')}")

    # Verificar valor
    valor_minimo = config.get("valor_minimo", 0)
    if not valor_valido(transacao.get("valor"), minimo=valor_minimo):
        erros.append(f"valor inválido: {transacao.get('valor')}")

    # Verificar categoria
    categorias = config.get("categorias_validas", [])
    if not categoria_valida(transacao.get("categoria", ""), categorias):
        erros.append(f"categoria inválida: '{transacao.get('categoria')}'")

    # Verificar status
    status_validos = config.get("status_validos", [])
    if transacao.get("status") not in status_validos:
        erros.append(f"status inválido: '{transacao.get('status')}'")

    return erros
```

!!! note "Set para lookup eficiente"

    `{c["id"] for c in clientes}` cria um `set` de IDs. Busca em `set` é O(1) — muito mais rápido que percorrer uma lista inteira quando há muitos registros.

---

## 7. Aplicação no projeto — DataProcessor

Crie o arquivo `validador.py`:

```python linenums="1" title="dataprocessor/validador.py"
# validador.py
from datetime import date


def email_valido(email):
    if not email or not email.strip():
        return False
    if "@" not in email:
        return False
    partes = email.strip().split("@")
    if len(partes) != 2 or "." not in partes[1]:
        return False
    return True


def idade_valida(idade):
    if idade is None:
        return False
    return 0 < idade < 150


def data_valida(texto):
    if not texto:
        return False
    try:
        date.fromisoformat(texto)
        return True
    except ValueError:
        return False


def valor_valido(valor, minimo=0):
    if valor is None:
        return False
    return valor > minimo


def validar_cliente(cliente):
    erros = []
    if not cliente.get("nome", "").strip():
        erros.append("nome vazio")
    if not email_valido(cliente.get("email")):
        erros.append(f"email inválido: '{cliente.get('email')}'")
    if not idade_valida(cliente.get("idade")):
        erros.append(f"idade inválida: {cliente.get('idade')}")
    if not data_valida(cliente.get("data_cadastro")):
        erros.append(f"data inválida: '{cliente.get('data_cadastro')}'")
    return erros


def validar_transacao(transacao, ids_clientes, config):
    erros = []
    if transacao.get("cliente_id") not in ids_clientes:
        erros.append(f"cliente_id inexistente: {transacao.get('cliente_id')}")
    if not valor_valido(transacao.get("valor"), config.get("valor_minimo", 0)):
        erros.append(f"valor inválido: {transacao.get('valor')}")
    categorias = config.get("categorias_validas", [])
    if transacao.get("categoria") not in categorias:
        erros.append(f"categoria inválida: '{transacao.get('categoria')}'")
    status_validos = config.get("status_validos", [])
    if transacao.get("status") not in status_validos:
        erros.append(f"status inválido: '{transacao.get('status')}'")
    return erros


def separar_registros(registros, funcao_validar, **kwargs):
    validos = []
    invalidos = []
    for registro in registros:
        erros = funcao_validar(registro, **kwargs)
        if erros:
            invalidos.append({"registro": registro, "erros": erros})
        else:
            validos.append(registro)
    return validos, invalidos
```

Atualize o `main.py`:

```python linenums="1" title="dataprocessor/main.py"
# main.py
from leitor import carregar_clientes, carregar_transacoes, carregar_config
from validador import validar_cliente, validar_transacao, separar_registros

clientes = carregar_clientes("data/clientes.csv")
transacoes = carregar_transacoes("data/transacoes.csv")
config = carregar_config("data/config.json")

# Separação de clientes
clientes_validos, clientes_invalidos = separar_registros(
    clientes, validar_cliente
)

ids_clientes_validos = {c["id"] for c in clientes_validos}

# Separação de transações
transacoes_validas, transacoes_invalidas = separar_registros(
    transacoes, validar_transacao,
    ids_clientes=ids_clientes_validos, config=config
)

print(f"Clientes válidos: {len(clientes_validos)}")
print(f"Clientes inválidos: {len(clientes_invalidos)}")
print(f"Transações válidas: {len(transacoes_validas)}")
print(f"Transações inválidas: {len(transacoes_invalidas)}")
```

---

## Desafio guiado (em sala)

**Separar clientes válidos e inválidos**

1. Implemente as funções `email_valido()`, `idade_valida()` e `data_valida()` conforme visto na aula
2. Implemente `validar_cliente(cliente)` retornando uma lista de erros
3. Percorra os 5 clientes do dataset e classifique cada um como `[OK]` ou `[INVÁLIDO]`
4. Ao final, imprima o resumo:

```
=== VALIDAÇÃO DE CLIENTES ===
[OK] ID 1 — João Silva
[INVÁLIDO] ID 2 — Maria Souza: email inválido: 'maria@email'
[INVÁLIDO] ID 3 — Carlos Pereira: idade inválida: -5
[OK] ID 4 — Ana Lima
[INVÁLIDO] ID 5 — Pedro Santos: email inválido: '', data inválida: '2023-02-30'

Resultado: 2 válidos, 3 inválidos
```

---

## Desafio extra (para casa)

Implemente a validação completa de transações:

1. `validar_transacao(transacao, ids_clientes, config)` — usando a função de validação cruzada vista na aula
2. Execute a validação nas 5 transações
3. Gere o relatório:

```
=== VALIDAÇÃO DE TRANSAÇÕES ===
[OK] ID 1 — cliente 1 | R$ 150.50 | eletronicos | aprovado
[OK] ID 2 — cliente 2 | R$ 200.00 | roupas | pendente
[INVÁLIDO] ID 3 — cliente 3: valor inválido: -50.0
[OK] ID 4 — cliente 1 | R$ 300.00 | eletronicos | recusado
[INVÁLIDO] ID 5 — cliente 10: cliente_id inexistente: 10

Resultado: 3 válidas, 2 inválidas
```

**Atenção:** a validação de transações deve usar **apenas os IDs dos clientes válidos** (não todos os clientes). Use o resultado da validação de clientes.
