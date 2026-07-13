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

---

## Módulo 5 — Arquitetura e Organização de Projetos Python

Neste módulo, o projeto **não ganha funcionalidades novas**. Ele ganha organização.

- O comportamento funcional deve permanecer igual
- A estrutura evolui gradualmente, aula a aula
- O foco é preparar o terreno para POO no próximo módulo

!!! note "Diretriz do módulo"

	Refatorar arquitetura sem quebrar regra de negócio é habilidade profissional central.

## Dataset do curso

Todos os exemplos usam os mesmos arquivos de dados: `clientes.csv`, `transacoes.csv` e `config.json`.

Acesse os datasets na seção **[Datasets](../datasets/index.md)**.
