# Aula 16 — Menu interativo em texto

## Objetivo

Nesta aula você vai:

- Criar uma segunda porta de entrada para o DataProcessor, além da CLI de argumentos
- Construir um loop de menu com `while True` e `input()`
- Reaproveitar `executar_processamento` e `criar_gerador` sem duplicar regra de negócio
- Despachar opções do menu para funções dedicadas

## 1. Por que um menu, além do `argparse`?

A CLI da Aula 15 é ótima para automação: um comando, todos os parâmetros, roda e
termina. Mas ela é ruim para *explorar* dados — a cada teste, você reescreve a linha
inteira de argumentos.

Um menu interativo resolve outro problema: alguém sentado no terminal, testando o
sistema passo a passo, sem decorar flags. Os dois formatos vão conviver — nenhuma CLI de
produção séria é escrita de um jeito só.

!!! note "Isso não substitui a Aula 15"

    `main.py` continua existindo, intacto. O menu é uma **porta de entrada nova**, não
    uma reforma da antiga.

## 2. Anatomia de um loop de menu

O padrão é sempre o mesmo: mostrar opções, ler a escolha, decidir o que fazer, repetir.

```python
def menu_principal():
    while True:
        print("\n=== DataProcessor — Menu ===")
        print("1. Processar dados")
        print("2. Exibir relatório")
        print("3. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print("processar (ainda não implementado)")
        elif opcao == "2":
            print("exibir (ainda não implementado)")
        elif opcao == "3":
            break
```

Rode e confirme que o loop e a saída funcionam antes de conectar qualquer regra de
negócio.

## 3. Criando o módulo `interfaces`

Novo pacote, paralelo a `core`, `infra` e `services`:

```text
dataprocessor/
    dataprocessor/
        interfaces/
            __init__.py
            menu.py
```

`interfaces` é onde moram as portas de entrada — hoje só o menu, mas é o lugar certo
para qualquer forma nova de "alguém conversar com o sistema".

## 4. Opção 1 — Processar dados

Reaproveite exatamente o que a CLI já usa:

```python
from ..infra.fontes import FonteDadosArquivos
from ..services.processamento import executar_processamento


def processar():
    caminho_clientes = input("Caminho do CSV de clientes [data/clientes.csv]: ").strip() or "data/clientes.csv"
    caminho_transacoes = input("Caminho do CSV de transações [data/transacoes.csv]: ").strip() or "data/transacoes.csv"
    caminho_config = input("Caminho do JSON de config [data/config.json]: ").strip() or "data/config.json"

    fonte = FonteDadosArquivos(caminho_clientes, caminho_transacoes, caminho_config)
    resultado = executar_processamento(fonte)
    print(f"Clientes válidos: {len(resultado.clientes)}")
    print(f"Transações válidas: {len(resultado.transacoes)}")
    return resultado
```

Note que `processar()` não sabe nada sobre validação, transformação ou métricas — isso
continua no `core`. O menu só decide **quando** chamar o service.

## 5. Opção 2 — Exibir relatório

```python
from ..infra.relatorios import criar_gerador


def exibir_relatorio(resultado):
    formato = input("Formato (texto/json/csv) [texto]: ").strip() or "texto"
    gerador = criar_gerador(formato)
    print(gerador.render(resultado))
```

## 6. Ligando tudo no loop

```python
def menu_principal():
    resultado = None
    while True:
        print("\n=== DataProcessor — Menu ===")
        print("1. Processar dados")
        print("2. Exibir relatório")
        print("3. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            resultado = processar()
        elif opcao == "2":
            exibir_relatorio(resultado)
        elif opcao == "3":
            break


if __name__ == "__main__":
    menu_principal()
```

Se você escolher "2" antes de "1", o programa quebra — isso é esperado por enquanto. A
Aula 17 resolve isso.

### Verificação 1

Rode o menu de dentro da pasta `dataprocessor/`:

```bash
python -m dataprocessor.interfaces.menu
```

Escolha "1", confirme os caminhos padrão com Enter, depois escolha "2" e veja o
relatório em texto. Por fim, escolha "3" e confirme que o programa termina sem erro.

## Desafio guiado

1. Crie o pacote `interfaces/` com `__init__.py`.
2. Escreva `menu_principal()` com as três opções.
3. Implemente `processar()` reaproveitando `FonteDadosArquivos` e `executar_processamento`.
4. Implemente `exibir_relatorio()` reaproveitando `criar_gerador`.
5. Rode o menu e teste as três opções manualmente.

## Desafio extra

Adicione uma quarta opção, "Salvar relatório em arquivo", reaproveitando a mesma lógica
de escrita em disco que o `main.py` já usa (`Path.write_text`). Não copie a lógica de
formato — chame `criar_gerador` de novo.

## Resumo

O menu interativo prova, na prática, algo que a arquitetura em camadas prometeu desde a
Aula 08: o `core` e o `services` não mudam quando você troca a forma de interagir com o
sistema. O menu apenas orquestra chamadas — a regra de negócio continua em um único
lugar.
