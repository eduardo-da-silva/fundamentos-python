# Aula 15 — CLI, logging e integração final

## Objetivo

Nesta aula você vai:

- Transformar o programa em uma CLI reutilizável
- Ler argumentos com `argparse`
- Selecionar fonte e relatório durante a execução
- Salvar saídas e logs
- Tratar erros e códigos de saída
- Executar o pipeline completo

## 1. Do script fixo para uma CLI

Até aqui, os caminhos poderiam estar escritos diretamente no `main.py`. Isso obriga o
usuário a editar o código para processar outro arquivo.

Queremos executar:

```bash
python -m dataprocessor \
  --clientes data/clientes.csv \
  --transacoes data/transacoes.csv \
  --config data/config.json \
  --formato json \
  --output output/
```

## 2. Criando o parser

Comece com a biblioteca padrão:

```python
import argparse


def configurar_parser():
    parser = argparse.ArgumentParser(
        description="Processa clientes e transações."
    )
    parser.add_argument("--clientes", required=True)
    parser.add_argument("--transacoes", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--formato", choices=("texto", "json", "csv"), default="texto")
    parser.add_argument("--output", default="output")
    return parser
```

Teste a ajuda antes de conectar o pipeline:

```bash
python -m dataprocessor --help
```

## 3. Conectando as abstrações

Depois de obter os argumentos, crie a fonte concreta e execute o service:

```python
args = configurar_parser().parse_args(argv)
fonte = FonteDadosArquivos(
    args.clientes,
    args.transacoes,
    args.config,
)
resultado = executar_processamento(fonte)
gerador = criar_gerador(args.formato)
relatorio = gerador.render(resultado)
```

Observe o fluxo:

```text
argumentos
   ↓
FonteDadosArquivos
   ↓
executar_processamento
   ↓
ResultadoProcessamento
   ↓
GeradorRelatorio concreto
```

O `main.py` escolhe as implementações concretas, mas as camadas internas continuam
trabalhando com as ABCs.

## 4. Salvando o resultado

Crie o diretório de saída e escolha a extensão:

```python
from pathlib import Path


args.output.mkdir(parents=True, exist_ok=True)
nome = "relatorio.txt" if args.formato == "texto" else f"relatorio.{args.formato}"
(args.output / nome).write_text(relatorio, encoding="utf-8")
```

O relatório JSON não deve receber mensagens de diagnóstico. A saída do relatório e o
log são arquivos diferentes.

## 5. Registrando o processamento

Use `print()` para o resultado que o usuário pediu e `logging` para diagnóstico:

```python
import logging


logging.basicConfig(
    filename=args.output / "dataprocessor.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logging.info("Iniciando processamento")
```

Ao concluir:

```python
logging.info(
    "Processamento concluído: %d clientes e %d transações válidos",
    len(resultado.clientes),
    len(resultado.transacoes),
)
```

## 6. Tratando falhas e códigos de saída

Arquivos inexistentes e JSON inválido devem produzir erro controlado:

```python
try:
    resultado = executar_processamento(fonte)
except (OSError, ValueError, KeyError) as erro:
    logging.exception("Falha no processamento")
    print(f"[ERRO] {erro}")
    return 1

return 0
```

O terminal pode usar o código retornado:

```bash
python -m dataprocessor ...
echo $?
```

`0` indica execução válida; `1` indica falha de entrada ou processamento.

## 7. Verificação guiada

Execute o formato texto:

```bash
cd dataprocessor
python -m dataprocessor \
  --clientes data/clientes.csv \
  --transacoes data/transacoes.csv \
  --config data/config.json \
  --formato texto \
  --output output/texto/
```

Confirme:

```text
Clientes válidos: 2
Transações válidas: 2
Média de idade: 39.5
Total aprovado: R$ 150.50
```

Depois execute JSON e CSV e confira os arquivos gerados. Por fim, passe um caminho
inexistente e verifique o código de saída `1` e a criação do log de erro.

## Desafio guiado

1. Crie o parser com os cinco argumentos.
2. Instancie `FonteDadosArquivos` a partir dos caminhos.
3. Execute o service.
4. Escolha o gerador pela fábrica.
5. Salve relatório e log.
6. Trate erros e retorne códigos de saída.
7. Teste os três formatos e um caminho inválido.

## Entrega do módulo

Ao final das Aulas 12–15, o DataProcessor possui:

- entidades com comportamento explícito;
- contratos com ABC e implementações por herança;
- relatórios polimórficos;
- fontes de dados substituíveis;
- testes automatizados;
- CLI e logging usando apenas a biblioteca padrão.

## Resumo

O `main.py` conecta as partes, mas não concentra as regras. As ABCs tornam os contratos
visíveis para quem está aprendendo, as classes concretas mostram a herança e a CLI fecha
o ciclo entre entrada, processamento e saída.
