# Aula 09 — Camada services: casos de uso e orquestração

## Objetivo

Nesta aula você vai:

- Criar a camada `services` para organizar casos de uso
- Separar fluxo de processamento (orquestração) das regras do `core`
- Isolar infraestrutura de leitura de dados em um pacote próprio
- Deixar `main.py` como adaptador de entrada/saída
- Consolidar um pipeline com fronteiras claras

---

## 1. De core para services: o próximo passo natural

Após a Aula 08, já temos regras puras em `core`. Agora falta separar melhor **fluxo de aplicação**:

- ler dados
- validar
- transformar
- calcular métricas
- devolver resultado final

Isso é caso de uso. E caso de uso pertence à camada `services`.

!!! tip "Resumo rápido"

    `core` responde "como calcular/validar".
    `services` responde "em que ordem executar".

---

## 2. Estrutura incremental desta aula

```text
dataprocessor/
    main.py
    dataprocessor/
        __init__.py
        core/
            __init__.py
            validacao.py
            normalizacao.py
            metricas.py
        infra/
            __init__.py
            arquivos.py
        services/
            __init__.py
            processamento_service.py
```

Perceba que agora existe separação explícita entre regras de negócio e infraestrutura.

---

## 3. Camada de infraestrutura

A leitura de CSV/JSON sai de módulo genérico e vai para `infra/arquivos.py`:

```python linenums="1" title="dataprocessor/dataprocessor/infra/arquivos.py"
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
        return {}

    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)
```

---

## 4. Camada services (caso de uso)

```python linenums="1" title="dataprocessor/dataprocessor/services/processamento_service.py"
from ..infra.arquivos import carregar_clientes, carregar_transacoes, carregar_config
from ..core.validacao import validar_cliente, validar_transacao, separar_registros
from ..core.normalizacao import transformar_clientes, transformar_transacoes
from ..core.metricas import media_idade, total_aprovado


def executar_processamento(caminho_clientes, caminho_transacoes, caminho_config):
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

Agora a antiga lógica de `pipeline.py` está modelada como serviço de aplicação.

---

## 5. `main.py` como adaptador fino

```python linenums="1" title="dataprocessor/main.py"
from dataprocessor.services.processamento_service import executar_processamento


def main():
    resultado = executar_processamento(
        "data/clientes.csv",
        "data/transacoes.csv",
        "data/config.json",
    )

    print("=== DataProcessor CLI ===")
    print(f"Clientes válidos: {len(resultado['clientes'])}")
    print(f"Clientes inválidos: {len(resultado['clientes_invalidos'])}")
    print(f"Transações válidas: {len(resultado['transacoes'])}")
    print(f"Transações inválidas: {len(resultado['transacoes_invalidas'])}")
    print(f"Média de idade: {resultado['metricas']['media_idade']:.1f}")
    print(f"Total aprovado: R$ {resultado['metricas']['total_aprovado']:.2f}")


if __name__ == "__main__":
    main()
```

---

## 6. Comparação com JavaScript

Esse desenho é equivalente a uma arquitetura com `services` em Node.js.

=== "Python"

    ```python linenums="1"
    from dataprocessor.services.processamento_service import executar_processamento
    resultado = executar_processamento("data/clientes.csv", "data/transacoes.csv", "data/config.json")
    ```

=== "JavaScript"

    ```javascript linenums="1"
    const { executarProcessamento } = require("./services/processamentoService");
    const resultado = executarProcessamento("data/clientes.csv", "data/transacoes.csv", "data/config.json");
    ```

A ideia é a mesma: centralizar caso de uso em serviço reaproveitável.

---

## 7. Por que essa mudança melhora o software?

- fluxo completo fica em um ponto previsível (`services`)
- `main.py` para de concentrar decisão de negócio
- infraestrutura fica substituível (arquivo hoje, outro adapter amanhã)
- prepara terreno para introduzir classes de serviço na fase de POO

!!! note "Sem alterar comportamento"

    A ordem do pipeline e as regras continuam as mesmas.
    O que mudou foi a distribuição de responsabilidade.

---

## Desafio guiado (em sala)

**Criar a camada services no DataProcessor**

1. Crie `infra/arquivos.py` com as funções de leitura
2. Crie `services/processamento_service.py` com `executar_processamento()`
3. Atualize `main.py` para chamar o serviço
4. Execute e valide que os números finais continuam iguais

Saída mínima esperada:

```text
Clientes válidos: 2
Clientes inválidos: 3
Transações válidas: 2
Transações inválidas: 3
```

---

## Desafio extra (para casa)

Implemente um segundo caso de uso no mesmo módulo de services:

```python
def executar_validacao_apenas(caminho_clientes, caminho_transacoes, caminho_config):
    ...
```

Esse caso de uso deve:

- ler os mesmos arquivos
- validar clientes e transações
- não transformar
- não calcular métricas

Reflexão:

- qual camada muda quando o produto pede um novo fluxo de negócio?
