# Aula 01 — Introdução prática ao Python

## Objetivo

Nesta aula você vai:

- Entender as diferenças práticas entre Python e JavaScript
- Trabalhar com os tipos e estruturas de dados mais usados em Python
- Ter o primeiro contato com o dataset do projeto
- Escrever seu primeiro trecho de código do **DataProcessor**

---

## 1. Python vs JavaScript — o que muda na prática

Você já sabe programar. A questão não é aprender lógica de novo — é mapear o que você já conhece para a sintaxe e filosofia do Python.

### Diferenças imediatas

|                        | JavaScript             | Python                 |
| ---------------------- | ---------------------- | ---------------------- |
| Blocos de código       | `{ }`                  | indentação             |
| Fim de linha           | `;` (opcional)         | nada                   |
| Declaração de variável | `let`, `const`, `var`  | nada (só o nome)       |
| Impressão              | `console.log()`        | `print()`              |
| Tipo nulo              | `null`, `undefined`    | `None`                 |
| Boolean                | `true`, `false`        | `True`, `False`        |
| Comentário             | `// texto`             | `# texto`              |
| String                 | `"texto"` ou `'texto'` | `"texto"` ou `'texto'` |

### Exemplos lado a lado

=== "Python"

    ```python linenums="1"
    # Variáveis
    nome = "João Silva"
    idade = 34

    # Condicional
    if idade >= 18:
        print(nome + " é maior de idade")
    else:
        print(nome + " é menor de idade")

    # Função
    def saudar(nome):
        return "Olá, " + nome
    ```

=== "JavaScript"

    ```javascript linenums="1"
    // Variáveis
    const nome = "João Silva";
    let idade = 34;

    // Condicional
    if (idade >= 18) {
        console.log(nome + " é maior de idade");
    } else {
        console.log(nome + " é menor de idade");
    }

    // Função
    function saudar(nome) {
        return "Olá, " + nome;
    }
    ```

!!! tip "Ponto importante"

    Em Python, **a indentação é obrigatória e faz parte da sintaxe**. Não é estética. Um bloco mal indentado gera erro.

---

## 2. Strings em Python

Python tem interpolação de strings com f-strings — equivalente aos template literals do JS.

=== "Python"

    ```python linenums="1"
    cidade = "Joinville"
    populacao = 600000
    print(f"{cidade} tem {populacao} habitantes")
    ```

=== "JavaScript"

    ```javascript linenums="1"
    const cidade = "Joinville";
    const populacao = 600000;
    console.log(`${cidade} tem ${populacao} habitantes`);
    ```

Você pode fazer operações dentro das chaves:

```python linenums="1"
valor = 150.5
print(f"Valor com desconto: R$ {valor * 0.9:.2f}")
# Valor com desconto: R$ 135.45
```

---

## 3. Listas — o equivalente ao Array

Python usa `list` onde JavaScript usa `Array`. A sintaxe é quase idêntica, mas o comportamento tem diferenças importantes.

```python linenums="1"
# Criação
cidades = ["Joinville", "Florianopolis", "Curitiba", "Sao Paulo"]

# Acesso por índice
print(cidades[0])   # Joinville
print(cidades[-1])  # Sao Paulo (índice negativo = do final)

# Tamanho
print(len(cidades))  # 4

# Adicionar elementos
cidades.append("Porto Alegre")

# Remover
cidades.remove("Curitiba")

# Iterar
for cidade in cidades:
    print(cidade)
```

### Métodos úteis comparados

| Operação           | JavaScript        | Python                       |
| ------------------ | ----------------- | ---------------------------- |
| Adicionar no final | `arr.push(x)`     | `lista.append(x)`            |
| Remover do final   | `arr.pop()`       | `lista.pop()`                |
| Tamanho            | `arr.length`      | `len(lista)`                 |
| Incluir elemento?  | `arr.includes(x)` | `x in lista`                 |
| Filtrar            | `arr.filter(fn)`  | `[x for x in lista if cond]` |
| Mapear             | `arr.map(fn)`     | `[fn(x) for x in lista]`     |

### List comprehension — o mapa/filtro do Python

Essa é uma das features mais características de Python. Em vez de criar um loop para transformar uma lista, você escreve em uma linha:

```python linenums="1"
# Todos os nomes em maiúsculo
nomes = ["João Silva", "Maria Souza", "Carlos Pereira"]

# Jeito verboso (equivalente ao for)
nomes_upper = []
for nome in nomes:
    nomes_upper.append(nome.upper())

# Jeito Pythônico — list comprehension
nomes_upper = [nome.upper() for nome in nomes]

print(nomes_upper)
# ['JOÃO SILVA', 'MARIA SOUZA', 'CARLOS PEREIRA']
```

Filtrando ao mesmo tempo:

```python linenums="1"
idades = [34, 28, -5, 45, 38]

# Apenas idades válidas (maiores que zero)
idades_validas = [idade for idade in idades if idade > 0]
print(idades_validas)
# [34, 28, 45, 38]
```

---

## 4. Dicionários — o equivalente ao Object

Python usa `dict` onde JavaScript usa `Object` (ou `{}`). São pares chave-valor.

```python linenums="1"
# Criação
cliente = {
    "id": 1,
    "nome": "João Silva",
    "email": "joao.silva@email.com",
    "idade": 34,
    "cidade": "Joinville"
}

# Acesso
print(cliente["nome"])       # João Silva
print(cliente.get("email"))  # joao.silva@email.com

# Acesso seguro (sem KeyError)
print(cliente.get("telefone", "não informado"))  # não informado

# Adicionar/atualizar chave
cliente["ativo"] = True

# Remover
del cliente["ativo"]

# Verificar se chave existe
if "email" in cliente:
    print("tem email")

# Iterar sobre chaves e valores
for chave, valor in cliente.items():
    print(f"{chave}: {valor}")
```

### Diferença importante: `.get()` vs `[]`

```python linenums="1"
cliente = {"nome": "João"}

# Isso gera KeyError se a chave não existe:
print(cliente["telefone"])  # KeyError: 'telefone'

# Isso retorna None (ou valor padrão):
print(cliente.get("telefone"))          # None
print(cliente.get("telefone", "N/A"))   # N/A
```

!!! warning "Dado sujo no projeto"

    No dataset `clientes.csv`, o cliente 5 (Pedro Santos) não tem email. Quando você carregar os dados, vai se deparar com esse problema. O `.get()` vai ser seu aliado.

---

## 5. Lista de dicionários — a estrutura base do projeto

Os dados do projeto vão ter **exatamente esse formato**: uma lista onde cada elemento é um dicionário representando um registro.

```python linenums="1"
clientes = [
    {
        "id": 1,
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "idade": 34,
        "cidade": "Joinville",
        "data_cadastro": "2023-01-10"
    },
    {
        "id": 2,
        "nome": "Maria Souza",
        "email": "maria@email",      # email inválido
        "idade": 28,
        "cidade": "Florianopolis",
        "data_cadastro": "2023-02-15"
    },
    {
        "id": 3,
        "nome": "Carlos Pereira",
        "email": "carlos.pereira@email.com",
        "idade": -5,                  # idade inválida
        "cidade": "Curitiba",
        "data_cadastro": "2023-03-20"
    },
    {
        "id": 4,
        "nome": "Ana Lima",
        "email": "ana.lima@email.com",
        "idade": 45,
        "cidade": "Joinville",
        "data_cadastro": "2023-01-25"
    },
    {
        "id": 5,
        "nome": "Pedro Santos",
        "email": "",                  # email vazio
        "idade": 38,
        "cidade": "Sao Paulo",
        "data_cadastro": "2023-02-30" # data inválida
    },
]
```

Observe os problemas nos dados — eles são **propositais**. Parte do trabalho do DataProcessor é identificar e tratar essas inconsistências.

---

## 6. Primeiro acesso aos dados

Agora você já sabe o suficiente para escrever código que lê e inspeciona essa estrutura.

```python linenums="1"
# Imprimir todos os clientes
for cliente in clientes:
    print(f"ID {cliente['id']}: {cliente['nome']} | {cliente['cidade']}")
```

Saída esperada:

```
ID 1: João Silva | Joinville
ID 2: Maria Souza | Florianopolis
ID 3: Carlos Pereira | Curitiba
ID 4: Ana Lima | Joinville
ID 5: Pedro Santos | Sao Paulo
```

Quantos clientes temos?

```python linenums="1"
print(f"Total de clientes: {len(clientes)}")
```

Quais cidades aparecem?

```python linenums="1"
cidades = [cliente["cidade"] for cliente in clientes]
print(cidades)
# ['Joinville', 'Florianopolis', 'Curitiba', 'Joinville', 'Sao Paulo']
```

Cidades únicas:

```python linenums="1"
cidades_unicas = list(set(cidades))
print(cidades_unicas)
```

!!! note "O tipo `set`"

    `set` é uma coleção **sem duplicatas**. Igual ao `Set` do JavaScript. `set(lista)` elimina os valores repetidos.

---

## 7. Aplicação no projeto — DataProcessor

O primeiro passo do projeto é ter os dados em memória para trabalhar. Mesmo antes de ler arquivos CSV (que vem na Aula 03), você vai trabalhar com os dados hardcoded — exatamente como fizemos aqui.

Estrutura inicial do projeto:

```
dataprocessor/
    main.py
    data/
        clientes.csv
        transacoes.csv
        config.json
```

No `main.py`, comece com:

```python linenums="1" title="dataprocessor/main.py"
# main.py

clientes = [
    {"id": 1, "nome": "João Silva", "email": "joao.silva@email.com",
     "idade": 34, "cidade": "Joinville", "data_cadastro": "2023-01-10"},
    {"id": 2, "nome": "Maria Souza", "email": "maria@email",
     "idade": 28, "cidade": "Florianopolis", "data_cadastro": "2023-02-15"},
    {"id": 3, "nome": "Carlos Pereira", "email": "carlos.pereira@email.com",
     "idade": -5, "cidade": "Curitiba", "data_cadastro": "2023-03-20"},
    {"id": 4, "nome": "Ana Lima", "email": "ana.lima@email.com",
     "idade": 45, "cidade": "Joinville", "data_cadastro": "2023-01-25"},
    {"id": 5, "nome": "Pedro Santos", "email": "",
     "idade": 38, "cidade": "Sao Paulo", "data_cadastro": "2023-02-30"},
]

print(f"DataProcessor iniciado — {len(clientes)} clientes carregados.")
```

---

## Desafio guiado (em sala)

**Contar clientes por cidade**

Dado o dataset `clientes` (hardcoded, como definido acima), escreva um programa que:

1. Percorra a lista de clientes
2. Conte quantos clientes existem em cada cidade
3. Imprima o resultado no seguinte formato:

```
Joinville: 2 clientes
Florianopolis: 1 cliente
Curitiba: 1 cliente
Sao Paulo: 1 cliente
```

**Dicas:**

- Use um dicionário para acumular a contagem
- A chave é a cidade, o valor é a quantidade
- `.get()` com valor padrão `0` vai ajudar

??? note "Pista (só olhe se travar)"

    ```python
        contagem = {}
        for cliente in clientes:
            cidade = cliente["cidade"]
            contagem[cidade] = contagem.get(cidade, 0) + 1
    ```

---

## Desafio extra (para casa)

Estenda o desafio guiado:

1. Além de contar, liste **os nomes dos clientes** de cada cidade
2. Ordene o resultado pelo número de clientes (maior para menor)
3. Imprima no formato:

```
Joinville (2): João Silva, Ana Lima
Sao Paulo (1): Pedro Santos
Florianopolis (1): Maria Souza
Curitiba (1): Carlos Pereira
```

**Requisito extra:** use apenas recursos vistos nesta aula — nenhuma biblioteca externa.
