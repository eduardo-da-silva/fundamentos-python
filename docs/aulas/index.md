# Aulas

Todas as aulas do curso são organizadas em sequência. Cada uma tem teoria, exemplos práticos e desafios conectados ao projeto **DataProcessor CLI**.

| Aula                               | Tema                         | Conteúdo-chave                                  |
| ---------------------------------- | ---------------------------- | ----------------------------------------------- |
| [01](aula-01-introducao.md)        | Introdução prática ao Python | Sintaxe, listas, dicionários, comparação com JS |
| [02](aula-02-manipulacao-dados.md) | Manipulação de dados         | Loops, funções, agregação                       |
| [03](aula-03-leitura-arquivos.md)  | Leitura de arquivos          | CSV, JSON, `csv` module, `json` module          |
| [04](aula-04-validacao.md)         | Validação de dados           | Funções de validação, exceptions, dados sujos   |
| [05](aula-05-transformacao.md)     | Transformação de dados       | Normalização, limpeza, padronização             |
| [06](aula-06-arquitetura-crescimento.md) | Crescimento e arquitetura | Revisão estrutural, responsabilidade de módulos |
| [07](aula-07-packages-imports.md)  | Packages e imports           | `__init__.py`, imports absolutos e relativos    |
| [08](aula-08-camada-core.md)       | Camada core                  | Regras puras, separação de negócio              |
| [09](aula-09-camada-services.md)   | Camada services              | Casos de uso, orquestração e infraestrutura     |
| [10](aula-10-configuracao-organizacao.md) | Configuração e consolidação | Organização final pré-POO                       |
| [11](aula-11-entidades-dataclass.md) | Entidades com `dataclass` | `@dataclass`, `frozen=True`, `replace()`     |
| [12](aula-12-comportamento-entidades.md) | Comportamento nas entidades | `@property`, imutabilidade e testes |
| [13](aula-13-relatorios-polimorfismo.md) | ABC e relatórios polimórficos | `ABC`, herança, texto, JSON e CSV |
| [14](aula-14-fontes-dados-abc.md) | ABC para fontes de dados | Herança e fonte em memória |
| [15](aula-15-cli-logging-integracao.md) | CLI e integração | `argparse`, logging e entrega final |

---

## Módulo 5 — Arquitetura e Organização de Projetos Python

Neste módulo, o projeto **não ganha funcionalidades novas**. Ele ganha organização.

- O comportamento funcional deve permanecer igual
- A estrutura evolui gradualmente, aula a aula
- O foco é preparar o terreno para POO no próximo módulo

!!! note "Diretriz do módulo"

	Refatorar arquitetura sem quebrar regra de negócio é habilidade profissional central.

## Módulo 6 — POO aplicada

A partir da Aula 11 o projeto volta a **crescer em funcionalidade**, e cada recurso novo
justifica um conceito de orientação a objetos:

- entidades explícitas no lugar de dicionários (Aula 11)
- comportamento nas entidades e testes automatizados (Aula 12)
- relatórios em vários formatos exigindo polimorfismo (Aula 13)
- origens de dados intercambiáveis exigindo contrato de interface (Aula 14)
- CLI e logging fechando o ciclo do DataProcessor (Aula 15)

!!! note "Diretriz do módulo"

	Classe nova só entra quando um requisito novo pede. POO não é enfeite de arquitetura.

## Dataset do curso

Todos os exemplos usam os mesmos arquivos de dados: `clientes.csv`, `transacoes.csv` e `config.json`.

Acesse os datasets na seção **[Datasets](../datasets/index.md)**.
