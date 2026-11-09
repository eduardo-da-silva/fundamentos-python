from painel.core.entidades import Nota


def media_por_disciplina(notas: list[Nota]) -> dict[str, float]:
    somas: dict[str, list[float]] = {}
    for nota in notas:
        somas.setdefault(nota.disciplina, []).append(nota.valor)
    return {d: sum(v) / len(v) for d, v in sorted(somas.items())}
