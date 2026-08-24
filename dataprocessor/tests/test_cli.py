import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTestCase(unittest.TestCase):
    def test_cli_salva_relatorio_json_e_log(self):
        projeto = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta)
            processo = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "dataprocessor",
                    "--clientes",
                    str(projeto / "data/clientes.csv"),
                    "--transacoes",
                    str(projeto / "data/transacoes.csv"),
                    "--config",
                    str(projeto / "data/config.json"),
                    "--formato",
                    "json",
                    "--output",
                    str(saida),
                ],
                cwd=projeto,
                capture_output=True,
                text=True,
            )

            self.assertEqual(processo.returncode, 0, processo.stderr)
            relatorio = json.loads((saida / "relatorio.json").read_text(encoding="utf-8"))
            self.assertEqual(relatorio["metricas"]["total_aprovado"], 150.50)
            self.assertTrue((saida / "dataprocessor.log").exists())


if __name__ == "__main__":
    unittest.main()
