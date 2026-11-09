import json
import unittest
from pathlib import Path

from painel.core.entidades import Aluno, Config, Nota
from painel.core.validador import ErroValidacao, validar_nota
from painel.infra.arquivos import ler_config, ler_csv
from painel.infra.relatorios import RelatorioJSON, RelatorioTexto
from painel.services.processamento import executar_processamento

CONFIG = Config(media_aprovacao=6.0, media_recuperacao=4.0, nota_maxima=10.0)
DATA = Path(__file__).resolve().parent.parent / "data"


def aluno_com(*valores: float) -> Aluno:
    return Aluno("1", "Teste", "3A", [Nota("1", "Mat", f"P{i}", v) for i, v in enumerate(valores)])


class TestSituacao(unittest.TestCase):
    def test_limites_de_situacao(self):
        self.assertEqual(aluno_com(6.0).situacao(CONFIG), "aprovado")
        self.assertEqual(aluno_com(5.9).situacao(CONFIG), "recuperação")
        self.assertEqual(aluno_com(4.0).situacao(CONFIG), "recuperação")
        self.assertEqual(aluno_com(3.9).situacao(CONFIG), "reprovado")

    def test_aluno_sem_notas(self):
        self.assertIsNone(aluno_com().media())
        self.assertEqual(aluno_com().situacao(CONFIG), "sem notas")

    def test_media(self):
        self.assertAlmostEqual(aluno_com(8.0, 6.0, 7.0).media(), 7.0)


class TestValidacaoNota(unittest.TestCase):
    def validar(self, **campos):
        registro = {"matricula": "1", "disciplina": "Mat", "avaliacao": "P1", "nota": "7.0", **campos}
        return validar_nota(2, registro, {"1"}, set(), CONFIG)

    def test_nota_valida_remove_espacos(self):
        nota = self.validar(disciplina="  Mat ", nota=" 7.5")
        self.assertEqual((nota.disciplina, nota.valor), ("Mat", 7.5))

    def test_tipos_de_erro(self):
        casos = {
            "nota": [("", "campo_vazio"), ("oito", "nota_invalida"), ("NA", "nota_invalida"),
                     ("nan", "nota_invalida"), ("11", "nota_fora_do_intervalo"),
                     ("-0.5", "nota_fora_do_intervalo")],
            "matricula": [("9", "matricula_inexistente")],
        }
        for campo, itens in casos.items():
            for valor, tipo in itens:
                with self.subTest(campo=campo, valor=valor):
                    resultado = self.validar(**{campo: valor})
                    self.assertIsInstance(resultado, ErroValidacao)
                    self.assertEqual(resultado.tipo, tipo)

    def test_avaliacao_duplicada(self):
        registro = {"matricula": "1", "disciplina": "Mat", "avaliacao": "P1", "nota": "7"}
        resultado = validar_nota(3, registro, {"1"}, {("1", "Mat", "P1")}, CONFIG)
        self.assertEqual(resultado.tipo, "avaliacao_duplicada")


class TestProcessamento(unittest.TestCase):
    def test_pipeline_em_memoria_nao_para_com_erros(self):
        alunos = [(2, {"matricula": "1", "nome": "Ana", "turma": "3A"}),
                  (3, {"matricula": "2", "nome": "Bia", "turma": "3A"})]
        notas = [(2, {"matricula": "1", "disciplina": "Mat", "avaliacao": "P1", "nota": "8"}),
                 (3, {"matricula": "1", "disciplina": "Mat", "avaliacao": "P2", "nota": "x"}),
                 (4, {"matricula": "2", "disciplina": "Mat", "avaliacao": "P1", "nota": "3"})]
        r = executar_processamento(alunos, notas, CONFIG)
        self.assertEqual((r.notas_validas, r.notas_invalidas), (2, 1))
        self.assertEqual([e.linha for e in r.erros], [3])
        self.assertEqual(r.contagem_situacoes(), {"aprovado": 1, "reprovado": 1})
        self.assertEqual(r.medias_disciplinas, {"Mat": 5.5})


class TestDatasetCompleto(unittest.TestCase):
    """Confere o resultado com o gabarito dos erros plantados no dataset."""

    @classmethod
    def setUpClass(cls):
        cls.r = executar_processamento(
            ler_csv(DATA / "alunos.csv"), ler_csv(DATA / "notas.csv"), ler_config(DATA / "config.json")
        )

    def test_erros_batem_com_o_gabarito(self):
        gabarito = json.loads((Path(__file__).parent / "gabarito_erros.json").read_text())
        esperado = {(a, e["linha"], e["tipo"]) for a, v in gabarito.items() for e in v}
        obtido = {(e.arquivo, e.linha, e.tipo) for e in self.r.erros}
        self.assertEqual(obtido, esperado)

    def test_totais(self):
        self.assertEqual(len(self.r.alunos), 32)
        self.assertEqual((self.r.notas_validas, self.r.notas_invalidas), (457, 27))

    def test_relatorios_renderizam(self):
        dados = json.loads(RelatorioJSON().render(self.r))
        self.assertEqual(len(dados["erros"]), 30)
        self.assertIn("PAINEL DE NOTAS", RelatorioTexto().render(self.r))


if __name__ == "__main__":
    unittest.main()
