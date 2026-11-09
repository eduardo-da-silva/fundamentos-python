import argparse
import logging
import sys
from pathlib import Path

from painel.infra.arquivos import ler_config, ler_csv
from painel.infra.relatorios import GERADORES
from painel.services.processamento import executar_processamento

log = logging.getLogger("painel")


def criar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="painel", description="Painel de Notas da Turma")
    p.add_argument("--alunos", type=Path, required=True)
    p.add_argument("--notas", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--formato", choices=sorted(GERADORES), default="texto")
    p.add_argument("--output", type=Path, default=Path("output"))
    return p


def main(argv: list[str] | None = None) -> int:
    args = criar_parser().parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=args.output / "painel.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    try:
        resultado = executar_processamento(
            ler_csv(args.alunos), ler_csv(args.notas), ler_config(args.config)
        )
    except (OSError, KeyError, ValueError) as exc:
        log.error("falha ao processar: %s", exc)
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    for erro in resultado.erros:
        log.warning("%s:%s %s", erro.arquivo, erro.linha, erro.motivo)
    destino = GERADORES[args.formato]().salvar(resultado, args.output)
    log.info("relatório gerado em %s", destino)
    print(f"Relatório gerado em {destino} ({len(resultado.erros)} erro(s) registrados)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
