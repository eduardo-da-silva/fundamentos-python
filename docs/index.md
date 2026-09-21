# Fundamentos de Python

Bem-vindo ao curso de **Fundamentos de Python** — um bootcamp hands-on de 80 horas para quem já conhece lógica de programação e JavaScript.

Este material foi desenvolvido para o curso técnico de nível médio, pelo prof. Eduardo da Silva. O conteúdo é melhor aproveitado durante as atividades realizadas em sala de aula.

---

## Sobre o curso

Este curso **não ensina Python do zero**. O ponto de partida é que você já sabe pensar em código — variáveis, condicionais, laços, funções — provavelmente com JavaScript.

Aqui o foco é diferente:

- Aprender Python de forma **prática e profissional**
- Desenvolver raciocínio de **manipulação de dados**
- Construir base sólida para **backend com FastAPI** (fase 2)
- Entender como Python é usado em contextos reais

Ao final deste curso, você terá construído um sistema CLI funcional do zero: o **DataProcessor**.

---

## Projeto do curso — DataProcessor CLI

Durante todo o curso, você vai construir o **DataProcessor CLI**, um consolidador de dados que:

- Lê arquivos **CSV** e **JSON**
- Valida dados inconsistentes
- Transforma e normaliza informações
- Cruza dados entre arquivos
- Gera relatórios consolidados
- Salva arquivos de saída e logs
- Roda via **linha de comando**

Nenhum banco de dados. Nenhum framework web. Python puro com bibliotecas padrão.

---

## Trilha do curso

Este curso faz parte de uma trilha de aprendizado:

- **Lógica de Programação com JavaScript** — pré-requisito ✓
- **Fundamentos de Python** ← você está aqui
- **Desenvolvimento Web com FastAPI** (fase 2)
- **Banco de Dados com SQLAlchemy / PostgreSQL** (fase 3)

---

## Estrutura das aulas

### Fase 1 — Fundamentos (Aulas 01–05)

Sintaxe, listas e dicionários, loops, funções, leitura de CSV/JSON, validação e
transformação de dados. Ao final, o primeiro pipeline funcional do DataProcessor.

**[Ir para a Aula 01](aulas/aula-01-introducao.md)**

### Módulo 5 — Arquitetura e organização (Aulas 06–10)

Diagnóstico arquitetural, migração para package, camadas `core`/`infra`/`services` e
configuração centralizada — sem alterar o comportamento funcional.

**[Ir para a Aula 06](aulas/aula-06-arquitetura-crescimento.md)**

### Módulo 6 — POO aplicada (Aulas 11–15)

Entidades com `dataclass`, comportamento e testes, relatórios polimórficos com `ABC`,
fontes de dados intercambiáveis, CLI e logging.

**[Ir para a Aula 11](aulas/aula-11-entidades-dataclass.md)**

### Módulo 7 — Interfaces e portas de entrada (Aulas 16–20)

Menu interativo em texto, isolamento testável da porta de entrada, um endpoint REST de
demonstração com FastAPI e o fechamento do curso com o nome do padrão construído:
arquitetura hexagonal.

**[Ir para a Aula 16](aulas/aula-16-menu-interativo.md)**

**[Ir para o índice completo das aulas](aulas/index.md)**

---

## Como usar este material

- Acompanhe as aulas **com o código aberto no editor**
- Cada aula tem um **desafio guiado** (feito em sala) e um **desafio extra** (para casa)
- Os exemplos usam sempre o mesmo dataset — os mesmos arquivos que você vai trabalhar no projeto

Bons estudos!
