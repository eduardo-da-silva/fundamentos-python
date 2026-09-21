# Aula 17 — Estado de sessão e robustez do menu

## Objetivo

Nesta aula você vai:

- Guardar o resultado do processamento entre iterações do menu
- Impedir que uma opção inválida ou fora de ordem derrube o programa
- Tratar erros de processamento (arquivo inexistente, JSON inválido) sem fechar o menu
- Adicionar validação de opção e de formato, com mensagens de erro amigáveis

## 1. O problema do estado perdido

A Aula 16 deixou um bug de propósito: escolher "Exibir relatório" antes de "Processar
dados" quebra o programa com `AttributeError`. O motivo é estrutural — `resultado`
começa `None` e só é preenchido dentro do `if opcao == "1"`.

Um menu não pode presumir que quem está usando segue a ordem "certa". Trate isso como
uma responsabilidade da interface, não como "erro de quem usa".

## 2. Guardando estado sem variável global

A resposta não é uma variável global — é o próprio corpo da função de loop, que já vive
durante toda a execução do programa:

```python
def menu_principal():
    resultado = None
    while True:
        ...
        if opcao == "2":
            if resultado is None:
                print("Nenhum dado processado ainda. Escolha a opção 1 primeiro.")
                continue
            exibir_relatorio(resultado)
```

`continue` volta para o topo do loop sem executar o resto do corpo — é o mecanismo certo
para "essa rodada não vale, tenta de novo".

## 3. Validando a opção escolhida

Hoje, digitar "9" simplesmente não faz nada (nenhum `if` corresponde) e o menu reaparece
sem explicação. Torne isso explícito:

```python
opcoes_validas = {"1", "2", "3"}
if opcao not in opcoes_validas:
    print(f"Opção inválida: '{opcao}'. Escolha 1, 2 ou 3.")
    continue
```

## 4. Tratando falhas de processamento

Reaproveite exatamente as exceções que a Aula 15 já tratou na CLI — o menu corre o mesmo
risco (arquivo inexistente, JSON malformado):

```python
def processar():
    caminho_clientes = input("Caminho do CSV de clientes [data/clientes.csv]: ").strip() or "data/clientes.csv"
    caminho_transacoes = input("Caminho do CSV de transações [data/transacoes.csv]: ").strip() or "data/transacoes.csv"
    caminho_config = input("Caminho do JSON de config [data/config.json]: ").strip() or "data/config.json"

    try:
        fonte = FonteDadosArquivos(caminho_clientes, caminho_transacoes, caminho_config)
        resultado = executar_processamento(fonte)
    except (OSError, ValueError, KeyError) as erro:
        print(f"[ERRO] Não foi possível processar: {erro}")
        return None

    print(f"Clientes válidos: {len(resultado.clientes)}")
    print(f"Transações válidas: {len(resultado.transacoes)}")
    return resultado
```

No loop principal, `processar()` pode devolver `None` — e o `resultado` anterior só é
substituído quando o processamento dá certo:

```python
if opcao == "1":
    novo_resultado = processar()
    if novo_resultado is not None:
        resultado = novo_resultado
```

Assim, uma tentativa de reprocessamento que falha não apaga um resultado bom que já
existia.

!!! warning "Por que não `except Exception`?"

    Capturar `Exception` genérico esconderia bugs de verdade (um erro de digitação no
    próprio código, por exemplo). As mesmas três exceções da Aula 15 continuam sendo as
    únicas que representam "entrada ruim de quem usa o programa".

## 5. Submenu de formato

Coloque a mesma validação na escolha de formato:

```python
def exibir_relatorio(resultado):
    formatos = {"texto", "json", "csv"}
    formato = input("Formato (texto/json/csv) [texto]: ").strip() or "texto"
    if formato not in formatos:
        print(f"Formato inválido: '{formato}'.")
        return
    print(criar_gerador(formato).render(resultado))
```

### Verificação 1

Rode o menu e teste, nessa ordem:

1. Escolha "2" sem ter processado nada — deve avisar e voltar ao menu.
2. Digite uma opção inexistente ("9") — deve avisar e voltar ao menu.
3. Processe apontando para um arquivo inexistente — deve mostrar `[ERRO]` e manter o
   menu de pé.
4. Processe de novo com os caminhos corretos, depois exiba o relatório com um formato
   inválido ("xml") — deve avisar sem apagar o `resultado` já processado.

## Desafio guiado

1. Adicione a variável `resultado` com estado entre iterações do loop.
2. Bloqueie a opção "2" quando `resultado is None`.
3. Valide a opção do menu contra um conjunto de opções válidas.
4. Envolva `processar()` em `try/except` com as três exceções da Aula 15.
5. Valide o formato escolhido em `exibir_relatorio()`.

## Desafio extra

Adicione uma opção "Reprocessar com os últimos caminhos usados" que reaproveita os três
caminhos da última chamada bem-sucedida, sem perguntar de novo.

## Resumo

Um menu interativo tem uma responsabilidade que o `argparse` resolve de graça: validar a
sequência de ações de quem está usando o programa. Nada disso é regra de negócio — é
robustez da porta de entrada, e por isso vive inteiramente em `interfaces/menu.py`.
