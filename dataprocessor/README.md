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

## Menu interativo (Aulas 16–18)

```bash
python -m dataprocessor.interfaces.menu
```

## API REST (Aulas 19–25)

```bash
pip install -e ".[api]"
uvicorn dataprocessor.interfaces.api:app --reload
# outra pasta de dados:
DATAPROCESSOR_DATA_DIR=/caminho/dados uvicorn dataprocessor.interfaces.api:app
```

Documentação interativa em `http://127.0.0.1:8000/docs`.
