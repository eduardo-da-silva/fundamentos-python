from ..core.resultados import ResultadoProcessamento
from ..infra.fontes import fonte_a_partir_de_caminhos
from ..infra.relatorios import criar_gerador
from ..services.processamento import executar_processamento

OPCOES_VALIDAS = {"1", "2", "3"}
FORMATOS_VALIDOS = {"texto", "json", "csv"}


def processar_caminhos(caminho_clientes, caminho_transacoes, caminho_config) -> ResultadoProcessamento:
    fonte = fonte_a_partir_de_caminhos(caminho_clientes, caminho_transacoes, caminho_config)
    return executar_processamento(fonte)


def processar() -> ResultadoProcessamento | None:
    caminho_clientes = input("Caminho do CSV de clientes [data/clientes.csv]: ").strip() or "data/clientes.csv"
    caminho_transacoes = input("Caminho do CSV de transações [data/transacoes.csv]: ").strip() or "data/transacoes.csv"
    caminho_config = input("Caminho do JSON de config [data/config.json]: ").strip() or "data/config.json"
    try:
        resultado = processar_caminhos(caminho_clientes, caminho_transacoes, caminho_config)
    except (OSError, ValueError, KeyError) as erro:
        print(f"[ERRO] Não foi possível processar: {erro}")
        return None
    print(f"Clientes válidos: {len(resultado.clientes)}")
    print(f"Transações válidas: {len(resultado.transacoes)}")
    return resultado


def exibir_relatorio(resultado: ResultadoProcessamento) -> None:
    formato = input("Formato (texto/json/csv) [texto]: ").strip() or "texto"
    if formato not in FORMATOS_VALIDOS:
        print(f"Formato inválido: '{formato}'.")
        return
    print(criar_gerador(formato).render(resultado))


def menu_principal() -> None:
    resultado = None
    while True:
        print("\n=== DataProcessor — Menu ===")
        print("1. Processar dados")
        print("2. Exibir relatório")
        print("3. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao not in OPCOES_VALIDAS:
            print(f"Opção inválida: '{opcao}'. Escolha 1, 2 ou 3.")
            continue

        if opcao == "1":
            novo_resultado = processar()
            if novo_resultado is not None:
                resultado = novo_resultado
        elif opcao == "2":
            if resultado is None:
                print("Nenhum dado processado ainda. Escolha a opção 1 primeiro.")
                continue
            exibir_relatorio(resultado)
        else:
            break


if __name__ == "__main__":
    menu_principal()
