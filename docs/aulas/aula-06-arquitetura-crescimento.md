# Aula 06 — Crescimento do projeto e responsabilidade de módulos

## Objetivo

Nesta aula você vai:

- Revisar a estrutura atual do **DataProcessor CLI** com olhar arquitetural
- Identificar sinais de crescimento que pedem reorganização
- Definir responsabilidade clara para cada módulo
- Fazer a primeira refatoração de organização sem alterar regra de negócio
- Deixar o ponto de entrada (`main.py`) mais simples e previsível

---

## 1. Projeto pequeno: simples funciona

Até aqui, o projeto está funcional e isso é ótimo. Em projeto pequeno, começar com poucos arquivos é uma decisão boa:

- acelera entrega
- reduz fricção no começo
- facilita aprendizado do fluxo

Mas quando o projeto cresce, surge uma pergunta importante:

> O código ainda está simples ou só ficou concentrado em poucos arquivos?

!!! note "Princípio do módulo"

    Módulo bom não é o módulo "curto". É o módulo com responsabilidade clara.

---

## 2. Revisão da estrutura atual

Estrutura atual ao final da Aula 05:

```text
dataprocessor/
    main.py
    leitor.py
    validador.py
    transformador.py
    processador.py
    data/
        clientes.csv
        transacoes.csv
        config.json
```

### Responsabilidade declarada vs responsabilidade real

| Módulo            | Responsabilidade esperada                     | O que costuma acontecer com o tempo             |
| ----------------- | --------------------------------------------- | ----------------------------------------------- |
| `leitor.py`       | Ler CSV/JSON                                  | Começa a carregar defaults e tratar erro demais |
| `validador.py`    | Validar regras                                | Mistura regra com mensagens e formatação        |
| `transformador.py`| Normalizar dados                              | Acumula limpeza + regra + fallback              |
| `processador.py`  | Calcular métricas                             | Acumula regra de filtro e agregação             |
| `main.py`         | Orquestrar execução                           | Vira arquivo gigante com tudo junto             |

O primeiro gargalo quase sempre aparece em `main.py`.

---

## 3. O problema clássico: `main.py` inchado

Quando o `main.py` cresce demais, três sintomas aparecem:

1. dificuldade para entender o fluxo completo
2. duplicação de passos de validação e transformação
3. mudança pequena exigindo edição em muitos pontos

Exemplo típico (funciona, mas começa a ficar caro de manter):

```python linenums="1" title="dataprocessor/main.py (antes da refatoração da aula)"
from leitor import carregar_clientes, carregar_transacoes, carregar_config
from validador import validar_cliente, validar_transacao, separar_registros
from transformador import transformar_clientes, transformar_transacoes
from processador import media_idade, total_aprovado


def main():
    clientes_raw = carregar_clientes("data/clientes.csv")
    transacoes_raw = carregar_transacoes("data/transacoes.csv")
    config = carregar_config("data/config.json")

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

    print("=== DataProcessor ===")
    print(f"Clientes válidos: {len(clientes)}")
    print(f"Clientes inválidos: {len(clientes_invalidos)}")
    print(f"Transações válidas: {len(transacoes)}")
    print(f"Transações inválidas: {len(transacoes_invalidas)}")
    print(f"Média de idade: {media_idade(clientes):.1f}")
    print(f"Total aprovado: R$ {total_aprovado(transacoes):.2f}")


if __name__ == "__main__":
    main()
```

!!! warning "Importante"

    O problema aqui não é "estar errado". O problema é **escala de manutenção**.
    Com novas funcionalidades, esse arquivo vira gargalo.

---

## 4. Primeira refatoração: extrair orquestração

A primeira mudança do Módulo 5 é pequena e intencional:

- `main.py` para de conhecer detalhes internos do pipeline
- uma função dedicada concentra o fluxo principal

Crie `pipeline.py` para encapsular a execução:

```python linenums="1" title="dataprocessor/pipeline.py"
from leitor import carregar_clientes, carregar_transacoes, carregar_config
from validador import validar_cliente, validar_transacao, separar_registros
from transformador import transformar_clientes, transformar_transacoes
from processador import media_idade, total_aprovado


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

`main.py` fica focado em entrada/saída:

```python linenums="1" title="dataprocessor/main.py (depois da refatoração da aula)"
from pipeline import executar_pipeline


def main():
    resultado = executar_pipeline(
        "data/clientes.csv",
        "data/transacoes.csv",
        "data/config.json",
    )

    print("=== DataProcessor ===")
    print(f"Clientes válidos: {len(resultado['clientes'])}")
    print(f"Clientes inválidos: {len(resultado['clientes_invalidos'])}")
    print(f"Transações válidas: {len(resultado['transacoes'])}")
    print(f"Transações inválidas: {len(resultado['transacoes_invalidas'])}")

    media = resultado["metricas"]["media_idade"]
    total = resultado["metricas"]["total_aprovado"]
    print(f"Média de idade: {media:.1f}")
    print(f"Total aprovado: R$ {total:.2f}")


if __name__ == "__main__":
    main()
```

!!! tip "O ganho real"

    Você não mudou regra de negócio nenhuma. Só mudou **organização de responsabilidade**.
    Esse é exatamente o tipo de refatoração segura que projeto profissional exige.

---

## 5. Comparação com JavaScript (mesma ideia arquitetural)

Separar entrada do caso de uso é o mesmo princípio usado em Node.js.

=== "Python"

    ```python linenums="1"
    # main.py
    from pipeline import executar_pipeline

    def main():
        resultado = executar_pipeline("data/clientes.csv", "data/transacoes.csv", "data/config.json")
        print(resultado["metricas"])
    ```

=== "JavaScript"

    ```javascript linenums="1"
    // main.js
    const { executarPipeline } = require("./pipeline");

    function main() {
      const resultado = executarPipeline("data/clientes.csv", "data/transacoes.csv", "data/config.json");
      console.log(resultado.metricas);
    }
    ```

No Python vamos evoluir isso para packages e camadas nas próximas aulas.

---

## 6. Aplicação imediata no DataProcessor

Após esta aula, a estrutura do projeto fica assim:

```text
dataprocessor/
    main.py
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

Checklist de segurança da refatoração:

- mesmas entradas de arquivo
- mesmas regras de validação
- mesmas regras de transformação
- mesmas métricas finais
- mesma saída funcional

!!! note "Invariante da aula"

    Refatoração arquitetural sem mudança funcional.
    Se o comportamento mudou, foi bug, não evolução arquitetural.

---

## Desafio guiado (em sala)

**Refatorar o ponto de entrada sem quebrar o pipeline**

1. Crie o arquivo `pipeline.py`
2. Implemente `executar_pipeline()` retornando um dicionário com:
   - clientes válidos
   - clientes inválidos
   - transações válidas
   - transações inválidas
   - métricas (`media_idade`, `total_aprovado`)
3. Atualize o `main.py` para apenas chamar `executar_pipeline()` e imprimir resumo
4. Compare a saída antes e depois

Saída esperada (resumo):

```text
=== DataProcessor ===
Clientes válidos: 2
Clientes inválidos: 3
Transações válidas: 2
Transações inválidas: 3
Média de idade: 39.5
Total aprovado: R$ 150.50
```

---

## Desafio extra (para casa)

Crie uma função `imprimir_relatorio(resultado)` em `pipeline.py` (ou em arquivo separado, se preferir) para remover completamente formatação de saída do `main.py`.

Objetivo:

- `main.py` deve ficar com no máximo 10 linhas úteis
- toda regra de apresentação fica centralizada
- nenhum cálculo novo deve aparecer no `main.py`

Pergunta para reflexão:

- se amanhã você trocar CLI por API, quais arquivos precisariam mudar?
