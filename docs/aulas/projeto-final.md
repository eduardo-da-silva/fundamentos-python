# Projeto final — Painel de Notas da Turma

## Objetivo

Neste projeto você vai aplicar, de forma autônoma, o que construiu ao longo do curso. O
domínio é novo (notas escolares), mas o caminho é o mesmo do DataProcessor: ler dados
sujos, validar, calcular, gerar relatórios e expor tudo por uma interface de linha de
comando — com o código organizado em camadas.

- **Prazo:** 2 semanas
- **Esforço estimado:** 3 a 4 horas
- **Modalidade:** individual
- **Ferramentas:** Python e biblioteca padrão (FastAPI só na extensão opcional)

!!! note "O que está sendo avaliado"

	Não é a quantidade de funcionalidades. É a **separação de responsabilidades**: a regra
	de negócio mora no `core`, a leitura e a escrita de arquivos moram na `infra`, e a CLI
	apenas recebe argumentos e chama o service.

## 1. O problema

Uma escola mantém as notas da turma em planilhas exportadas em CSV. Os arquivos chegam
com erros: notas fora do intervalo, matrículas que não existem, campos vazios. A
coordenação precisa de um programa que **consolide** esses dados e informe a situação de
cada aluno, sem travar quando encontrar um registro inválido.

## 2. Arquivos de entrada

Baixe os arquivos: [alunos.csv](../assets/projeto-final/alunos.csv),
[notas.csv](../assets/projeto-final/notas.csv) e
[config.json](../assets/projeto-final/config.json). São 32 alunos em 3 turmas, 5
disciplinas (Matemática, Português, Física, História e Inglês) e 3 avaliações por
disciplina (`P1`, `P2` e `T1`): cerca de 480 linhas de notas. O formato é este:

`alunos.csv`

```csv
matricula,nome,turma
1001,Ana Souza,3A
1002,Bruno Lima,3A
1003,Carla Dias,3B
```

`notas.csv`

```csv
matricula,disciplina,avaliacao,nota
1001,Matemática,P1,8.5
1001,Matemática,P2,7.0
1002,Matemática,P1,4.5
```

`config.json`

```json
{
  "media_aprovacao": 6.0,
  "media_recuperacao": 4.0,
  "nota_maxima": 10.0
}
```

Os dados fornecidos contêm erros de propósito. Seu programa deve encontrá-los e
**registrá-los**, não corrigi-los em silêncio nem parar a execução. Os tipos de problema
são:

| Tipo                     | Onde         | Descrição                                              |
| ------------------------ | ------------ | ------------------------------------------------------ |
| `campo_vazio`            | os dois      | qualquer campo obrigatório em branco                   |
| `nota_invalida`          | `notas.csv`  | nota que não é um número (por exemplo `"oito"`)        |
| `nota_fora_do_intervalo` | `notas.csv`  | nota negativa ou maior que `nota_maxima`               |
| `matricula_inexistente`  | `notas.csv`  | matrícula que não consta em `alunos.csv`               |
| `avaliacao_duplicada`    | `notas.csv`  | mesma matrícula, disciplina e avaliação já lançadas    |
| `matricula_invalida`     | `alunos.csv` | matrícula não numérica                                 |
| `matricula_duplicada`    | `alunos.csv` | matrícula já cadastrada em uma linha anterior          |

Há também uma **armadilha que não é erro**: alguns campos têm espaços sobrando nas
pontas (por exemplo `"  Carla Dias "`). Esses valores devem ser limpos e aceitos.

## 3. O que o programa deve fazer

1. **Ler** os arquivos CSV e JSON.
2. **Validar** cada registro. Os válidos seguem no pipeline; os inválidos vão para uma
   lista de erros com a linha de origem e o motivo.
3. **Calcular** as médias e a situação de cada aluno:
    - média do aluno = média aritmética de todas as suas notas válidas
    - média da disciplina = média aritmética de todas as notas válidas da disciplina
      (considerando a turma inteira)
    - média ≥ `media_aprovacao` → `aprovado`
    - média ≥ `media_recuperacao` → `recuperação`
    - caso contrário → `reprovado`

    A situação usa a média sem arredondar; nos relatórios, exiba 2 casas decimais.
4. **Gerar relatórios** em texto e em JSON, incluindo a seção de erros encontrados.
5. **Executar por linha de comando:**

```bash
python -m painel \
  --alunos data/alunos.csv \
  --notas data/notas.csv \
  --config data/config.json \
  --formato json \
  --output output/
```

### Regras de validação

- A numeração de linha dos erros conta o cabeçalho como **linha 1**.
- Em caso de duplicata, vale o **primeiro** registro; o repetido é rejeitado.
- Um registro inválido **não interrompe** nada: o programa registra o erro e segue.
- Cada linha rejeitada gera **um** erro. Se houver mais de um problema, registre o
  primeiro na ordem da tabela de tipos acima (vazio → formato → intervalo → matrícula).

### Exemplo de saída em texto

```text
PAINEL DE NOTAS — RESUMO
Alunos processados: 32
Registros de nota válidos: 457 | inválidos: 27

Situação dos alunos
  Ana Souza              3A  média 8.05  aprovado
  Bruno Lima             3B  média 7.89  aprovado
  ...

Média por disciplina
  Física       6.29
  ...

Erros encontrados (30)
  alunos.csv:7  matrícula 1004 já cadastrada
  notas.csv:3  matrícula inexistente (1033)
  notas.csv:52  nota inválida ('--')
  ...
```

Os **totais** (32 alunos, 457 notas válidas, 27 notas inválidas, 30 erros no total) servem
para você conferir se o seu programa está correto. O texto das mensagens de erro e o
layout do relatório são livres; o que conta é encontrar os mesmos erros nas mesmas
linhas.

## 4. Requisitos obrigatórios

| Requisito                                                                  | Aulas de referência |
| -------------------------------------------------------------------------- | ------------------- |
| Package com `core/`, `infra/` e `services/`                                | 06–10               |
| `@dataclass` para `Aluno` e `Nota`, com ao menos um método de comportamento (`media()`, `situacao()`) | 11–12 |
| Ao menos 2 geradores de relatório, com `ABC` e polimorfismo (texto e JSON) | 13                  |
| Validação que acumula erros sem interromper o processamento                | 04                  |
| CLI com `argparse` e `logging` em arquivo                                  | 15                  |
| Ao menos 5 testes com `unittest`, sem depender de arquivos reais           | 12, 18, 24          |
| `README.md` com instruções de execução e de testes                         | —                   |

## 5. Estrutura sugerida

```text
painel/
    painel/
        __main__.py
        main.py
        core/
            entidades.py
            validador.py
            metricas.py
        infra/
            arquivos.py
            relatorios.py
        services/
            processamento.py
    data/
    tests/
    README.md
```

Você pode adaptar os nomes, desde que a separação de responsabilidades seja mantida.

## 6. Extensões opcionais

Escolha **uma** para ganhar pontos extras. Não são necessárias para a nota máxima do
requisito base.

- **Menu interativo** que reaproveita o mesmo service (Aulas 16–18).
- **Endpoint** `GET /alunos/{matricula}` com FastAPI, devolvendo situação e médias, com
  teste via `TestClient` (Aulas 19–24).
- **Ranking** dos 3 melhores alunos por disciplina no relatório.

## 7. Cronograma sugerido

| Quando   | Tarefa                                                  | Tempo   |
| -------- | ------------------------------------------------------- | ------- |
| Semana 1 | Estrutura do package, entidades, leitura e validação    | ~1h30   |
| Semana 1 | Cálculo de médias e situação                            | ~45 min |
| Semana 2 | Relatórios (ABC), CLI e logging                         | ~1h     |
| Semana 2 | Testes e README                                         | ~45 min |

!!! tip "Dica de ordem de trabalho"

	Faça primeiro o caminho mais curto que funciona de ponta a ponta (ler → validar →
	calcular → imprimir), mesmo feio. Depois reorganize em camadas e acrescente os
	relatórios. É a mesma ordem das Aulas 01–10.

## 8. Critérios de avaliação

| Critério                                                         | Pontos |
| ---------------------------------------------------------------- | ------ |
| Funciona do início ao fim com os dados fornecidos                | 3      |
| Separação em camadas, sem regra de negócio na CLI                | 2      |
| Entidades e polimorfismo bem usados                              | 2      |
| Validação robusta e testes que passam                            | 2      |
| `README` e clareza do código                                     | 1      |
| **Total**                                                        | **10** |

A extensão opcional vale até **1 ponto extra**.

## 9. Entrega

- Pasta do projeto compactada ou repositório Git, **sem** `__pycache__`, ambiente
  virtual ou arquivos de saída.
- Dentro de `painel/`, o comando `python -m unittest discover -s tests` deve passar.
- O comando de execução do item 3 deve funcionar sem alterações.

## Antes de entregar

Faça este roteiro de verificação:

1. Rode o programa com os dados fornecidos. Os erros plantados aparecem no relatório?
2. Rode os testes. Algum deles depende de um arquivo que só existe na sua máquina?
3. Apague a pasta `output/` e rode de novo. O programa a recria?
4. Abra o `core/`. Existe algum `import` de `argparse`, `csv` ou `json` lá? Se existir,
   a regra de negócio está misturada com a infraestrutura.
