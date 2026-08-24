import unittest

from dataprocessor.core.entidades import Cliente, Transacao
from dataprocessor.infra.fontes import FonteDados, FonteDadosArquivos, FonteDadosMemoria
from dataprocessor.services.processamento import executar_processamento


class ProcessamentoTestCase(unittest.TestCase):
    def test_fonte_dados_e_uma_abc(self):
        self.assertTrue(issubclass(FonteDadosArquivos, FonteDados))
        self.assertTrue(issubclass(FonteDadosMemoria, FonteDados))

        with self.assertRaises(TypeError):
            FonteDados()

        class FonteIncompleta(FonteDados):
            pass

        with self.assertRaises(TypeError):
            FonteIncompleta()

    def test_dataset_oficial_preserva_metricas_da_aula_11(self):
        from pathlib import Path

        from dataprocessor.infra.fontes import FonteDadosArquivos

        data = Path(__file__).resolve().parents[1] / "data"
        resultado = executar_processamento(
            FonteDadosArquivos(data / "clientes.csv", data / "transacoes.csv", data / "config.json")
        )

        self.assertEqual(len(resultado.clientes), 2)
        self.assertEqual(len(resultado.transacoes), 2)
        self.assertEqual(resultado.media_idade, 39.5)
        self.assertEqual(resultado.total_aprovado, 150.50)

    def test_service_aceita_fonte_em_memoria(self):
        fonte = FonteDadosMemoria(
            clientes=(
                Cliente(1, " Ana Lima ", "ANA@EMAIL.COM", 45, " joinville ", "2023-01-25"),
            ),
            transacoes=(
                Transacao(1, 1, 100.0, "roupas", "2023-05-10", "aprovado"),
            ),
            config={
                "categorias_validas": ["roupas"],
                "status_validos": ["aprovado"],
                "valor_minimo": 0,
            },
        )

        resultado = executar_processamento(fonte)

        self.assertEqual(len(resultado.clientes), 1)
        self.assertEqual(resultado.clientes[0].nome, "Ana Lima")
        self.assertEqual(resultado.total_aprovado, 100.0)


if __name__ == "__main__":
    unittest.main()
