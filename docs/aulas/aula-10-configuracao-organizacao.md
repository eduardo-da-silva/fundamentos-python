# Aula 10 — Configuração do projeto e organização final (pré-POO)

## Objetivo

Nesta aula você vai:

- Centralizar configurações de execução do DataProcessor
- Separar parâmetros de ambiente de regras de negócio
- Consolidar a arquitetura final do Módulo 5
- Fechar o projeto com comportamento funcional idêntico
- Preparar base para introdução de POO no próximo módulo

---

## 1. Problema atual: configuração espalhada

Mesmo com `core`, `infra` e `services`, ainda existe um ponto comum de dor:

- caminhos de arquivos hardcoded
- defaults distribuídos em múltiplos módulos
- dificuldade para trocar ambiente (`dev`, `teste`, `produção`)

!!! warning "Cheiro de arquitetura"

    Configuração espalhada aumenta risco de inconsistência.
    Um projeto organizado precisa de um lugar único para configuração.

---

## 2. Criando um módulo de configuração

Vamos centralizar isso em `dataprocessor/config.py`.

```python linenums="1" title="dataprocessor/dataprocessor/config.py"
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    caminho_clientes: str
    caminho_transacoes: str
    caminho_config: str


def carregar_configuracao_padrao():
    return AppConfig(
        caminho_clientes="data/clientes.csv",
        caminho_transacoes="data/transacoes.csv",
        caminho_config="data/config.json",
    )
```

Por que `@dataclass(frozen=True)`?

- facilita leitura e autocomplete
- evita mutação acidental durante execução
- mantém contrato explícito de parâmetros

---

## 3. Ajustando service para receber configuração

```python linenums="1" title="dataprocessor/dataprocessor/services/processamento.py"
from ..infra.arquivos import carregar_clientes, carregar_transacoes, carregar_config
from ..core.validador import validar_cliente, validar_transacao, separar_registros
from ..core.transformador import transformar_clientes, transformar_transacoes
from ..core.metricas import media_idade, total_aprovado


def executar_processamento(app_config):
    clientes_raw = carregar_clientes(app_config.caminho_clientes)
    transacoes_raw = carregar_transacoes(app_config.caminho_transacoes)
    config_negocio = carregar_config(app_config.caminho_config)

    clientes_validos, clientes_invalidos = separar_registros(
        clientes_raw, validar_cliente
    )
    ids_validos = {c["id"] for c in clientes_validos}

    transacoes_validas, transacoes_invalidas = separar_registros(
        transacoes_raw,
        validar_transacao,
        ids_clientes=ids_validos,
        config=config_negocio,
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

Agora o serviço recebe dependências de execução por contrato, não por string hardcoded.

---

## 4. `main.py` final do módulo

```python linenums="1" title="dataprocessor/main.py"
from dataprocessor.config import carregar_configuracao_padrao
from dataprocessor.services.processamento import executar_processamento


def main():
    app_config = carregar_configuracao_padrao()
    resultado = executar_processamento(app_config)

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

## 5. Comparação com JavaScript

Centralizar configuração é um padrão universal.

=== "Python"

    ```python linenums="1"
    from dataprocessor.config import carregar_configuracao_padrao

    cfg = carregar_configuracao_padrao()
    ```

=== "JavaScript"

    ```javascript linenums="1"
    const cfg = {
      caminhoClientes: "data/clientes.csv",
      caminhoTransacoes: "data/transacoes.csv",
      caminhoConfig: "data/config.json",
    };
    ```

No Python, `dataclass` dá contrato forte sem custo alto de complexidade.

---

## 6. Organização final do Módulo 5

```text
dataprocessor/
    main.py
    dataprocessor/
        __init__.py
        config.py
        core/
            __init__.py
            validador.py
            transformador.py
            metricas.py
        infra/
            __init__.py
            arquivos.py
        services/
            __init__.py
            processamento.py
    data/
        clientes.csv
        transacoes.csv
        config.json
```

### Mapa de camadas

| Camada      | Responsabilidade                                    | Depende de |
| ----------- | --------------------------------------------------- | ---------- |
| `core`      | Regras de negócio puras                             | ninguém    |
| `infra`     | Leitura de arquivos e acesso a recursos externos    | biblioteca padrão |
| `services`  | Orquestra casos de uso combinando core + infra      | `core`, `infra` |
| `main.py`   | Entrada da aplicação (CLI)                          | `services`, `config` |

!!! note "Preparação para POO"

    O próximo passo natural é transformar serviços e adaptadores em classes.
    Como as responsabilidades já estão separadas, a migração para POO vira evolução suave.

---

## 7. Por que essa mudança melhora o software?

- parâmetros de execução deixam de ficar espalhados
- mudança de ambiente vira troca de configuração, não edição de regra
- camadas ficam explícitas para o time
- projeto fica pronto para crescimento sem "big rewrite"

---

## Desafio guiado (em sala)

**Consolidar configuração e arquitetura final**

1. Crie `config.py` com `AppConfig` e `carregar_configuracao_padrao()`
2. Atualize `executar_processamento()` para receber `app_config`
3. Atualize `main.py` para montar configuração e chamar service
4. Execute e confirme que os resultados finais continuam iguais

Resumo esperado:

```text
Clientes válidos: 2
Clientes inválidos: 3
Transações válidas: 2
Transações inválidas: 3
Média de idade: 39.5
Total aprovado: R$ 150.50
```

---

## Desafio extra (para casa)

Implemente suporte a argumentos opcionais de linha de comando para sobrescrever os caminhos padrão sem mudar as camadas existentes.

Requisitos:

1. criar função `carregar_configuracao_cli()`
2. fallback para `carregar_configuracao_padrao()`
3. não mover regra de negócio para `main.py`

Pergunta final do módulo:

- se amanhã o DataProcessor precisar rodar por agendamento e por API, quais camadas são reaproveitadas sem alteração?
