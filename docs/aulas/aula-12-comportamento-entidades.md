# Aula 12 — Comportamento nas entidades

## Objetivo

Nesta aula você vai:

- Retomar o DataProcessor a partir da Aula 11
- Diferenciar dado, comportamento e formatação
- Adicionar `@property` às entidades do domínio
- Preservar a imutabilidade com `frozen=True` e `replace()`
- Criar testes comportamentais com `unittest`

## Como vamos trabalhar

O projeto completo está disponível na pasta `dataprocessor/`, mas não vamos começar
copiando todos os arquivos. Em cada etapa você fará uma pequena mudança, executará um
teste e observará o efeito no projeto.

Ao final de cada etapa, compare seu código com a implementação disponível no projeto.

## 1. Ponto de partida: a entidade só tem dados

Na Aula 11, um cliente deixou de ser um dicionário solto:

```python title="dataprocessor/dataprocessor/core/entidades.py"
from dataclasses import dataclass


@dataclass(frozen=True)
class Cliente:
    id: int | None
    nome: str
    email: str
    idade: int | None
    cidade: str
    data_cadastro: str
```

Essa classe já melhora o contrato do programa, mas ainda responde apenas "quais dados
um cliente possui?". Agora queremos responder perguntas sobre esses dados.

## 2. Dado, comportamento ou apresentação?

Considere estas três operações:

```python
cliente.nome                  # dado
cliente.identificacao        # valor derivado
print(cliente.identificacao)  # apresentação
```

`identificacao` pode pertencer à entidade porque é um valor derivado, não lê arquivo,
não imprime e não depende de outra camada.

Adicione a propriedade:

```python title="dataprocessor/dataprocessor/core/entidades.py"
@property
def identificacao(self) -> str:
    return f"#{self.id} {self.nome}"
```

Teste no interpretador:

```python
cliente = Cliente(5, "Pedro Santos", "", 38, "Sao Paulo", "2023-02-30")
print(cliente.identificacao)
# #5 Pedro Santos
```

### Verificação 1

Adicione este teste em `tests/test_entidades.py`:

```python
def test_cliente_exibe_identificacao_derivada(self):
    cliente = Cliente(5, "Pedro Santos", "", 38, "Sao Paulo", "2023-02-30")
    self.assertEqual(cliente.identificacao, "#5 Pedro Santos")
```

Execute a suíte:

```bash
cd dataprocessor
python -m unittest discover -s tests -v
```

## 3. Comportamento de `Transacao`

Uma transação também pode responder se foi aprovada. Adicione a propriedade à classe:

```python title="dataprocessor/dataprocessor/core/entidades.py"
@property
def esta_aprovada(self) -> bool:
    return self.status == "aprovado"
```

Teste os dois estados:

```python
aprovada = Transacao(1, 1, 150.50, "eletronicos", "2023-05-10", "aprovado")
recusada = Transacao(4, 1, 300.00, "eletronicos", "2023-05-13", "recusado")

assert aprovada.esta_aprovada is True
assert recusada.esta_aprovada is False
```

A propriedade não substitui a validação da transação. Ela responde uma pergunta sobre
uma transação já criada; `validador.py` continua decidindo se os dados são aceitáveis.

## 4. Imutabilidade: mudar significa criar outra entidade

`frozen=True` impede alterações acidentais:

```python
cliente.nome = "Outro Nome"
# dataclasses.FrozenInstanceError
```

A transformação não deve alterar o objeto recebido. Use `replace()` para criar uma nova
entidade:

```python
from dataclasses import replace


def transformar_cliente(cliente):
    return replace(
        cliente,
        nome=normalizar_nome(cliente.nome),
        email=normalizar_email(cliente.email),
        cidade=normalizar_cidade(cliente.cidade),
        data_cadastro=cliente.data_cadastro.strip(),
    )
```

Faça este experimento:

```python
original = Cliente(7, "  ana LIMA ", "ANA@Email.COM", 45, " Joinville ", "2023-01-25")
normalizado = transformar_cliente(original)

print(original.nome)     #   ana LIMA
print(normalizado.nome)  # Ana Lima
```

## 5. O caminho da entidade pelo pipeline

Confira a responsabilidade de cada etapa:

```text
CSV/JSON
   ↓
infra/arquivos.py       cria Cliente e Transacao
   ↓
core/validador.py       lê atributos e retorna erros
   ↓
core/transformador.py   cria novas entidades com replace()
   ↓
core/metricas.py        calcula os números do domínio
```

Procure por `registro["campo"]` no package. Depois da migração, o acesso deve usar
`registro.campo`.

## 6. Verificação do comportamento anterior

Execute o teste de integração com os arquivos oficiais:

```bash
python -m unittest tests.test_processamento -v
```

O resultado esperado continua sendo:

```text
Clientes válidos: 2
Transações válidas: 2
Média de idade: 39.5
Total aprovado: R$ 150.50
```

## Desafio guiado

1. Adicione `Cliente.identificacao`.
2. Adicione `Transacao.esta_aprovada`.
3. Escreva testes para as duas propriedades.
4. Garanta que as entidades continuam imutáveis.
5. Reescreva a transformação com `replace()`.
6. Execute a suíte completa e compare o baseline.

## Desafio extra

Adicione `Transacao.resumo`, retornando uma linha com ID, valor e status. Discuta se a
linha é comportamento da entidade ou formatação de relatório.

## Resumo

Entidades não precisam conter toda a lógica do sistema. Elas devem conter dados e
comportamentos pequenos, derivados e coerentes com o próprio domínio. Na próxima aula,
essa ideia será ampliada para objetos de relatório com uma abstração comum.
