from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from ..core.entidades import Cliente, Transacao
from ..core.resultados import ResultadoProcessamento
from ..infra.fontes import FonteDados, FonteDadosMemoria, fonte_a_partir_de_caminhos
from ..infra.relatorios import criar_gerador
from ..services.processamento import executar_processamento
from .config import Settings, obter_settings
from .schemas import (
    ClienteSchema,
    MetricasSchema,
    ProcessamentoEntrada,
    TransacaoSchema,
)

app = FastAPI(title="DataProcessor API")

MEDIA_TYPES = {"texto": "text/plain", "json": "application/json", "csv": "text/csv"}


@app.exception_handler(OSError)
def fonte_indisponivel(request: Request, erro: OSError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": f"Fonte de dados indisponível: {erro}"})


def obter_fonte(settings: Settings = Depends(obter_settings)) -> FonteDados:
    pasta = settings.data_dir
    return fonte_a_partir_de_caminhos(pasta / "clientes.csv", pasta / "transacoes.csv", pasta / "config.json")


def obter_resultado(fonte: FonteDados = Depends(obter_fonte)) -> ResultadoProcessamento:
    return executar_processamento(fonte)


def resumir(resultado: ResultadoProcessamento) -> MetricasSchema:
    return MetricasSchema(
        clientes_validos=len(resultado.clientes),
        clientes_invalidos=len(resultado.clientes_invalidos),
        transacoes_validas=len(resultado.transacoes),
        transacoes_invalidas=len(resultado.transacoes_invalidas),
        media_idade=resultado.media_idade,
        total_aprovado=resultado.total_aprovado,
    )


@app.get("/relatorio")
def relatorio(resultado: ResultadoProcessamento = Depends(obter_resultado)):
    return resultado.to_dict()


@app.get("/relatorio/{formato}")
def relatorio_formatado(formato: Literal["texto", "json", "csv"], resultado: ResultadoProcessamento = Depends(obter_resultado)):
    conteudo = criar_gerador(formato).render(resultado)
    return Response(content=conteudo, media_type=MEDIA_TYPES[formato])


@app.get("/clientes", response_model=list[ClienteSchema])
def listar_clientes(resultado: ResultadoProcessamento = Depends(obter_resultado)):
    return resultado.clientes


@app.get("/clientes/{cliente_id}", response_model=ClienteSchema)
def obter_cliente(cliente_id: int, resultado: ResultadoProcessamento = Depends(obter_resultado)):
    for cliente in resultado.clientes:
        if cliente.id == cliente_id:
            return cliente
    raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} não encontrado")


@app.get("/transacoes", response_model=list[TransacaoSchema])
def listar_transacoes(
    status: Literal["aprovado", "pendente", "recusado"] | None = None,
    categoria: str | None = None,
    cliente_id: int | None = None,
    resultado: ResultadoProcessamento = Depends(obter_resultado),
):
    transacoes = resultado.transacoes
    if status is not None:
        transacoes = [t for t in transacoes if t.status == status]
    if categoria is not None:
        transacoes = [t for t in transacoes if t.categoria == categoria]
    if cliente_id is not None:
        transacoes = [t for t in transacoes if t.cliente_id == cliente_id]
    return transacoes


@app.get("/metricas", response_model=MetricasSchema)
def metricas(resultado: ResultadoProcessamento = Depends(obter_resultado)):
    return resumir(resultado)


@app.post("/processar", response_model=MetricasSchema)
def processar(entrada: ProcessamentoEntrada):
    fonte = FonteDadosMemoria(
        clientes=[Cliente(**c.model_dump()) for c in entrada.clientes],
        transacoes=[Transacao(**t.model_dump()) for t in entrada.transacoes],
        config=entrada.config.model_dump(),
    )
    return resumir(executar_processamento(fonte))
