# Aulas

Todas as aulas do curso são organizadas em sequência, agrupadas em módulos. Cada uma tem teoria, exemplos práticos e desafios conectados ao projeto **DataProcessor CLI**.

## Fase 1 — Fundamentos

Nas cinco primeiras aulas, o projeto ganha corpo: dados hardcoded viram um pipeline
funcional que lê arquivos reais, valida, transforma e calcula métricas.

| Aula                               | Tema                         | Conteúdo-chave                                  |
| ---------------------------------- | ---------------------------- | ----------------------------------------------- |
| [01](aula-01-introducao.md)        | Introdução prática ao Python | Sintaxe, listas, dicionários, comparação com JS |
| [02](aula-02-manipulacao-dados.md) | Manipulação de dados         | Loops, funções, agregação                       |
| [03](aula-03-leitura-arquivos.md)  | Leitura de arquivos          | CSV, JSON, `csv` module, `json` module          |
| [04](aula-04-validacao.md)         | Validação de dados           | Funções de validação, exceptions, dados sujos   |
| [05](aula-05-transformacao.md)     | Transformação de dados       | Normalização, limpeza, padronização             |

## Módulo 5 — Arquitetura e organização

Neste módulo, o projeto **não ganha funcionalidades novas**. Ele ganha organização.

| Aula                               | Tema                         | Conteúdo-chave                                  |
| ---------------------------------- | ---------------------------- | ----------------------------------------------- |
| [06](aula-06-arquitetura-crescimento.md) | Crescimento e arquitetura | Revisão estrutural, responsabilidade de módulos |
| [07](aula-07-packages-imports.md)  | Packages e imports           | `__init__.py`, imports absolutos e relativos    |
| [08](aula-08-camada-core.md)       | Camada core                  | Regras puras, separação de negócio              |
| [09](aula-09-camada-services.md)   | Camada services              | Casos de uso, orquestração e infraestrutura     |
| [10](aula-10-configuracao-organizacao.md) | Configuração e consolidação | Organização final pré-POO                       |

- O comportamento funcional deve permanecer igual
- A estrutura evolui gradualmente, aula a aula
- O foco é preparar o terreno para POO no próximo módulo

!!! note "Diretriz do módulo"

	Refatorar arquitetura sem quebrar regra de negócio é habilidade profissional central.

## Módulo 6 — POO aplicada

A partir da Aula 11 o projeto volta a **crescer em funcionalidade**, e cada recurso novo
justifica um conceito de orientação a objetos.

| Aula                               | Tema                         | Conteúdo-chave                                  |
| ---------------------------------- | ---------------------------- | ----------------------------------------------- |
| [11](aula-11-entidades-dataclass.md) | Entidades com `dataclass` | `@dataclass`, `frozen=True`, `replace()`     |
| [12](aula-12-comportamento-entidades.md) | Comportamento nas entidades | `@property`, imutabilidade e testes |
| [13](aula-13-relatorios-polimorfismo.md) | ABC e relatórios polimórficos | `ABC`, herança, texto, JSON e CSV |
| [14](aula-14-fontes-dados-abc.md) | ABC para fontes de dados | Herança e fonte em memória |
| [15](aula-15-cli-logging-integracao.md) | CLI e integração | `argparse`, logging e entrega final |

- entidades explícitas no lugar de dicionários (Aula 11)
- comportamento nas entidades e testes automatizados (Aula 12)
- relatórios em vários formatos exigindo polimorfismo (Aula 13)
- origens de dados intercambiáveis exigindo contrato de interface (Aula 14)
- CLI e logging fechando o ciclo do DataProcessor (Aula 15)

!!! note "Diretriz do módulo"

	Classe nova só entra quando um requisito novo pede. POO não é enfeite de arquitetura.

## Módulo 7 — Interfaces e portas de entrada

As Aulas 16 a 20 provam, na prática, o que a arquitetura em camadas prometeu desde o
Módulo 5: trocar a forma de entrada não exige tocar em `core` nem em `services`.

| Aula                               | Tema                         | Conteúdo-chave                                  |
| ---------------------------------- | ---------------------------- | ----------------------------------------------- |
| [16](aula-16-menu-interativo.md) | Menu interativo em texto | `while`, `input()`, despacho de opções |
| [17](aula-17-robustez-menu.md) | Estado de sessão e robustez do menu | Validação de entrada, tratamento de erros |
| [18](aula-18-porta-de-entrada.md) | Isolando a porta de entrada | Função pura, testes sem `input()` |
| [19](aula-19-trailer-rest-fastapi.md) | Trailer: REST com FastAPI | Endpoint mínimo, `@app.get`, decorators |
| [20](aula-20-arquitetura-hexagonal.md) | Arquitetura hexagonal e fechamento | Ports & adapters, revisão do curso |

- menu interativo em texto, reaproveitando o service já pronto (Aula 16)
- estado de sessão e tratamento de erros no menu (Aula 17)
- isolamento da porta de entrada em uma função pura e testável (Aula 18)
- o mesmo núcleo atrás de um endpoint REST, como prévia da Fase 2 (Aula 19)
- nome e diagrama para o padrão construído: arquitetura hexagonal (Aula 20)

!!! note "Diretriz do módulo"

	Cada nova porta de entrada é uma prova da arquitetura, não uma funcionalidade isolada.

## Módulo 8 — API REST com FastAPI

A Fase 2 transforma o trailer da Aula 19 em uma API completa — e o `core` continua sem
uma linha nova.

| Aula                               | Tema                         | Conteúdo-chave                                  |
| ---------------------------------- | ---------------------------- | ----------------------------------------------- |
| [21](aula-21-multiplos-endpoints.md) | Múltiplos endpoints | Parâmetros de rota e de consulta, `Response` |
| [22](aula-22-schemas-pydantic.md) | Schemas Pydantic | `response_model`, `Literal`, `POST` com corpo |
| [23](aula-23-erros-http-dependencias.md) | Erros HTTP e dependências | `HTTPException`, `exception_handler`, `Depends` |
| [24](aula-24-testando-a-api.md) | Testando a API | `TestClient`, `dependency_overrides` |
| [25](aula-25-configuracao-fechamento.md) | Configuração e fechamento | Variáveis de ambiente, `pyproject.toml` |

- várias rotas de leitura com filtros e formatos (Aula 21)
- contrato de entrada e saída separado da regra de negócio (Aula 22)
- códigos de status corretos e fonte de dados injetada (Aula 23)
- testes da API sem servidor, rede ou arquivos (Aula 24)
- configuração por ambiente e dependências declaradas (Aula 25)

!!! note "Diretriz do módulo"

	O Pydantic valida a forma; o `core` valida o negócio. Nenhuma regra mora na rota.

## Dataset do curso

Todos os exemplos usam os mesmos arquivos de dados: `clientes.csv`, `transacoes.csv` e `config.json`.

Acesse os datasets na seção **[Datasets](../datasets/index.md)**.
