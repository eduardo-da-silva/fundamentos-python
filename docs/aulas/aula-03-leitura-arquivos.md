# Aula 03 — Leitura de arquivos

## Objetivo

Nesta aula você vai:

- Ler arquivos CSV usando o módulo `csv` da biblioteca padrão
- Ler arquivos JSON usando o módulo `json`
- Converter dados lidos do disco para listas de dicionários
- Substituir os dados hardcoded do projeto por leitura real de arquivos

A partir desta aula, o **DataProcessor** começa a funcionar de verdade.

---

## 1. O módulo `csv`

Python tem suporte nativo a CSV — sem precisar instalar nada. O módulo `csv` da biblioteca padrão faz o parsing.

### Criando o arquivo de dados

Antes de rodar os exemplos, crie o arquivo `data/clientes.csv` com este conteúdo:

```csv linenums="1"
id,nome,email,idade,cidade,data_cadastro
1,João Silva,joao.silva@email.com,34,Joinville,2023-01-10
2,Maria Souza,maria@email,28,Florianopolis,2023-02-15
3,Carlos Pereira,carlos.pereira@email.com,-5,Curitiba,2023-03-20
4,Ana Lima,ana.lima@email.com,45,Joinville,2023-01-25
5,Pedro Santos,,38,Sao Paulo,2023-02-30
```

### Leitura básica com `csv.reader`

```python linenums="1"
import csv

with open("data/clientes.csv", encoding="utf-8") as arquivo:
    leitor = csv.reader(arquivo)
    for linha in leitor:
        print(linha)
```

Saída:

```
['id', 'nome', 'email', 'idade', 'cidade', 'data_cadastro']
['1', 'João Silva', 'joao.silva@email.com', '34', 'Joinville', '2023-01-10']
['2', 'Maria Souza', 'maria@email', '28', 'Florianopolis', '2023-02-15']
...
```

O `csv.reader` retorna **listas**. Cada elemento é uma string. Note dois pontos importantes:

- A primeira linha é o cabeçalho — você precisa pular ou tratar separadamente
- `34` vem como `'34'` (string), não como número

### Leitura com `csv.DictReader` — a forma correta para o projeto

`DictReader` faz o mapeamento automático do cabeçalho para as chaves do dicionário:

```python linenums="1"
import csv

with open("data/clientes.csv", encoding="utf-8") as arquivo:
    leitor = csv.DictReader(arquivo)
    for linha in leitor:
        print(dict(linha))
```

Saída:

```python
{'id': '1', 'nome': 'João Silva', 'email': 'joao.silva@email.com', 'idade': '34', 'cidade': 'Joinville', 'data_cadastro': '2023-01-10'}
{'id': '2', 'nome': 'Maria Souza', 'email': 'maria@email', 'idade': '28', 'cidade': 'Florianopolis', 'data_cadastro': '2023-02-15'}
...
```

Agora temos dicionários com as chaves certas. Mas os valores ainda são **strings**.

### Carregar em uma lista

```python linenums="1"
import csv

def carregar_clientes(caminho):
    clientes = []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            clientes.append(dict(linha))
    return clientes

clientes = carregar_clientes("data/clientes.csv")
print(f"{len(clientes)} clientes carregados.")
```

---

## 2. Conversão de tipos

Dados de CSV chegam como strings. Você precisa converter para os tipos corretos.

```python linenums="1"
linha = {'id': '1', 'nome': 'João Silva', 'idade': '34'}

# Conversão manual
cliente = {
    "id": int(linha["id"]),
    "nome": linha["nome"],
    "idade": int(linha["idade"]),
}
```

### O problema da conversão — dados sujos

E se a idade for inválida? Isso acontece no nosso dataset:

```python
int("-5")   # funciona: -5
int("")     # ValueError!
int("abc")  # ValueError!
```

Precisamos converter com segurança:

```python linenums="1"
def converter_inteiro(valor, padrao=None):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return padrao

print(converter_inteiro("34"))   # 34
print(converter_inteiro(""))     # None
print(converter_inteiro("abc"))  # None
print(converter_inteiro("-5"))   # -5
```

!!! note "Por que `None` como padrão?"

    `None` é o equivalente a "sem valor" em Python. É diferente de `0`. Uma idade `None` significa que o dado não veio — é um dado ausente. Uma idade `0` seria um valor (incorreto, mas presente).

### Função de carregamento com conversão

```python linenums="1"
import csv

def carregar_clientes(caminho):
    def converter_inteiro(v, pad=None):
        try:
            return int(v)
        except (ValueError, TypeError):
            return pad

    clientes = []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            cliente = {
                "id": converter_inteiro(linha["id"]),
                "nome": linha["nome"].strip(),
                "email": linha["email"].strip(),
                "idade": converter_inteiro(linha["idade"]),
                "cidade": linha["cidade"].strip(),
                "data_cadastro": linha["data_cadastro"].strip(),
            }
            clientes.append(cliente)
    return clientes
```

`.strip()` remove espaços em branco extras — problema frequente em CSVs reais.

---

## 3. Lendo JSON com o módulo `json`

JSON é mais direto que CSV — o módulo `json` converte automaticamente os tipos quando possível.

### O arquivo `config.json`

Crie o arquivo `data/config.json`:

```json linenums="1"
{
  "categorias_validas": ["eletronicos", "roupas", "alimentacao", "livros"],
  "status_validos": ["aprovado", "pendente", "recusado"],
  "valor_minimo": 0
}
```

### Leitura básica

```python linenums="1"
import json

with open("data/config.json", encoding="utf-8") as arquivo:
    config = json.load(arquivo)

print(config)
print(type(config))                        # <class 'dict'>
print(config["categorias_validas"])        # ['eletronicos', 'roupas', ...]
print(config["valor_minimo"])              # 0 (int, não string)
```

!!! tip "JSON vs CSV"

    Com JSON, os tipos são preservados — `0` continua sendo `int`, `true` vira `True`, listas viram `list`. Com CSV, tudo vira `str` e você precisa converter manualmente.

### Função de carregamento

```python linenums="1"
import json

def carregar_config(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)

config = carregar_config("data/config.json")
print(f"Categorias válidas: {config['categorias_validas']}")
```

---

## 4. Lendo as transações

Crie o arquivo `data/transacoes.csv`:

```csv linenums="1"
id,cliente_id,valor,categoria,data,status
1,1,150.50,eletronicos,2023-05-10,aprovado
2,2,200.00,roupas,2023-05-11,pendente
3,3,-50.00,alimentacao,2023-05-12,aprovado
4,1,300.00,eletronicos,2023-05-13,recusado
5,10,120.00,livros,2023-05-14,aprovado
```

Aqui temos `valor` como `float`. A conversão precisa tratar isso:

```python linenums="1"
import csv

def carregar_transacoes(caminho):
    def para_int(v, pad=None):
        try:
            return int(v)
        except (ValueError, TypeError):
            return pad

    def para_float(v, pad=None):
        try:
            return float(v)
        except (ValueError, TypeError):
            return pad

    transacoes = []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            transacao = {
                "id": para_int(linha["id"]),
                "cliente_id": para_int(linha["cliente_id"]),
                "valor": para_float(linha["valor"]),
                "categoria": linha["categoria"].strip(),
                "data": linha["data"].strip(),
                "status": linha["status"].strip(),
            }
            transacoes.append(transacao)
    return transacoes
```

---

## 5. Tratando arquivo não encontrado

O DataProcessor vai rodar via linha de comando. Se o arquivo não existir, o programa não pode travar sem uma mensagem útil.

```python linenums="1"
import csv
import os

def carregar_clientes(caminho):
    if not os.path.exists(caminho):
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return []

    clientes = []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            # ... conversão ...
            clientes.append(dict(linha))
    return clientes
```

---

## 6. Aplicação no projeto — DataProcessor

Agora o projeto deixa de ter dados hardcoded. Crie o arquivo `leitor.py`:

```python linenums="1" title="dataprocessor/leitor.py"
# leitor.py
import csv
import json
import os


def _para_int(valor, padrao=None):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return padrao


def _para_float(valor, padrao=None):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return padrao


def carregar_clientes(caminho):
    if not os.path.exists(caminho):
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return []

    clientes = []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            clientes.append({
                "id": _para_int(linha["id"]),
                "nome": linha["nome"].strip(),
                "email": linha["email"].strip(),
                "idade": _para_int(linha["idade"]),
                "cidade": linha["cidade"].strip(),
                "data_cadastro": linha["data_cadastro"].strip(),
            })
    return clientes


def carregar_transacoes(caminho):
    if not os.path.exists(caminho):
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return []

    transacoes = []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            transacoes.append({
                "id": _para_int(linha["id"]),
                "cliente_id": _para_int(linha["cliente_id"]),
                "valor": _para_float(linha["valor"]),
                "categoria": linha["categoria"].strip(),
                "data": linha["data"].strip(),
                "status": linha["status"].strip(),
            })
    return transacoes


def carregar_config(caminho):
    if not os.path.exists(caminho):
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return {}

    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)
```

Atualize o `main.py`:

```python linenums="1" title="dataprocessor/main.py"
# main.py
from leitor import carregar_clientes, carregar_transacoes, carregar_config

clientes = carregar_clientes("data/clientes.csv")
transacoes = carregar_transacoes("data/transacoes.csv")
config = carregar_config("data/config.json")

print(f"Clientes carregados: {len(clientes)}")
print(f"Transações carregadas: {len(transacoes)}")
print(f"Configuração: {config}")
```

Estrutura do projeto agora:

```
dataprocessor/
    main.py
    leitor.py
    processador.py
    data/
        clientes.csv
        transacoes.csv
        config.json
```

---

## Desafio guiado (em sala)

**Carregar e exibir os dados**

1. Crie os três arquivos de dados (`clientes.csv`, `transacoes.csv`, `config.json`) na pasta `data/`
2. Implemente `carregar_clientes()` que lê o CSV e retorna uma lista de dicionários com tipos corretos (`id` como `int`, `idade` como `int`)
3. Imprima os dados no seguinte formato:

```
=== CLIENTES ===
ID 1 | João Silva | joao.silva@email.com | 34 anos | Joinville
ID 2 | Maria Souza | maria@email | 28 anos | Florianopolis
ID 3 | Carlos Pereira | carlos.pereira@email.com | -5 anos | Curitiba
ID 4 | Ana Lima | ana.lima@email.com | 45 anos | Joinville
ID 5 | Pedro Santos |  | 38 anos | Sao Paulo
```

**Dica:** o campo `email` do cliente 5 chega vazio do CSV — trate isso com `.strip()` e exiba como está.

---

## Desafio extra (para casa)

Leia os três arquivos e gere um relatório inicial:

```
=== RELATÓRIO INICIAL ===
Clientes carregados: 5
Transações carregadas: 5
Configuração carregada: OK

Categorias configuradas: eletronicos, roupas, alimentacao, livros
Status configurados: aprovado, pendente, recusado

Clientes por cidade:
  Joinville: 2
  Florianopolis: 1
  Curitiba: 1
  Sao Paulo: 1

Transações por status:
  aprovado: 3
  pendente: 1
  recusado: 1
```

Tudo deve ser gerado dinamicamente a partir dos arquivos — nenhum valor hardcoded.
