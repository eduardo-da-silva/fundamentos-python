# Aula 07 — Packages e estratégia de imports

## Objetivo

Nesta aula você vai:

- Evoluir o projeto de "pasta de scripts" para **package Python**
- Entender quando usar imports absolutos e relativos
- Evitar erros comuns de organização (principalmente import circular)
- Reorganizar o DataProcessor em etapas pequenas e seguras
- Manter o mesmo comportamento funcional após a migração

---

## 1. Por que transformar em package?

Enquanto o projeto é pequeno, rodar arquivos soltos funciona. Quando ele cresce, começam os sintomas:

- imports quebrando dependendo do diretório de execução
- dificuldade de reutilizar código em outro entrypoint
- organização inconsistente entre times e ambientes

Package resolve isso porque estabelece fronteiras e namespace.

!!! tip "Regra prática"

    Se você já tem 5+ módulos que se importam entre si, já vale organizar como package.

---

## 2. Estrutura antes e depois

### Antes (scripts no mesmo nível)

```text
dataprocessor/
    main.py
    pipeline.py
    leitor.py
    validador.py
    transformador.py
    processador.py
```

### Depois (package explícito)

```text
dataprocessor/
    main.py
    dataprocessor/
        __init__.py
        pipeline.py
        leitor.py
        validador.py
        transformador.py
        processador.py
    data/
        clientes.csv
        transacoes.csv
        config.json
```

### O papel do `__init__.py`

Arquivo mínimo:

```python linenums="1" title="dataprocessor/dataprocessor/__init__.py"
"""Package principal do DataProcessor CLI."""
```

Com isso, Python reconhece a pasta como package e você ganha imports previsíveis.

---

## 3. Imports absolutos vs relativos

### Import absoluto (preferência em projeto maior)

```python linenums="1"
from dataprocessor.leitor import carregar_clientes
from dataprocessor.validador import validar_cliente
```

Vantagens:

- deixa explícito de onde vem o módulo
- facilita navegação no editor
- reduz ambiguidade quando o projeto cresce

### Import relativo (útil dentro do package)

```python linenums="1"
from .leitor import carregar_clientes
from .validador import validar_cliente
```

Vantagens:

- reduz repetição de prefixo longo
- funciona bem em módulo interno do mesmo package

Desvantagem:

- pode confundir iniciante quando há muitos níveis (`..`, `...`)

!!! note "Padrão recomendado para este módulo"

    Dentro do package, use import relativo simples (`from .x import y`) quando o módulo está no mesmo nível.
    No ponto de entrada (`main.py`), use import absoluto.

---

## 4. Comparação com JavaScript

A motivação é a mesma do Node.js quando você sai de arquivos soltos para estrutura modular.

=== "Python"

    ```python linenums="1"
    from dataprocessor.pipeline import executar_pipeline
    ```

=== "JavaScript"

    ```javascript linenums="1"
    const { executarPipeline } = require("./src/pipeline");
    ```

A diferença é que no Python o conceito de package é parte central da resolução de imports.

---

## 5. Aplicação no DataProcessor

### `pipeline.py` dentro do package

```python linenums="1" title="dataprocessor/dataprocessor/pipeline.py"
from .leitor import carregar_clientes, carregar_transacoes, carregar_config
from .validador import validar_cliente, validar_transacao, separar_registros
from .transformador import transformar_clientes, transformar_transacoes
from .processador import media_idade, total_aprovado


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

### `main.py` apontando para o package

```python linenums="1" title="dataprocessor/main.py"
from dataprocessor.pipeline import executar_pipeline


def main():
    resultado = executar_pipeline(
        "data/clientes.csv",
        "data/transacoes.csv",
        "data/config.json",
    )

    print("=== DataProcessor ===")
    print(f"Clientes válidos: {len(resultado['clientes'])}")
    print(f"Transações válidas: {len(resultado['transacoes'])}")
    print(f"Total aprovado: R$ {resultado['metricas']['total_aprovado']:.2f}")


if __name__ == "__main__":
    main()
```

### Execução

```bash
cd dataprocessor
python main.py
```

---

## 6. Erro clássico: import circular

Exemplo de problema:

- `pipeline.py` importa `validador.py`
- `validador.py` importa `pipeline.py`

Resultado: inicialização quebrada.

Como evitar:

1. regra de direção de dependência
2. módulo de orquestração não deve ser importado por módulo de regra
3. funções utilitárias compartilhadas vão para módulo neutro

!!! warning "Direção de dependência"

    `main.py` depende de `pipeline.py`.
    `pipeline.py` depende de leitura/validação/transformação/processamento.
    O caminho contrário não deve acontecer.

---

## 7. Por que essa mudança melhora o software?

Porque aumenta previsibilidade operacional:

- o import passa a depender da estrutura do package, não do acaso do diretório atual
- o projeto fica pronto para múltiplos entrypoints (CLI, testes, scripts de manutenção)
- o passo seguinte (camadas `core` e `services`) fica natural

---

## Desafio guiado (em sala)

**Migrar para package sem alterar resultado final**

1. Crie a pasta `dataprocessor/dataprocessor/`
2. Mova os módulos (`pipeline.py`, `leitor.py`, `validador.py`, `transformador.py`, `processador.py`) para dentro dela
3. Crie o `__init__.py`
4. Ajuste imports internos para relativos
5. Ajuste `main.py` para importar `executar_pipeline` com import absoluto
6. Execute e compare saída com a Aula 06

Critério de aceite:

- mesma quantidade de válidos/inválidos
- mesmas métricas finais

---

## Desafio extra (para casa)

Crie um segundo ponto de entrada chamado `debug_main.py` (na raiz do projeto) que também use o package, mas imprima detalhes extras dos inválidos.

Regras:

- não duplicar lógica do pipeline
- `debug_main.py` só chama funções já existentes
- nenhum import relativo no entrypoint

Pergunta para reflexão:

- qual é o ganho de ter mais de um entrypoint reaproveitando o mesmo package?
