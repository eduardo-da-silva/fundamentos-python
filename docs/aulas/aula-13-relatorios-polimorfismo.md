# Aula 13 — ABC, herança e relatórios polimórficos

## Objetivo

Nesta aula você vai:

- Separar resultado de processamento e apresentação
- Criar uma classe abstrata com `ABC`
- Implementar classes concretas por herança
- Entender sobrescrita e polimorfismo
- Gerar relatórios em texto, JSON e CSV

## 1. O problema: um resultado, várias apresentações

O service calcula os dados. Ele não deveria saber se o usuário quer ler texto no
terminal, enviar JSON para outro programa ou abrir CSV em uma planilha.

O resultado do processamento já está organizado em `ResultadoProcessamento`:

```python
resultado = executar_processamento(fonte)
```

Agora vamos criar objetos responsáveis apenas por transformar esse resultado em texto.

## 2. Primeiro relatório: texto

Comece com uma classe concreta simples:

```python title="dataprocessor/dataprocessor/infra/relatorios.py"
class RelatorioTexto:
    def render(self, resultado) -> str:
        return "\n".join(
            [
                "=== DataProcessor CLI ===",
                f"Clientes válidos: {len(resultado.clientes)}",
                f"Transações válidas: {len(resultado.transacoes)}",
                f"Total aprovado: R$ {resultado.total_aprovado:.2f}",
            ]
        )
```

O método `render()` é o comportamento comum que os próximos relatórios também terão.

## 3. Por que uma classe abstrata?

Queremos que todo gerador de relatório tenha `render()`, mas não existe um relatório
genérico para instanciar. A classe-base serve para declarar o contrato:

```python
from abc import ABC, abstractmethod


class GeradorRelatorio(ABC):
    @abstractmethod
    def render(self, resultado) -> str:
        ...
```

`ABC` transforma a classe em uma abstração. `@abstractmethod` exige que cada classe
concreta implemente o método.

Agora declare a herança:

```python
class RelatorioTexto(GeradorRelatorio):
    def render(self, resultado) -> str:
        ...
```

Este código deve falhar:

```python
GeradorRelatorio()
# TypeError: não é possível instanciar uma classe abstrata
```

### Verificação 1

Adicione ao teste:

```python
def test_gerador_relatorio_e_uma_abc(self):
    self.assertTrue(issubclass(RelatorioTexto, GeradorRelatorio))
    with self.assertRaises(TypeError):
        GeradorRelatorio()
```

Execute somente os testes de relatório e confirme a falha antes de implementar o
contrato. Depois faça a classe herdar de `GeradorRelatorio` e confirme que passam.

## 4. Polimorfismo em ação

Crie os relatórios JSON e CSV usando a mesma abstração:

```python
class RelatorioJson(GeradorRelatorio):
    def render(self, resultado) -> str:
        return json.dumps(resultado.to_dict(), ensure_ascii=False, indent=2) + "\n"


class RelatorioCsv(GeradorRelatorio):
    def render(self, resultado) -> str:
        # escreve os clientes em uma tabela CSV
        ...
```

O consumidor não precisa conhecer a classe concreta:

```python
def salvar_relatorio(gerador: GeradorRelatorio, resultado, caminho):
    caminho.write_text(gerador.render(resultado), encoding="utf-8")
```

O mesmo código aceita qualquer objeto concreto:

```python
for gerador in (RelatorioTexto(), RelatorioJson(), RelatorioCsv()):
    salvar_relatorio(gerador, resultado, caminho)
```

Isso é polimorfismo: a chamada é a mesma, mas o comportamento executado depende do
objeto recebido.

## 5. Escolhendo o formato

Concentre a escolha das classes em uma fábrica:

```python
def criar_gerador(formato: str) -> GeradorRelatorio:
    geradores = {
        "texto": RelatorioTexto,
        "json": RelatorioJson,
        "csv": RelatorioCsv,
    }
    return geradores[formato]()
```

A fábrica escolhe a classe. O restante da aplicação trabalha com `GeradorRelatorio`.

## 6. Testando o contrato e o resultado

Teste duas coisas diferentes:

- a hierarquia impede uma classe abstrata incompleta;
- cada relatório produz o conteúdo esperado.

```python
def test_relatorio_json_preserva_dados(self):
    documento = json.loads(RelatorioJson().render(resultado_exemplo()))
    self.assertEqual(documento["metricas"]["total_aprovado"], 150.50)
```

Execute:

```bash
cd dataprocessor
python -m unittest tests.test_relatorios -v
```

## Desafio guiado

1. Crie `GeradorRelatorio(ABC)`.
2. Marque `render()` com `@abstractmethod`.
3. Faça `RelatorioTexto` herdar da ABC.
4. Implemente JSON e CSV com a mesma operação.
5. Crie testes de herança e conteúdo.
6. Use a fábrica para escolher o formato.

## Desafio extra

Crie `RelatorioInvalidos(GeradorRelatorio)`. Ele deve listar a identificação e os erros
dos registros inválidos sem revalidar nem alterar os dados.

## Resumo

Uma ABC define o contrato que o aluno precisa enxergar. A herança permite que cada
implementação cumpra esse contrato de um jeito diferente. Na próxima aula, aplicaremos
a mesma ideia às fontes de dados.
