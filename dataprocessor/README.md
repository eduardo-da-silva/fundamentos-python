# DataProcessor CLI

Projeto executável usado nas Aulas 12–15 de Fundamentos de Python.

## Executar

```bash
python -m dataprocessor \
  --clientes data/clientes.csv \
  --transacoes data/transacoes.csv \
  --config data/config.json \
  --formato texto \
  --output output/
```

## Testar

```bash
python -m unittest discover -s tests -v
```
