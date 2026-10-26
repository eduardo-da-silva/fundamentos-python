# Aula 25 — Configuração por ambiente e fechamento da Fase 2

## Objetivo

Nesta aula você vai:

- Tirar o caminho dos dados de dentro do código, usando uma variável de ambiente
- Declarar dependências no `pyproject.toml` em vez de um `pip install` solto
- Rodar a API em outra pasta de dados sem alterar uma linha de código
- Revisar o que a Fase 2 acrescentou ao projeto
- Ver onde a Fase 3 (banco de dados) vai se encaixar

## 1. Configuração não pertence ao código

Em `obter_fonte()`, a pasta `"data"` ainda está escrita no código. Para mudar de pasta
hoje, é preciso editar e reiniciar. Pior: o valor certo em desenvolvimento
(`dataprocessor/data`) não é o valor certo em produção.

A prática padrão é ler esse tipo de valor do **ambiente**: variáveis que o sistema
operacional entrega ao processo.

```bash
DATAPROCESSOR_DATA_DIR=/srv/dados uvicorn dataprocessor.interfaces.api:app
```

## 2. Um objeto `Settings`

Crie `dataprocessor/interfaces/config.py`:

```python
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path


def obter_settings() -> Settings:
    return Settings(data_dir=Path(os.environ.get("DATAPROCESSOR_DATA_DIR", "data")))
```

`os.environ.get(nome, padrao)` devolve o valor da variável, ou o padrão se ela não
existir — então o comportamento atual (`data/`) é preservado sem configurar nada.

Agora `obter_fonte` pede as configurações da mesma forma que `obter_resultado` pede a
fonte, usando `Depends`:

```python
from .config import Settings, obter_settings


def obter_fonte(settings: Settings = Depends(obter_settings)) -> FonteDados:
    pasta = settings.data_dir
    return fonte_a_partir_de_caminhos(pasta / "clientes.csv", pasta / "transacoes.csv", pasta / "config.json")
```

A cadeia completa de dependências ficou:

```text
obter_settings  ->  obter_fonte  ->  obter_resultado  ->  rota
(ambiente)          (infra)          (service)            (HTTP)
```

Cada elo pode ser substituído isoladamente em um teste, e nenhum conhece o elo anterior
além do tipo que recebe.

### Verificação 1

Copie os dados para outra pasta e aponte a API para ela:

```bash
cp -r data /tmp/dados-alternativos
DATAPROCESSOR_DATA_DIR=/tmp/dados-alternativos uvicorn dataprocessor.interfaces.api:app
curl http://127.0.0.1:8000/metricas
```

Depois aponte para uma pasta que não existe e confirme que a resposta é `503` com a
mensagem `Fonte de dados indisponível`.

!!! warning "Por que não gravar segredos no código?"

    Hoje o único valor é um caminho. Amanhã será a URL de um banco de dados com usuário
    e senha. O hábito de ler configuração do ambiente — nunca do repositório — começa
    aqui, quando o custo de errar é zero.

## 3. Dependências declaradas: `pyproject.toml`

A Aula 19 pediu `pip install fastapi uvicorn` à mão. Isso não é reproduzível: quem
clonar o projeto não sabe o que instalar. Crie `dataprocessor/pyproject.toml`:

```toml
[project]
name = "dataprocessor"
version = "0.1.0"
description = "DataProcessor — projeto do curso Fundamentos de Python"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
api = ["fastapi", "uvicorn", "httpx"]

[tool.setuptools.packages.find]
include = ["dataprocessor*"]
```

Há uma decisão deliberada aqui: `dependencies` está **vazia**. O núcleo e a CLI
continuam usando só a biblioteca padrão. FastAPI, Uvicorn e HTTPX ficam no grupo
opcional `api`, que só é instalado quando se quer a porta REST:

```bash
pip install -e ".[api]"
```

O `-e` (editable) instala o projeto *apontando* para a pasta atual, então editar o
código não exige reinstalar.

### Verificação 2

Em um ambiente virtual **novo**:

```bash
python -m venv .venv-teste
source .venv-teste/bin/activate
pip install -e ".[api]"
python -m unittest discover -s tests -v
```

Todos os testes, incluindo os da API, devem passar — sem nenhuma instalação manual
extra. Sem o `[api]`, os testes da API aparecem como `skipped`.

## 4. O que a Fase 2 mudou no projeto

| Antes (Aula 19)                    | Depois (Aula 25)                                             |
| ---------------------------------- | ------------------------------------------------------------ |
| 1 endpoint, caminhos fixos         | 7 rotas com filtros, 404, 422 e 503                          |
| Respostas sem contrato             | Schemas Pydantic descrevendo entrada e saída                 |
| Só leitura de arquivos             | Leitura de arquivos **e** `POST` com dados no corpo          |
| Sem testes de API                  | Suíte com `TestClient` e `dependency_overrides`              |
| `pip install` manual               | `pyproject.toml` com dependências opcionais                  |
| Caminho fixo no código             | Configuração por variável de ambiente                        |

E o que **não** mudou: `core/`, `services/` e as ABCs de `infra/` receberam zero linhas
novas de FastAPI. A API inteira vive em `interfaces/`.

## 5. Ponte para a Fase 3: onde o banco entra

Hoje `FonteDados` tem três métodos: `carregar_clientes`, `carregar_transacoes` e
`carregar_config`. Os dois primeiros devolvem listas de entidades. Um banco de dados é
outra implementação desse mesmo contrato:

```text
FonteDados (ABC)
├── FonteDadosArquivos   # CSV e JSON       (Aula 14)
├── FonteDadosMemoria    # testes            (Aula 14)
└── FonteDadosBanco      # SQLAlchemy        (Fase 3)
```

Para a API, basta mudar **uma função**:

```python
def obter_fonte(settings: Settings = Depends(obter_settings)) -> FonteDados:
    return FonteDadosBanco(settings.database_url)
```

Nenhuma rota muda. Nenhum teste de rota muda — eles já substituem `obter_fonte`. É a
mesma troca que você fez ao criar `FonteDadosMemoria`, agora com um motor de banco por
trás.

A Fase 3 vai acrescentar o que esta fase deixou de fora de propósito: persistir
registros (hoje o `POST /processar` calcula e esquece), `PUT`/`DELETE`, migrações e
transações.

## Desafio guiado

1. Crie `interfaces/config.py` com `Settings` e `obter_settings()`.
2. Faça `obter_fonte` depender de `obter_settings` via `Depends`.
3. Rode a API com `DATAPROCESSOR_DATA_DIR` apontando para outra pasta.
4. Crie o `pyproject.toml` com o grupo opcional `api`.
5. Reproduza a Verificação 2 em um ambiente virtual limpo.

## Desafio extra

Adicione `DATAPROCESSOR_LOG_LEVEL` a `Settings` (padrão `"INFO"`) e use-o para
configurar o `logging` da API, como a CLI já faz desde a Aula 15. Escreva um teste que
sobrescreve `obter_settings` com `dependency_overrides` e verifica o valor lido.

## Resumo da Fase 2

Cinco aulas transformaram um endpoint de demonstração em uma API com contrato, erros
bem definidos, testes e configuração por ambiente — sem tocar no núcleo. O padrão que
atravessa o curso inteiro se repetiu mais uma vez: **a regra de negócio é um só lugar e
as bordas se adaptam a ela**. Quando a Fase 3 trouxer o banco de dados, esse será o
critério de sucesso outra vez.
