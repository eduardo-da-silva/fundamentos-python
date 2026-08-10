# Aula 08 — Camada core: regras de negócio puras

## Objetivo

Nesta aula você vai:

- Criar a camada `core` para concentrar regras de negócio
- Separar regras puras de detalhes de infraestrutura
- Reaproveitar validação, transformação e métricas sem depender de arquivo/CLI
- Preparar base arquitetural para a camada de `services`
- Manter comportamento funcional idêntico ao pipeline atual

---

## 1. O que é core no contexto deste projeto?

No **DataProcessor**, `core` é o lugar das regras que respondem perguntas de negócio:

- email é válido?
- idade é válida?
- cidade deve ser normalizada como?
- total aprovado deve somar quais transações?

Essas regras não precisam saber:

- de qual arquivo veio o dado
- se a execução foi por CLI ou outro canal
- como o resultado será exibido

!!! tip "Teste mental"

    Se uma função precisa de caminho de arquivo ou `print()` para funcionar,
    ela provavelmente não pertence ao `core`.

---

## 2. Estrutura incremental após esta aula

```text
dataprocessor/
    main.py
    dataprocessor/
        __init__.py
        pipeline.py
        leitor.py
        core/
            __init__.py
            validador.py
            transformador.py
            metricas.py
```

Nesta etapa, ainda vamos manter `pipeline.py` e `leitor.py` fora de `core`.

---

## 3. Extraindo validação para `core`

```python linenums="1" title="dataprocessor/dataprocessor/core/validador.py"
from datetime import date


def email_valido(email):
    if not email or not email.strip():
        return False
    if "@" not in email:
        return False
    partes = email.strip().split("@")
    return len(partes) == 2 and "." in partes[1]


def idade_valida(idade):
    return idade is not None and 0 < idade < 150


def data_valida(texto_data):
    if not texto_data:
        return False
    try:
        date.fromisoformat(texto_data)
        return True
    except ValueError:
        return False


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

    valor_minimo = config.get("valor_minimo", 0)
    valor = transacao.get("valor")
    if valor is None or valor <= valor_minimo:
        erros.append(f"valor inválido: {valor}")

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

---

## 4. Extraindo normalização e métricas para `core`

```python linenums="1" title="dataprocessor/dataprocessor/core/transformador.py"
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

```python linenums="1" title="dataprocessor/dataprocessor/core/metricas.py"
def media_idade(clientes):
    idades_validas = [c["idade"] for c in clientes if c.get("idade") and c["idade"] > 0]
    if not idades_validas:
        return 0
    return sum(idades_validas) / len(idades_validas)


def total_aprovado(transacoes):
    return sum(
        t["valor"]
        for t in transacoes
        if t.get("status") == "aprovado" and t.get("valor", 0) > 0
    )
```

---

## 5. Ajustando o pipeline para usar `core`

```python linenums="1" title="dataprocessor/dataprocessor/pipeline.py"
from .leitor import carregar_clientes, carregar_transacoes, carregar_config
from .core.validador import validar_cliente, validar_transacao, separar_registros
from .core.transformador import transformar_clientes, transformar_transacoes
from .core.metricas import media_idade, total_aprovado


def executar_pipeline(caminho_clientes, caminho_transacoes, caminho_config):
    clientes_raw = carregar_clientes(caminho_clientes)
    transacoes_raw = carregar_transacoes(caminho_transacoes)
    config = carregar_config(caminho_config)

    clientes_validos, clientes_invalidos = separar_registros(
        clientes_raw, validar_cliente
    )
    ids_validos = {c["id"] for c in clientes_validos}

    transacoes_validas, transacoes_invalidas = separar_registros(
        transacoes_raw,
        validar_transacao,
        ids_clientes=ids_validos,
        config=config,
    )

    clientes = transformar_clientes(clientes_validos)
    transacoes = transformar_transacoes(transacoes_validas)

    return {
        "clientes": clientes,
        "transacoes": transacoes,
        "clientes_invalidos": clientes_invalidos,
        "transacoes_invalidas": transacoes_invalidas,
        "metricas": {
            "media_idade": media_idade(clientes),
            "total_aprovado": total_aprovado(transacoes),
        },
    }
```

---

## 6. Comparação com JavaScript

Separar domínio da infraestrutura é o mesmo padrão de projetos Node.js com `domain` e `infra`.

=== "Python"

    ```python linenums="1"
    # core/metricas.py
    def total_aprovado(transacoes):
        return sum(t["valor"] for t in transacoes if t["status"] == "aprovado")
    ```

=== "JavaScript"

    ```javascript linenums="1"
    // domain/metricas.js
    function totalAprovado(transacoes) {
      return transacoes
        .filter((t) => t.status === "aprovado")
        .reduce((acc, t) => acc + t.valor, 0);
    }
    ```

A regra é idêntica. O ganho é estrutural.

---

## 7. Por que essa mudança melhora o software?

- regras de negócio ficam fáceis de localizar
- testes futuros ficam mais baratos (funções puras)
- troca de infraestrutura não exige reescrever regra
- prepara diretamente a criação da camada `services`

!!! note "Base para POO"

    Na próxima fase, classes de serviço podem envolver essas funções de `core` sem duplicar regra.

---

## Desafio guiado (em sala)

**Extrair regras para `core` sem quebrar a execução**

1. Crie `core/validador.py`, `core/transformador.py` e `core/metricas.py`
2. Mova as funções de regra para esses arquivos
3. Atualize `pipeline.py` para importar da camada `core`
4. Rode o projeto e compare métricas com a Aula 07

Critério de aceite:

```text
Clientes válidos: 2
Transações válidas: 2
Média de idade: 39.5
Total aprovado: R$ 150.50
```

---

## Desafio extra (para casa)

Implemente uma nova função de regra em `core/metricas.py`:

```python
def ticket_medio_aprovado(transacoes):
    ...
```

Regras:

- usar apenas transações aprovadas e com valor positivo
- retornar `0` quando não houver transações elegíveis
- não usar leitura de arquivo nem `print()` dentro da função

Depois, mostre esse valor no `main.py` sem criar lógica de cálculo fora do `core`.
