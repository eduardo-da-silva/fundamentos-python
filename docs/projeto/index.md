# Projeto — DataProcessor CLI

## Visão geral

O **DataProcessor CLI** é o projeto central do curso. Você vai construí-lo incrementalmente ao longo das aulas, adicionando peças a cada encontro.

Ao final da Fase 1, o sistema vai:

- Ler arquivos CSV e JSON da linha de comando
- Validar cada registro contra regras de negócio
- Normalizar e transformar os dados
- Cruzar informações entre clientes e transações
- Gerar um relatório consolidado em texto
- Salvar os resultados em arquivos de saída
- Registrar logs de execução

No **Módulo 5**, o foco muda de funcionalidade para arquitetura:

- reorganizar o projeto em camadas
- separar regras de negócio de infraestrutura
- centralizar configuração
- preparar base para POO sem alterar comportamento funcional

---

## Estrutura ao fim da Fase 1 (Aula 05)

```
dataprocessor/
    main.py           ← ponto de entrada, orquestra o pipeline
    leitor.py         ← leitura de CSV e JSON (Aula 03)
    validador.py      ← validação dos dados (Aula 04)
    transformador.py  ← normalização e limpeza (Aula 05)
    processador.py    ← métricas e agregações (Aula 02)
    relatorio.py      ← geração de relatórios (fase posterior)
    logger.py         ← logs de execução (fase posterior)
    data/
        clientes.csv
        transacoes.csv
        config.json
    output/
        relatorio.txt
        clientes_validos.csv
        erros.log
```

    ## Estrutura ao fim do Módulo 5 (Aula 10)

    ```text
    dataprocessor/
      main.py
      dataprocessor/
        __init__.py
        config.py
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
      data/
        clientes.csv
        transacoes.csv
        config.json
    ```

---

## Pipeline de processamento

```mermaid
flowchart TD
    A[Arquivos de entrada\nCSV + JSON] --> B[Leitura\nleitor.py]
    B --> C[Validação\nvalidador.py]
    C --> D{Válido?}
    D -- Sim --> E[Transformação\ntransformador.py]
    D -- Não --> F[Log de erros\nerros.log]
    E --> G[Processamento\nprocessador.py]
    G --> H[Relatório\nrelatorio.py]
    H --> I[Saída\noutput/]
```

---

## O que está pronto ao fim de cada aula

| Aula | O que o DataProcessor consegue fazer                |
| ---- | --------------------------------------------------- |
| 01   | Ter dados hardcoded em memória e exibir por cidade  |
| 02   | Calcular métricas (média, mín, máx, total aprovado) |
| 03   | Ler dados reais de arquivos CSV e JSON              |
| 04   | Separar registros válidos de inválidos              |
| 05   | Normalizar dados e executar o pipeline completo     |
| 06   | Revisar responsabilidades e extrair orquestração    |
| 07   | Migrar para package e padronizar imports            |
| 08   | Isolar regras de negócio na camada `core`           |
| 09   | Criar camada `services` e separar infraestrutura    |
| 10   | Centralizar configuração e consolidar arquitetura   |

---

## Mapa de camadas no fim do Módulo 5

| Camada      | Responsabilidade                                 |
| ----------- | ------------------------------------------------ |
| `core`      | Regras puras de negócio                          |
| `infra`     | Entrada de dados e acesso a recursos externos    |
| `services`  | Casos de uso e orquestração do pipeline          |
| `main.py`   | Entrada da aplicação (CLI)                       |

!!! note "Invariante do módulo"

  A arquitetura muda. O comportamento funcional permanece.

---

## Exemplo de saída esperada (Aula 05)

```
=== DataProcessor CLI ===

[LEITURA]
  clientes.csv ............. 5 registros
  transacoes.csv ........... 5 registros
  config.json .............. OK

[VALIDAÇÃO]
  Clientes válidos: 2 / 5
  Transações válidas: 2 / 5

[TRANSFORMAÇÃO]
  2 clientes normalizados
  2 transações normalizadas

[RELATÓRIO]
  Total aprovado: R$ 150.50
  Média de idade: 39.5
  Clientes por cidade:
    Joinville: 1
    Florianopolis: 1
```

---

## Como executar

```bash
cd dataprocessor
python main.py
```

Nas fases seguintes do curso, o projeto vai aceitar argumentos de linha de comando:

```bash
python main.py --clientes data/clientes.csv --config data/config.json --output output/
```
