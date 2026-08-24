from ..core.metricas import media_idade, total_aprovado
from ..core.resultados import ResultadoProcessamento
from ..core.transformador import transformar_clientes, transformar_transacoes
from ..core.validador import separar_registros, validar_cliente, validar_transacao
from ..infra.fontes import FonteDados


def executar_processamento(fonte: FonteDados) -> ResultadoProcessamento:
    clientes_raw = fonte.carregar_clientes()
    transacoes_raw = fonte.carregar_transacoes()
    config = fonte.carregar_config()

    clientes_validos, clientes_invalidos = separar_registros(clientes_raw, validar_cliente)
    ids_validos = {cliente.id for cliente in clientes_validos}
    transacoes_validas, transacoes_invalidas = separar_registros(
        transacoes_raw,
        validar_transacao,
        ids_clientes=ids_validos,
        config=config,
    )

    clientes = transformar_clientes(clientes_validos)
    transacoes = transformar_transacoes(transacoes_validas)
    return ResultadoProcessamento(
        clientes=tuple(clientes),
        transacoes=tuple(transacoes),
        clientes_invalidos=tuple(clientes_invalidos),
        transacoes_invalidas=tuple(transacoes_invalidas),
        media_idade=media_idade(clientes),
        total_aprovado=total_aprovado(transacoes),
    )
