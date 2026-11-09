import contextlib
import io
import unittest
from unittest.mock import patch

from dataprocessor.interfaces.menu import menu_principal, processar_caminhos

CAMINHOS_PADRAO = ("data/clientes.csv", "data/transacoes.csv", "data/config.json")


def executar_menu(entradas: list[str]) -> str:
    saida = io.StringIO()
    with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida):
        menu_principal()
    return saida.getvalue()


class ProcessarCaminhosTestCase(unittest.TestCase):
    def test_processa_dataset_padrao(self):
        resultado = processar_caminhos(*CAMINHOS_PADRAO)
        self.assertEqual(resultado.total_aprovado, 150.50)

    def test_arquivo_inexistente_levanta_oserror(self):
        with self.assertRaises(OSError):
            processar_caminhos("nao-existe.csv", *CAMINHOS_PADRAO[1:])


class MenuTestCase(unittest.TestCase):
    def test_exibir_antes_de_processar_avisa(self):
        saida = executar_menu(["2", "3"])
        self.assertIn("Nenhum dado processado ainda", saida)

    def test_opcao_invalida_avisa(self):
        saida = executar_menu(["9", "3"])
        self.assertIn("Opção inválida: '9'", saida)

    def test_erro_de_processamento_mantem_menu(self):
        saida = executar_menu(["1", "nao-existe.csv", "", "", "3"])
        self.assertIn("[ERRO]", saida)

    def test_falha_nao_apaga_resultado_anterior(self):
        saida = executar_menu(["1", "", "", "", "1", "nao-existe.csv", "", "", "2", "json", "3"])
        self.assertIn('"total_aprovado": 150.5', saida)

    def test_formato_invalido_avisa(self):
        saida = executar_menu(["1", "", "", "", "2", "xml", "3"])
        self.assertIn("Formato inválido: 'xml'", saida)


if __name__ == "__main__":
    unittest.main()
