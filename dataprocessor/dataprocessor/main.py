import argparse
import logging
from pathlib import Path

from .infra.fontes import FonteDadosArquivos
from .infra.relatorios import criar_gerador
from .services.processamento import executar_processamento


def configurar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Processa clientes e transações.")
    parser.add_argument("--clientes", required=True, help="Caminho do CSV de clientes.")
    parser.add_argument("--transacoes", required=True, help="Caminho do CSV de transações.")
    parser.add_argument("--config", required=True, help="Caminho do JSON de configuração.")
    parser.add_argument("--formato", choices=("texto", "json", "csv"), default="texto")
    parser.add_argument("--output", type=Path, default=Path("output"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = configurar_parser().parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    log_path = args.output / "dataprocessor.log"
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.info("Iniciando processamento")
    try:
        fonte = FonteDadosArquivos(args.clientes, args.transacoes, args.config)
        resultado = executar_processamento(fonte)
        relatorio = criar_gerador(args.formato).render(resultado)
        nome = "relatorio.txt" if args.formato == "texto" else f"relatorio.{args.formato}"
        (args.output / nome).write_text(relatorio, encoding="utf-8")
        logging.info(
            "Processamento concluído: %d clientes e %d transações válidos",
            len(resultado.clientes),
            len(resultado.transacoes),
        )
        print(relatorio, end="")
        return 0
    except (OSError, ValueError, KeyError) as erro:
        logging.exception("Falha no processamento")
        print(f"[ERRO] {erro}")
        return 1
