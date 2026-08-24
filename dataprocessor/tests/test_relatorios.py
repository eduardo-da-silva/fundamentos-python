import json
import unittest

from dataprocessor.core.entidades import Cliente, Transacao
from dataprocessor.core.resultados import ResultadoProcessamento
from dataprocessor.infra.relatorios import (
    GeradorRelatorio,
    RelatorioCsv,
    RelatorioJson,
    RelatorioTexto,
)


def resultado_exemplo():
    return ResultadoProcessamento(
        clientes=(
            Cliente(1, "Joao Silva", "joao@email.com", 34, "Joinville", "2023-01-10"),
        ),
        transacoes=(
            Transacao(1, 1, 150.50, "eletronicos", "2023-05-10", "aprovado"),
        ),
        clientes_invalidos=(),
        transacoes_invalidas=(),
        media_idade=34.0,
        total_aprovado=150.50,
    )


class RelatoriosTestCase(unittest.TestCase):
    def test_gerador_relatorio_e_uma_abc(self):
        self.assertTrue(issubclass(RelatorioTexto, GeradorRelatorio))

        with self.assertRaises(TypeError):
            GeradorRelatorio()

        class GeradorIncompleto(GeradorRelatorio):
            pass

        with self.assertRaises(TypeError):
            GeradorIncompleto()

    def test_relatorio_texto_exibe_metricas(self):
        texto = RelatorioTexto().render(resultado_exemplo())

        self.assertIn("Clientes válidos: 1", texto)
        self.assertIn("Média de idade: 34.0", texto)
        self.assertIn("Total aprovado: R$ 150.50", texto)

    def test_relatorio_json_preserva_dados_do_resultado(self):
        documento = json.loads(RelatorioJson().render(resultado_exemplo()))

        self.assertEqual(documento["clientes"][0]["nome"], "Joao Silva")
        self.assertEqual(documento["metricas"]["total_aprovado"], 150.50)

    def test_relatorio_csv_produz_cabecalho_e_linhas(self):
        csv = RelatorioCsv().render(resultado_exemplo())

        self.assertIn("id,nome,email,idade,cidade,data_cadastro", csv)
        self.assertIn("1,Joao Silva,joao@email.com,34,Joinville,2023-01-10", csv)


if __name__ == "__main__":
    unittest.main()
