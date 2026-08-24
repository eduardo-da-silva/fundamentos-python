import unittest

from dataprocessor.core.entidades import Cliente, Transacao


class EntidadesTestCase(unittest.TestCase):
    def test_cliente_exibe_identificacao_derivada(self):
        cliente = Cliente(
            id=5,
            nome="Pedro Santos",
            email="",
            idade=38,
            cidade="Sao Paulo",
            data_cadastro="2023-02-30",
        )

        self.assertEqual(cliente.identificacao, "#5 Pedro Santos")

    def test_transacao_informa_se_foi_aprovada(self):
        transacao = Transacao(
            id=1,
            cliente_id=1,
            valor=150.50,
            categoria="eletronicos",
            data="2023-05-10",
            status="aprovado",
        )

        self.assertTrue(transacao.esta_aprovada)

    def test_entidades_sao_imutaveis(self):
        cliente = Cliente(1, "Joao", "joao@email.com", 30, "Joinville", "2023-01-01")

        with self.assertRaises(AttributeError):
            cliente.nome = "Outro nome"


if __name__ == "__main__":
    unittest.main()
