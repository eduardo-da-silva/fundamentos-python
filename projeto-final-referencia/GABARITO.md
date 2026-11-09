# Gabarito — Painel de Notas da Turma

**Uso exclusivo do professor.** Contém a solução de referência e a lista completa dos
erros plantados.

## Totais esperados

- Alunos válidos: **32** (3 linhas de `alunos.csv` são rejeitadas)
- Notas válidas: **457** | inválidas: **27** (484 linhas de dados)
- Erros no total: **30** (3 em `alunos.csv`, 27 em `notas.csv`)
- Situações: aprovado **18**, recuperação **11**, reprovado **3**

## Erros por tipo

| Tipo | Quantidade |
| --- | --- |
| `avaliacao_duplicada` | 4 |
| `campo_vazio` | 7 |
| `matricula_duplicada` | 1 |
| `matricula_inexistente` | 5 |
| `matricula_invalida` | 1 |
| `nota_fora_do_intervalo` | 6 |
| `nota_invalida` | 6 |

## Lista completa (linha do arquivo, cabeçalho = linha 1)

| Arquivo | Linha | Tipo | Mensagem da referência |
| --- | --- | --- | --- |
| `alunos.csv` | 7 | `matricula_duplicada` | matrícula 1004 já cadastrada |
| `alunos.csv` | 15 | `campo_vazio` | campo 'nome' vazio |
| `alunos.csv` | 23 | `matricula_invalida` | matrícula '10x7' não é numérica |
| `notas.csv` | 3 | `matricula_inexistente` | matrícula inexistente (1033) |
| `notas.csv` | 35 | `campo_vazio` | campo 'nota' vazio |
| `notas.csv` | 51 | `campo_vazio` | campo 'nota' vazio |
| `notas.csv` | 52 | `nota_invalida` | nota inválida ('--') |
| `notas.csv` | 65 | `nota_fora_do_intervalo` | nota fora do intervalo (12.0) |
| `notas.csv` | 80 | `avaliacao_duplicada` | História/P2 já lançada para 1032 |
| `notas.csv` | 114 | `nota_fora_do_intervalo` | nota fora do intervalo (11.0) |
| `notas.csv` | 123 | `matricula_inexistente` | matrícula inexistente (9999) |
| `notas.csv` | 162 | `matricula_inexistente` | matrícula inexistente (2001) |
| `notas.csv` | 167 | `matricula_inexistente` | matrícula inexistente (1099) |
| `notas.csv` | 177 | `campo_vazio` | campo 'avaliacao' vazio |
| `notas.csv` | 180 | `nota_fora_do_intervalo` | nota fora do intervalo (100.0) |
| `notas.csv` | 206 | `nota_fora_do_intervalo` | nota fora do intervalo (10.5) |
| `notas.csv` | 215 | `avaliacao_duplicada` | Física/P2 já lançada para 1027 |
| `notas.csv` | 217 | `nota_invalida` | nota inválida ('dez') |
| `notas.csv` | 238 | `nota_fora_do_intervalo` | nota fora do intervalo (-1.0) |
| `notas.csv` | 240 | `avaliacao_duplicada` | Inglês/P2 já lançada para 1008 |
| `notas.csv` | 269 | `nota_invalida` | nota inválida ('abc') |
| `notas.csv` | 312 | `nota_fora_do_intervalo` | nota fora do intervalo (-0.5) |
| `notas.csv` | 325 | `nota_invalida` | nota inválida ('NA') |
| `notas.csv` | 327 | `avaliacao_duplicada` | Física/P1 já lançada para 1008 |
| `notas.csv` | 331 | `nota_invalida` | nota inválida ('oito') |
| `notas.csv` | 343 | `campo_vazio` | campo 'matricula' vazio |
| `notas.csv` | 396 | `campo_vazio` | campo 'disciplina' vazio |
| `notas.csv` | 457 | `nota_invalida` | nota inválida ('7.5.0') |
| `notas.csv` | 461 | `campo_vazio` | campo 'nota' vazio |
| `notas.csv` | 465 | `matricula_inexistente` | matrícula inexistente (1000) |

## Armadilhas que não são erro

- 10 linhas de `notas.csv` e 4 de `alunos.csv` têm **espaços nas pontas** (`"  Carla Dias "`).
  Devem ser aparados (`strip`), não rejeitados.
- Uma matrícula duplicada em `alunos.csv` (linha 7) é rejeitada; vale o primeiro cadastro.
- As 4 `avaliacao_duplicada` mantêm a **primeira** nota e rejeitam a repetida.
- O aluno de `alunos.csv` linha 15 (nome vazio) não tem notas; nenhuma nota do dataset
  aponta para as matrículas rejeitadas.

## Decisões de correção

- A ordem das checagens em `notas.csv` é: campo vazio → formato da nota → intervalo →
  matrícula inexistente → duplicada. Cada linha plantada tem só um erro, então a ordem
  só importa para dados novos.
- Médias são aritméticas simples sobre as notas válidas (do aluno; da disciplina). A
  situação usa a média **sem arredondar**; a exibição usa 2 casas. Aceite diferença de
  até 0,01.
- Corrija por tipo e linha do erro, **não** pelo texto da mensagem.
- Valores `nan`/`inf` são rejeitados como `nota_invalida` (`float("nan")` não falha).

## Como rodar a referência

```bash
cd projeto-final-referencia/painel
python -m painel --alunos data/alunos.csv --notas data/notas.csv \
  --config data/config.json --formato json --output output/
python -m unittest discover -s tests -v
```

`saida_esperada/` contém os relatórios gerados pela referência.
O teste `TestDatasetCompleto` compara os erros encontrados com `tests/gabarito_erros.json`,
produzido pelo gerador dos dados de forma independente da solução.
