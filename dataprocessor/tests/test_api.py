import unittest

try:
    from fastapi.testclient import TestClient

    from dataprocessor.core.entidades import Cliente, Transacao
    from dataprocessor.infra.fontes import FonteDadosMemoria
    from dataprocessor.interfaces.api import app, obter_fonte
except ImportError:  # fastapi/httpx são opcionais (Aulas 19 a 25)
    app = None

CONFIG = {
    "categorias_validas": ["eletronicos", "livros"],
    "status_validos": ["aprovado", "pendente", "recusado"],
    "valor_minimo": 0,
}


def fonte_de_teste():
    return FonteDadosMemoria(
        clientes=[
            Cliente(1, "Ana Lima", "ana@email.com", 40, "Joinville", "2023-01-10"),
            Cliente(2, "Bia Souza", "bia@email.com", 20, "Blumenau", "2023-02-15"),
            Cliente(3, "Sem Email", "", 30, "Curitiba", "2023-03-20"),
        ],
        transacoes=[
            Transacao(1, 1, 100.0, "livros", "2023-05-10", "aprovado"),
            Transacao(2, 2, 50.0, "eletronicos", "2023-05-11", "pendente"),
            Transacao(3, 1, 25.0, "livros", "2023-05-12", "aprovado"),
        ],
        config=CONFIG,
    )


@unittest.skipIf(app is None, "fastapi/httpx não instalados")
class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[obter_fonte] = fonte_de_teste
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_metricas(self):
        corpo = self.client.get("/metricas").json()
        self.assertEqual(corpo["clientes_validos"], 2)
        self.assertEqual(corpo["clientes_invalidos"], 1)
        self.assertEqual(corpo["total_aprovado"], 125.0)
        self.assertEqual(corpo["media_idade"], 30.0)

    def test_lista_clientes_validos(self):
        corpo = self.client.get("/clientes").json()
        self.assertEqual([c["nome"] for c in corpo], ["Ana Lima", "Bia Souza"])

    def test_cliente_existente(self):
        resposta = self.client.get("/clientes/2")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["nome"], "Bia Souza")

    def test_cliente_inexistente_devolve_404(self):
        resposta = self.client.get("/clientes/99")
        self.assertEqual(resposta.status_code, 404)
        self.assertIn("99", resposta.json()["detail"])

    def test_id_nao_numerico_devolve_422(self):
        self.assertEqual(self.client.get("/clientes/abc").status_code, 422)

    def test_filtra_transacoes_por_status(self):
        corpo = self.client.get("/transacoes", params={"status": "aprovado"}).json()
        self.assertEqual([t["id"] for t in corpo], [1, 3])

    def test_filtros_combinados(self):
        corpo = self.client.get("/transacoes", params={"status": "aprovado", "cliente_id": 1, "categoria": "livros"}).json()
        self.assertEqual(len(corpo), 2)

    def test_status_invalido_devolve_422(self):
        self.assertEqual(self.client.get("/transacoes", params={"status": "xyz"}).status_code, 422)

    def test_relatorio_csv_tem_content_type(self):
        resposta = self.client.get("/relatorio/csv")
        self.assertTrue(resposta.headers["content-type"].startswith("text/csv"))
        self.assertIn("Ana Lima", resposta.text)

    def test_formato_invalido_devolve_422(self):
        self.assertEqual(self.client.get("/relatorio/xml").status_code, 422)

    def test_relatorio_json_completo(self):
        corpo = self.client.get("/relatorio").json()
        self.assertEqual(corpo["metricas"]["total_aprovado"], 125.0)

    def test_fonte_indisponivel_devolve_503(self):
        from dataprocessor.infra.fontes import FonteDadosArquivos

        app.dependency_overrides[obter_fonte] = lambda: FonteDadosArquivos("x.csv", "y.csv", "z.json")
        resposta = TestClient(app).get("/metricas")
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("indisponível", resposta.json()["detail"])


@unittest.skipIf(app is None, "fastapi/httpx não instalados")
class ProcessarTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def corpo(self, **mudancas):
        base = {
            "clientes": [{"id": 1, "nome": "Ana", "email": "ana@email.com", "idade": 30, "cidade": "Joinville", "data_cadastro": "2023-01-10"}],
            "transacoes": [{"id": 1, "cliente_id": 1, "valor": 10.5, "categoria": "livros", "data": "2023-05-10", "status": "aprovado"}],
            "config": CONFIG,
        }
        base.update(mudancas)
        return base

    def test_processa_corpo_valido(self):
        resposta = self.client.post("/processar", json=self.corpo())
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["total_aprovado"], 10.5)

    def test_regra_de_negocio_ainda_vem_do_core(self):
        transacao = {"id": 1, "cliente_id": 1, "valor": 10.5, "categoria": "inexistente", "data": "2023-05-10", "status": "aprovado"}
        corpo = self.client.post("/processar", json=self.corpo(transacoes=[transacao])).json()
        self.assertEqual(corpo["transacoes_invalidas"], 1)

    def test_corpo_mal_formado_devolve_422(self):
        resposta = self.client.post("/processar", json={"clientes": "nao-e-lista"})
        self.assertEqual(resposta.status_code, 422)


class ConfigTestCase(unittest.TestCase):
    def test_data_dir_vem_da_variavel_de_ambiente(self):
        import os
        from unittest.mock import patch

        from dataprocessor.interfaces.config import obter_settings

        with patch.dict(os.environ, {"DATAPROCESSOR_DATA_DIR": "/tmp/outros"}):
            self.assertEqual(str(obter_settings().data_dir), "/tmp/outros")
        with patch.dict(os.environ, clear=True):
            self.assertEqual(str(obter_settings().data_dir), "data")


if __name__ == "__main__":
    unittest.main()
