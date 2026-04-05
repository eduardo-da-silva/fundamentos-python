# Datasets do curso

Estes são os arquivos de dados usados em todas as aulas. Os dados contêm inconsistências **propositais** — identificar e corrigir esses problemas é parte do aprendizado.

---

## clientes.csv

Baixar: [clientes.csv](../assets/dados/clientes.csv)

```csv
id,nome,email,idade,cidade,data_cadastro
1,João Silva,joao.silva@email.com,34,Joinville,2023-01-10
2,Maria Souza,maria@email,28,Florianopolis,2023-02-15
3,Carlos Pereira,carlos.pereira@email.com,-5,Curitiba,2023-03-20
4,Ana Lima,ana.lima@email.com,45,Joinville,2023-01-25
5,Pedro Santos,,38,Sao Paulo,2023-02-30
```

### Problemas nos dados

| ID  | Campo           | Problema                                                   |
| --- | --------------- | ---------------------------------------------------------- |
| 2   | `email`         | `maria@email` — domínio inválido (falta `.com` ou similar) |
| 3   | `idade`         | `-5` — valor negativo                                      |
| 5   | `email`         | campo vazio                                                |
| 5   | `data_cadastro` | `2023-02-30` — fevereiro não tem dia 30                    |

---

## transacoes.csv

Baixar: [transacoes.csv](../assets/dados/transacoes.csv)

```csv
id,cliente_id,valor,categoria,data,status
1,1,150.50,eletronicos,2023-05-10,aprovado
2,2,200.00,roupas,2023-05-11,pendente
3,3,-50.00,alimentacao,2023-05-12,aprovado
4,1,300.00,eletronicos,2023-05-13,recusado
5,10,120.00,livros,2023-05-14,aprovado
```

### Problemas nos dados

| ID  | Campo        | Problema                            |
| --- | ------------ | ----------------------------------- |
| 3   | `valor`      | `-50.00` — valor negativo           |
| 5   | `cliente_id` | `10` — não existe cliente com ID 10 |

---

## config.json

Baixar: [config.json](../assets/dados/config.json)

```json
{
  "categorias_validas": ["eletronicos", "roupas", "alimentacao", "livros"],
  "status_validos": ["aprovado", "pendente", "recusado"],
  "valor_minimo": 0
}
```

Este arquivo define as regras de negócio usadas na validação. O DataProcessor carrega esse arquivo para saber o que é válido — não tem nada hardcoded no código.

---

## Como usar esses arquivos

Crie a pasta `data/` na raiz do seu projeto e coloque os três arquivos lá:

```
dataprocessor/
    main.py
    leitor.py
    validador.py
    transformador.py
    data/
        clientes.csv       ← aqui
        transacoes.csv     ← aqui
        config.json        ← aqui
```
