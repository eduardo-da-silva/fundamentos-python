# Aula 18 — Isolando a porta de entrada

## Objetivo

Nesta aula você vai:

- Separar a lógica que decide o que fazer da lógica que conversa com o teclado
- Extrair uma função pura e testável de dentro do menu
- Comparar `main.py` (CLI) e `interfaces/menu.py` como dois adaptadores do mesmo núcleo
- Escrever um teste automatizado para a porta de entrada interativa

## 1. O que dá para testar em um menu?

`input()` e `print()` não são fáceis de testar — exigiriam simular teclado e capturar
tela. Mas a parte que importa — pegar três caminhos e devolver um
`ResultadoProcessamento` — não depende de terminal nenhum. Ela só está presa dentro de
uma função que também faz `input()`.

Separe as duas responsabilidades.

## 2. Extraindo a função pura

Hoje, `processar()` mistura leitura de teclado com orquestração:

```python
def processar():
    caminho_clientes = input(...) or "data/clientes.csv"
    ...
    fonte = FonteDadosArquivos(caminho_clientes, caminho_transacoes, caminho_config)
    resultado = executar_processamento(fonte)
    ...
```

Separe em duas funções:

```python
def processar_caminhos(caminho_clientes, caminho_transacoes, caminho_config):
    fonte = FonteDadosArquivos(caminho_clientes, caminho_transacoes, caminho_config)
    return executar_processamento(fonte)


def processar():
    caminho_clientes = input("Caminho do CSV de clientes [data/clientes.csv]: ").strip() or "data/clientes.csv"
    caminho_transacoes = input("Caminho do CSV de transações [data/transacoes.csv]: ").strip() or "data/transacoes.csv"
    caminho_config = input("Caminho do JSON de config [data/config.json]: ").strip() or "data/config.json"
    try:
        resultado = processar_caminhos(caminho_clientes, caminho_transacoes, caminho_config)
    except (OSError, ValueError, KeyError) as erro:
        print(f"[ERRO] Não foi possível processar: {erro}")
        return None
    print(f"Clientes válidos: {len(resultado.clientes)}")
    print(f"Transações válidas: {len(resultado.transacoes)}")
    return resultado
```

`processar_caminhos` não chama `input()` nem `print()`. Ela é só orquestração — e é
exatamente o que já faz o `main.py` da Aula 15.

### Verificação 1

Escreva o teste em `tests/test_menu.py`:

```python
import unittest

from dataprocessor.interfaces.menu import processar_caminhos


class ProcessarCaminhosTestCase(unittest.TestCase):
    def test_processa_dataset_padrao(self):
        resultado = processar_caminhos(
            "data/clientes.csv",
            "data/transacoes.csv",
            "data/config.json",
        )
        self.assertEqual(resultado.total_aprovado, 150.50)
```

Rode:

```bash
python -m unittest tests.test_menu -v
```

Nenhum `input()` foi simulado — porque a função testada não precisa de teclado.

## 3. Dois adaptadores, um núcleo

Coloque `main.py` e `menu.py` lado a lado:

```text
main.py (CLI)                          interfaces/menu.py (interativo)
--------------------------------       --------------------------------
args = parser.parse_args()             caminhos = input(...)
fonte = FonteDadosArquivos(...)        fonte = FonteDadosArquivos(...)
resultado = executar_processamento()   resultado = executar_processamento()
relatorio = gerador.render()           relatorio = gerador.render()
```

A única diferença real é **de onde vêm os caminhos**: `argparse` ou `input()`. Tudo que
vem depois — `FonteDadosArquivos`, `executar_processamento`, `criar_gerador` — é
idêntico.

!!! note "Regra da porta de entrada"

    Qualquer adaptador pode escolher qual `FonteDados` ou `GeradorRelatorio` concreto
    usar. Essa é a única decisão que pertence à borda do sistema. Tudo o mais já foi
    decidido em `core` e `services`.

## 4. Removendo a duplicação de composição

Montar a `FonteDadosArquivos` a partir de três caminhos aparece em `main.py` e em
`menu.py`. Extraia isso para um único lugar, dentro de `infra/fontes.py`:

```python
def fonte_a_partir_de_caminhos(caminho_clientes, caminho_transacoes, caminho_config) -> FonteDados:
    return FonteDadosArquivos(caminho_clientes, caminho_transacoes, caminho_config)
```

Ambos os adaptadores passam a chamar essa função em vez de instanciar a classe
diretamente. Se um dia `FonteDadosArquivos` ganhar um parâmetro novo, você muda em um
lugar só.

`processar_caminhos()` fica mais simples ainda:

```python
from ..infra.fontes import fonte_a_partir_de_caminhos


def processar_caminhos(caminho_clientes, caminho_transacoes, caminho_config):
    fonte = fonte_a_partir_de_caminhos(caminho_clientes, caminho_transacoes, caminho_config)
    return executar_processamento(fonte)
```

### Verificação 2

Rode a suíte completa e confirme que nada quebrou:

```bash
python -m unittest discover -s tests -v
```

## Desafio guiado

1. Extraia `processar_caminhos()` de dentro de `processar()`.
2. Escreva `tests/test_menu.py` testando só a função pura.
3. Extraia `fonte_a_partir_de_caminhos()` e use em `main.py` e `menu.py`.
4. Rode a suíte inteira e confirme que os testes antigos continuam passando.

## Desafio extra

Escreva um teste que compara o resultado de `processar_caminhos()` com o resultado
obtido rodando `main.py` via `subprocess` (como em `tests/test_cli.py`) sobre o mesmo
dataset, e confirme que o `total_aprovado` é idêntico nos dois caminhos.

## Resumo

Separar "o que faz" de "como pergunta" é o que transforma uma porta de entrada em algo
testável. A Aula 19 vai usar exatamente essa mesma função pura para responder a uma
requisição HTTP — sem mudar uma linha dela.
