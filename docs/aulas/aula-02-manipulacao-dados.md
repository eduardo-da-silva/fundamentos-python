# Aula 02 — Manipulação de dados

## Objetivo

Nesta aula você vai:

- Usar loops para processar coleções de dados
- Escrever funções reutilizáveis em Python
- Calcular métricas de agregação sobre o dataset
- Lidar com dados inválidos durante o processamento
- Adicionar as primeiras funções ao **DataProcessor**

---

## 1. Loops em Python

Python tem dois loops principais: `for` e `while`. No contexto de data processing, o `for` é o mais usado.

### `for` em listas

```python linenums="1"
clientes = [
    {"id": 1, "nome": "João Silva", "idade": 34},
    {"id": 2, "nome": "Maria Souza", "idade": 28},
    {"id": 3, "nome": "Carlos Pereira", "idade": -5},
]

for cliente in clientes:
    print(cliente["nome"])
```

### `enumerate` — quando você precisa do índice

=== "Python"

    ```python linenums="1"
    for i, cliente in enumerate(clientes, start=1):
        print(f"{i}. {cliente['nome']}")
    ```

=== "JavaScript"

    ```javascript linenums="1"
    clientes.forEach((cliente, i) => {
        console.log(`${i + 1}. ${cliente.nome}`);
    });
    ```

### `range` — para laços numéricos

```python linenums="1"
# Contar de 0 a 4
for i in range(5):
    print(i)

# Contar de 1 a 5
for i in range(1, 6):
    print(i)

# De 0 a 10, de 2 em 2
for i in range(0, 11, 2):
    print(i)
```

---

## 2. Funções em Python

A filosofia de Python é: **funções pequenas, com responsabilidade única**. Isso vai aparecer muito no DataProcessor.

### Definição básica

=== "Python"

    ```python linenums="1"
    def calcular_media(numeros):
        soma = sum(numeros)
        return soma / len(numeros)
    ```

=== "JavaScript"

    ```javascript linenums="1"
    function calcularMedia(numeros) {
        const soma = numeros.reduce((acc, n) => acc + n, 0);
        return soma / numeros.length;
    }
    ```

!!! tip "Convenção de nomes"

    Em Python, funções e variáveis usam `snake_case` (palavras separadas por underscore). Em JavaScript é `camelCase`. Essa diferença é cultural e você vai ver nos projetos Python que encontrar.

### Parâmetros com valor padrão

```python linenums="1"
def resumo_cliente(cliente, mostrar_email=False):
    linha = f"ID {cliente['id']}: {cliente['nome']} ({cliente['cidade']})"
    if mostrar_email:
        linha += f" — {cliente['email']}"
    return linha

print(resumo_cliente(clientes[0]))
print(resumo_cliente(clientes[0], mostrar_email=True))
```

### Funções que retornam múltiplos valores

Python permite retornar vários valores ao mesmo tempo — isso é chamado de **tuple unpacking**:

```python linenums="1"
def stats_idades(clientes):
    idades = [c["idade"] for c in clientes]
    return min(idades), max(idades), sum(idades) / len(idades)

minimo, maximo, media = stats_idades(clientes)
print(f"Min: {minimo}, Max: {maximo}, Média: {media:.1f}")
```

---

## 3. Funções built-in essenciais

Python tem um conjunto de funções nativas que você vai usar constantemente para trabalhar com dados.

```python linenums="1"
numeros = [34, 28, -5, 45, 38]

print(sum(numeros))    # 140
print(min(numeros))    # -5
print(max(numeros))    # 45
print(len(numeros))    # 5
print(sorted(numeros)) # [-5, 28, 34, 38, 45]
```

### `sorted` com chave de ordenação

Em JavaScript você passa uma função comparadora para `.sort()`. Em Python, você passa uma função `key` para `sorted()`:

=== "Python"

    ```python linenums="1"
    clientes_ordenados = sorted(clientes, key=lambda c: c["idade"])
    ```

=== "JavaScript"

    ```javascript linenums="1"
    clientes.sort((a, b) => a.idade - b.idade);
    ```

Ordem decrescente:

```python linenums="1"
clientes_ordenados = sorted(clientes, key=lambda c: c["idade"], reverse=True)
```

### `filter` e `map`

Python tem as funções `filter()` e `map()`, mas na prática **list comprehensions são mais usadas** porque são mais legíveis:

```python linenums="1"
clientes = [
    {"nome": "João Silva", "idade": 34},
    {"nome": "Maria Souza", "idade": 28},
    {"nome": "Carlos Pereira", "idade": -5},
    {"nome": "Ana Lima", "idade": 45},
    {"nome": "Pedro Santos", "idade": 38},
]

# Filtrar clientes com idade válida (> 0)
validos = [c for c in clientes if c["idade"] > 0]

# Extrair apenas os nomes
nomes = [c["nome"] for c in clientes]

# Combinar: nomes dos clientes válidos
nomes_validos = [c["nome"] for c in clientes if c["idade"] > 0]
```

---

## 4. Agregação de dados

Vamos trabalhar com o dataset completo de clientes — o mesmo da Aula 01, mas agora processando as informações com funções.

```python linenums="1"
clientes = [
    {"id": 1, "nome": "João Silva", "email": "joao.silva@email.com",
     "idade": 34, "cidade": "Joinville"},
    {"id": 2, "nome": "Maria Souza", "email": "maria@email",
     "idade": 28, "cidade": "Florianopolis"},
    {"id": 3, "nome": "Carlos Pereira", "email": "carlos.pereira@email.com",
     "idade": -5, "cidade": "Curitiba"},
    {"id": 4, "nome": "Ana Lima", "email": "ana.lima@email.com",
     "idade": 45, "cidade": "Joinville"},
    {"id": 5, "nome": "Pedro Santos", "email": "",
     "idade": 38, "cidade": "Sao Paulo"},
]
```

### Média de idades — versão ingênua (com bug)

```python linenums="1"
def media_idade(clientes):
    idades = [c["idade"] for c in clientes]
    return sum(idades) / len(idades)

print(media_idade(clientes))
# 28.0 — mas Carlos tem idade -5, que é inválida!
```

Isso está **errado**. A média está sendo calculada com um dado corrompido. É exatamente esse tipo de problema que o DataProcessor deve tratar.

### Média de idades — com tratamento de dados inválidos

```python linenums="1"
def media_idade(clientes):
    idades_validas = [c["idade"] for c in clientes if c["idade"] > 0]

    if not idades_validas:
        return None  # Sem dados válidos para calcular

    return sum(idades_validas) / len(idades_validas)

media = media_idade(clientes)
print(f"Média de idade (dados válidos): {media:.1f}")
# Média de idade (dados válidos): 36.3
```

### Maior e menor idade

```python linenums="1"
def extremos_idade(clientes):
    idades_validas = [c["idade"] for c in clientes if c["idade"] > 0]

    if not idades_validas:
        return None, None

    return min(idades_validas), max(idades_validas)

minimo, maximo = extremos_idade(clientes)
print(f"Menor idade: {minimo} | Maior idade: {maximo}")
# Menor idade: 28 | Maior idade: 45
```

### Contagem por cidade

```python linenums="1"
def contar_por_cidade(clientes):
    contagem = {}
    for cliente in clientes:
        cidade = cliente["cidade"]
        contagem[cidade] = contagem.get(cidade, 0) + 1
    return contagem

resultado = contar_por_cidade(clientes)
for cidade, total in resultado.items():
    print(f"{cidade}: {total}")
```

---

## 5. Trabalhando com transações

Vamos adicionar o segundo dataset ao projeto: as transações.

```python linenums="1"
transacoes = [
    {"id": 1, "cliente_id": 1, "valor": 150.50, "categoria": "eletronicos",
     "data": "2023-05-10", "status": "aprovado"},
    {"id": 2, "cliente_id": 2, "valor": 200.00, "categoria": "roupas",
     "data": "2023-05-11", "status": "pendente"},
    {"id": 3, "cliente_id": 3, "valor": -50.00, "categoria": "alimentacao",
     "data": "2023-05-12", "status": "aprovado"},
    {"id": 4, "cliente_id": 1, "valor": 300.00, "categoria": "eletronicos",
     "data": "2023-05-13", "status": "recusado"},
    {"id": 5, "cliente_id": 10, "valor": 120.00, "categoria": "livros",
     "data": "2023-05-14", "status": "aprovado"},
]
```

!!! warning "Dado inconsistente"

    A transação 3 tem `valor: -50.00` (inválido) e a transação 5 tem `cliente_id: 10` — mas não existe cliente com ID 10 no dataset de clientes. Esses problemas serão tratados na Aula 04.

### Total de vendas aprovadas

```python linenums="1"
def total_aprovado(transacoes):
    return sum(
        t["valor"]
        for t in transacoes
        if t["status"] == "aprovado" and t["valor"] > 0
    )

print(f"Total aprovado: R$ {total_aprovado(transacoes):.2f}")
# Total aprovado: R$ 270.50
```

### Total por categoria

```python linenums="1"
def total_por_categoria(transacoes):
    totais = {}
    for t in transacoes:
        if t["valor"] > 0 and t["status"] == "aprovado":
            cat = t["categoria"]
            totais[cat] = totais.get(cat, 0) + t["valor"]
    return totais

for cat, total in total_por_categoria(transacoes).items():
    print(f"{cat}: R$ {total:.2f}")
```

---

## 6. Aplicação no projeto — DataProcessor

Organize as funções em módulos separados. Crie o arquivo `processador.py`:

```python linenums="1" title="dataprocessor/processador.py"
# processador.py

def media_idade(clientes):
    """Calcula a média de idade ignorando valores inválidos."""
    idades_validas = [c["idade"] for c in clientes if c["idade"] > 0]
    if not idades_validas:
        return None
    return sum(idades_validas) / len(idades_validas)


def extremos_idade(clientes):
    """Retorna (minimo, maximo) das idades válidas."""
    idades_validas = [c["idade"] for c in clientes if c["idade"] > 0]
    if not idades_validas:
        return None, None
    return min(idades_validas), max(idades_validas)


def contar_por_cidade(clientes):
    """Retorna dicionário com contagem de clientes por cidade."""
    contagem = {}
    for cliente in clientes:
        cidade = cliente["cidade"]
        contagem[cidade] = contagem.get(cidade, 0) + 1
    return contagem


def total_aprovado(transacoes):
    """Soma os valores das transações aprovadas com valor positivo."""
    return sum(
        t["valor"]
        for t in transacoes
        if t["status"] == "aprovado" and t["valor"] > 0
    )
```

E no `main.py`, importe e use:

```python linenums="1" title="dataprocessor/main.py"
# main.py
from processador import media_idade, extremos_idade, contar_por_cidade

# ... definição dos clientes ...

media = media_idade(clientes)
minimo, maximo = extremos_idade(clientes)

print(f"Clientes carregados: {len(clientes)}")
print(f"Média de idade: {media:.1f}")
print(f"Faixa de idade: {minimo} – {maximo}")
print()
print("Clientes por cidade:")
for cidade, total in contar_por_cidade(clientes).items():
    print(f"  {cidade}: {total}")
```

---

## Desafio guiado (em sala)

**Métricas do dataset de clientes**

Use o dataset `clientes` hardcoded e implemente as seguintes funções:

1. `media_idade(clientes)` — retorna a média ignorando idades negativas
2. `cliente_mais_novo(clientes)` — retorna o dicionário do cliente com menor idade válida
3. `cliente_mais_velho(clientes)` — retorna o dicionário do cliente com maior idade válida

Ao final, imprima:

```
Média de idade: 36.3
Mais novo: Maria Souza (28 anos)
Mais velho: Ana Lima (45 anos)
```

**Requisitos:**

- Tratar idades inválidas (negativas ou zero)
- Usar funções separadas (não tudo dentro do `main`)
- Não importar nenhuma biblioteca

---

## Desafio extra (para casa)

Usando os dois datasets (`clientes` e `transacoes`):

1. Para cada cliente que tem pelo menos uma transação aprovada, calcule o total gasto
2. Imprima o ranking de clientes por total gasto (do maior para o menor)
3. Formato esperado:

```
Ranking de gastos (transações aprovadas):
1. João Silva — R$ 150.50
2. Pedro Santos — R$ 120.00
```

**Atenção:**

- A transação 5 tem `cliente_id: 10`, que não existe — ignore ela
- A transação 3 tem valor negativo — ignore ela
- Use as funções criadas durante a aula como base
