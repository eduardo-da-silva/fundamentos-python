from painel.core.entidades import Aluno, Config, Nota
from painel.core.metricas import media_por_disciplina
from painel.core.resultados import ResultadoProcessamento
from painel.core.validador import ErroValidacao, validar_aluno, validar_nota


def executar_processamento(
    linhas_alunos: list[tuple[int, dict]],
    linhas_notas: list[tuple[int, dict]],
    config: Config,
) -> ResultadoProcessamento:
    erros: list[ErroValidacao] = []

    alunos: dict[str, Aluno] = {}
    for numero, registro in linhas_alunos:
        resultado = validar_aluno(numero, registro, set(alunos))
        if isinstance(resultado, ErroValidacao):
            erros.append(resultado)
        else:
            alunos[resultado.matricula] = resultado

    notas_validas: list[Nota] = []
    vistas: set[tuple[str, str, str]] = set()
    invalidas = 0
    for numero, registro in linhas_notas:
        resultado = validar_nota(numero, registro, set(alunos), vistas, config)
        if isinstance(resultado, ErroValidacao):
            erros.append(resultado)
            invalidas += 1
            continue
        vistas.add((resultado.matricula, resultado.disciplina, resultado.avaliacao))
        notas_validas.append(resultado)
        alunos[resultado.matricula].notas.append(resultado)

    return ResultadoProcessamento(
        config=config,
        alunos=sorted(alunos.values(), key=lambda a: int(a.matricula)),
        medias_disciplinas=media_por_disciplina(notas_validas),
        erros=erros,
        notas_validas=len(notas_validas),
        notas_invalidas=invalidas,
    )
