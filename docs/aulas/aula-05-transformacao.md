# Aula 05 — Transformação de dados

## Objetivo

Nesta aula você vai:

- Normalizar strings (maiúsculas, minúsculas, remoção de espaços)
- Padronizar formatos de campos (emails, nomes, cidades)
- Criar funções de limpeza de dados
- Entender a diferença entre dados validados e dados normalizados
- Adicionar a camada de transformação ao **DataProcessor**

---

## 1. Validação vs Transformação

Após a Aula 04, você sabe separar dados válidos de inválidos. Mas um dado que passou na validação ainda pode estar **inconsistente em formato**.

Exemplos:

| Campo original           | Problema              | Esperado                 |
| ------------------------ | --------------------- | ------------------------ |
| `"JOINVILLE"`            | maiúsculas            | `"Joinville"`            |
| `"  Ana Lima  "`         | espaços extras        | `"Ana Lima"`             |
| `"JOAO.SILVA@EMAIL.COM"` | email em maiúsculas   | `"joao.silva@email.com"` |
| `"florianópolis"`        | acento diferente      | `"Florianopolis"`        |
| `"SAO PAULO"`            | forma não padronizada | `"Sao Paulo"`            |

**Validação** responde: "esse dado é aceitável?"  
**Transformação** responde: "como deixar esse dado no formato padrão?"

---

## 2. Métodos de string em Python

Python tem um conjunto rico de métodos nativos para manipulação de strings — sem precisar de bibliotecas externas.

```python linenums="1"
texto = "  João Silva  "

# Remover espaços das extremidades
print(texto.strip())     # "João Silva"
print(texto.lstrip())    # "João Silva  "
print(texto.rstrip())    # "  João Silva"

# Capitalização
print(texto.strip().upper())      # "JOÃO SILVA"
print(texto.strip().lower())      # "joão silva"
print(texto.strip().title())      # "João Silva"
print(texto.strip().capitalize()) # "João silva" (só a primeira letra)
```

!!! warning "`.title()` tem um comportamento curioso"

    `"ANA MARIA lima".title()` retorna `"Ana Maria Lima"` — o que geralmente é o que você quer. Mas `"O'Brien".title()` retorna `"O'Brien"`, que pode quebrar com nomes que têm apóstrofo.

### Verificações úteis

```python linenums="1"
texto = "joao.silva@email.com"

print(texto.startswith("joao"))    # True
print(texto.endswith(".com"))      # True
print("@" in texto)                # True
print(texto.isdigit())             # False
print("34".isdigit())              # True
```

### Substituição e split

```python linenums="1"
cidade = "São Paulo"

# Substituir caractere
normalizada = cidade.replace("ã", "a").replace("ã", "a")
# Resultado: "São Paulo" -> "Sao Paulo" (apenas o 'ã' de 'São')

# Split — dividir string
email = "joao.silva@email.com"
partes = email.split("@")
print(partes)       # ['joao.silva', 'email.com']
print(partes[0])    # 'joao.silva'
print(partes[1])    # 'email.com'

# Join — juntar lista em string
palavras = ["Python", "é", "prático"]
print(" ".join(palavras))   # "Python é prático"
```

---

## 3. Normalização de nomes

O problema de nomes inconsistentes é muito comum em dados reais. Aqui estão os casos mais frequentes:

```python linenums="1"
def normalizar_nome(nome):
    if not nome:
        return ""
    return nome.strip().title()

# Testes
print(normalizar_nome("joão silva"))       # "João Silva"
print(normalizar_nome("MARIA SOUZA"))      # "Maria Souza"
print(normalizar_nome("  ana lima  "))     # "Ana Lima"
print(normalizar_nome("CARLOS pereira"))   # "Carlos Pereira"
```

### Remover caracteres especiais — `unicodedata`

Para normalizar acentos (transformar `ã` em `a`, `é` em `e`, etc.), Python tem o módulo `unicodedata`:

```python linenums="1"
import unicodedata

def remover_acentos(texto):
    # Decompõe caracteres acentuados e remove os marcadores de acento
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

print(remover_acentos("Florianópolis"))  # "Florianopolis"
print(remover_acentos("João"))           # "Joao"
print(remover_acentos("São Paulo"))      # "Sao Paulo"
```

!!! note "Quando remover acentos?"

    Não remova acentos dos nomes das pessoas — isso é incorreto e desrespeitoso. Remova apenas em campos que precisam de padronização técnica, como slugs, identificadores ou cidades que serão usadas como chave de agrupamento.

---

## 4. Normalização de emails

```python linenums="1"
def normalizar_email(email):
    if not email:
        return ""
    return email.strip().lower()

print(normalizar_email("JOAO.SILVA@EMAIL.COM"))  # "joao.silva@email.com"
print(normalizar_email("  Maria@Email.com  "))   # "maria@email.com"
```

---

## 5. Normalização de cidades

No nosso dataset, cidades podem vir com capitalização inconsistente, acentos diferentes ou espaços extras.

```python linenums="1"
import unicodedata

def remover_acentos(texto):
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def normalizar_cidade(cidade):
    if not cidade:
        return ""
    sem_espacos = cidade.strip()
    sem_acentos = remover_acentos(sem_espacos)
    return sem_acentos.title()

print(normalizar_cidade("florianópolis"))   # "Florianopolis"
print(normalizar_cidade("SÃO PAULO"))       # "Sao Paulo"
print(normalizar_cidade("  joinville  "))   # "Joinville"
print(normalizar_cidade("CURITIBA"))        # "Curitiba"
```

---

## 6. Transformando um registro completo

Agora combinamos as funções para normalizar um cliente inteiro. Importante: transformação não altera os dados originais — ela cria um **novo dicionário** normalizado.

```python linenums="1"
def transformar_cliente(cliente):
    return {
        "id": cliente["id"],
        "nome": normalizar_nome(cliente.get("nome", "")),
        "email": normalizar_email(cliente.get("email", "")),
        "idade": cliente["idade"],
        "cidade": normalizar_cidade(cliente.get("cidade", "")),
        "data_cadastro": cliente.get("data_cadastro", ""),
    }

# Exemplo
cliente_original = {
    "id": 2,
    "nome": "  MARIA SOUZA  ",
    "email": "MARIA@email",
    "idade": 28,
    "cidade": "florianópolis",
    "data_cadastro": "2023-02-15"
}

cliente_normalizado = transformar_cliente(cliente_original)
print(cliente_normalizado)
# {'id': 2, 'nome': 'Maria Souza', 'email': 'maria@email',
#  'idade': 28, 'cidade': 'Florianopolis', 'data_cadastro': '2023-02-15'}
```

### Transformando uma lista inteira

```python linenums="1"
def transformar_clientes(clientes):
    return [transformar_cliente(c) for c in clientes]
```

---

## 7. Transformando transações

Para transações, a normalização é mais simples — os campos de texto precisam de `.strip().lower()`:

```python linenums="1"
def transformar_transacao(transacao):
    return {
        "id": transacao["id"],
        "cliente_id": transacao["cliente_id"],
        "valor": transacao["valor"],
        "categoria": transacao.get("categoria", "").strip().lower(),
        "data": transacao.get("data", "").strip(),
        "status": transacao.get("status", "").strip().lower(),
    }
```

---

## 8. O pipeline completo

Agora o DataProcessor tem um pipeline bem definido:

```
Arquivos de dados
      │
      ▼
   [LEITURA]     → carregar_clientes(), carregar_transacoes(), carregar_config()
      │
      ▼
[VALIDAÇÃO]     → separar_registros(), validar_cliente(), validar_transacao()
      │
      ▼
[TRANSFORMAÇÃO] → transformar_clientes(), transformar_transacoes()
      │
      ▼
   [SAÍDA]       → relatórios, arquivos CSV/JSON, logs
```

---

## 9. Aplicação no projeto — DataProcessor

Crie o arquivo `transformador.py`:

```python linenums="1" title="dataprocessor/transformador.py"
# transformador.py
import unicodedata


def _remover_acentos(texto):
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalizar_nome(nome):
    if not nome:
        return ""
    return nome.strip().title()


def normalizar_email(email):
    if not email:
        return ""
    return email.strip().lower()


def normalizar_cidade(cidade):
    if not cidade:
        return ""
    return _remover_acentos(cidade.strip()).title()


def transformar_cliente(cliente):
    return {
        "id": cliente["id"],
        "nome": normalizar_nome(cliente.get("nome", "")),
        "email": normalizar_email(cliente.get("email", "")),
        "idade": cliente["idade"],
        "cidade": normalizar_cidade(cliente.get("cidade", "")),
        "data_cadastro": cliente.get("data_cadastro", "").strip(),
    }


def transformar_transacao(transacao):
    return {
        "id": transacao["id"],
        "cliente_id": transacao["cliente_id"],
        "valor": transacao["valor"],
        "categoria": transacao.get("categoria", "").strip().lower(),
        "data": transacao.get("data", "").strip(),
        "status": transacao.get("status", "").strip().lower(),
    }


def transformar_clientes(clientes):
    return [transformar_cliente(c) for c in clientes]


def transformar_transacoes(transacoes):
    return [transformar_transacao(t) for t in transacoes]
```

`main.py` atualizado com o pipeline completo:

```python linenums="1" title="dataprocessor/main.py"
# main.py
from leitor import carregar_clientes, carregar_transacoes, carregar_config
from validador import validar_cliente, validar_transacao, separar_registros
from transformador import transformar_clientes, transformar_transacoes

# --- LEITURA ---
clientes_raw = carregar_clientes("data/clientes.csv")
transacoes_raw = carregar_transacoes("data/transacoes.csv")
config = carregar_config("data/config.json")

# --- VALIDAÇÃO ---
clientes_validos, clientes_invalidos = separar_registros(
    clientes_raw, validar_cliente
)
ids_validos = {c["id"] for c in clientes_validos}

transacoes_validas, transacoes_invalidas = separar_registros(
    transacoes_raw, validar_transacao,
    ids_clientes=ids_validos, config=config
)

# --- TRANSFORMAÇÃO ---
clientes = transformar_clientes(clientes_validos)
transacoes = transformar_transacoes(transacoes_validas)

# --- RESUMO ---
print("=== DataProcessor ===")
print(f"Clientes: {len(clientes)} válidos, {len(clientes_invalidos)} inválidos")
print(f"Transações: {len(transacoes)} válidas, {len(transacoes_invalidas)} inválidas")
print()
print("Clientes normalizados:")
for c in clientes:
    print(f"  {c['nome']} | {c['email']} | {c['cidade']}")
```

Estrutura do projeto ao final desta aula:

```
dataprocessor/
    main.py
    leitor.py
    processador.py
    validador.py
    transformador.py
    data/
        clientes.csv
        transacoes.csv
        config.json
```

---

## Desafio guiado (em sala)

**Padronizar nomes, emails e cidades**

1. Implemente `normalizar_nome()`, `normalizar_email()` e `normalizar_cidade()` conforme a aula
2. Crie `transformar_cliente(cliente)` que retorna um novo dicionário normalizado
3. Aplique nos clientes **válidos** (resultado da validação da Aula 04)
4. Compare antes e depois:

```
=== TRANSFORMAÇÃO ===

ANTES:
  nome: "  JOÃO SILVA  " | email: "Joao.Silva@Email.com" | cidade: "JOINVILLE"

DEPOIS:
  nome: "João Silva" | email: "joao.silva@email.com" | cidade: "Joinville"
```

Faça isso para os 2 clientes válidos do dataset.

---

## Desafio extra (para casa)

Implemente o pipeline completo no `main.py`:

1. Leitura dos 3 arquivos
2. Validação de clientes e transações
3. Transformação dos registros válidos
4. Geração do seguinte relatório final:

```
=== RELATÓRIO FINAL — DataProcessor ===

CLIENTES PROCESSADOS (2 válidos de 5)
  ID 1 | João Silva | joao.silva@email.com | 34 anos | Joinville
  ID 4 | Ana Lima | ana.lima@email.com | 45 anos | Joinville

CLIENTES REJEITADOS (3)
  ID 2 — Maria Souza: email inválido: 'maria@email'
  ID 3 — Carlos Pereira: idade inválida: -5
  ID 5 — Pedro Santos: email inválido: '', data inválida: '2023-02-30'

TRANSAÇÕES PROCESSADAS (2 válidas de 5)
  ID 1 | cliente 1 | R$ 150.50 | eletronicos | aprovado
  ID 2 | cliente 2 | R$ 200.00 | roupas | pendente

TRANSAÇÕES REJEITADAS (3)
  ID 3 — valor inválido: -50.0
  ID 4 — cliente rejeitado (ID 3 inválido)
  ID 5 — cliente_id inexistente: 10

MÉTRICAS
  Total aprovado: R$ 150.50
  Média de idade (válidos): 39.5
```

**Todas as funções devem estar em arquivos separados** (`leitor.py`, `validador.py`, `transformador.py`).
