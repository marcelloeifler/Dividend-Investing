import yfinance as yf
import pandas as pd
import numpy as np
import constants
import logging


def gera_compras(compras):
    # Definir o intervalo de datas
    inicio = "2013-01-01"
    fim = "2023-12-31"

    # Baixar os dados históricos de fechamento ajustado para os tickers
    tickers = list(set([compra["ticker"] for compra in compras]))
    dados = yf.download(tickers, start=inicio, end=fim)["Adj Close"]

    # Inicializar um DataFrame para armazenar a quantidade de ações compradas
    # A inicialização é feita com tipo float para evitar o problema de incompatibilidade de tipos
    quantidade_acoes_df = pd.DataFrame(0.0, index=dados.index, columns=tickers)

    # Inicializar o total investido
    total_investido = 0

    # Processar cada compra
    for compra in compras:
        ticker = compra["ticker"]
        data_compra = compra["data"]
        valor_investido = compra["valor_investido"]

        # Somar ao total investido
        total_investido += valor_investido

        # Preço de fechamento ajustado na data da compra
        preco_compra = dados.loc[data_compra, ticker]

        # Quantidade de ações compradas
        quantidade_acoes = valor_investido / preco_compra

        # Converter para o tipo float64 antes de somar, se necessário
        quantidade_acoes_df[ticker] = quantidade_acoes_df[ticker].astype(np.float64)

        # Adicionar a quantidade de ações compradas ao DataFrame de quantidade de ações
        quantidade_acoes_df.loc[data_compra:, ticker] += quantidade_acoes

    # Calcular o valor da carteira ao longo do tempo
    valor_carteira = pd.DataFrame(index=dados.index)
    for ticker in tickers:
        valor_carteira[ticker] = quantidade_acoes_df[ticker] * dados[ticker]

    # Calcular o valor total da carteira ao longo do tempo
    valor_carteira["Total"] = valor_carteira.sum(axis=1)

    # Calcular o retorno da carteira
    valor_final = valor_carteira["Total"].iloc[-1]
    retorno_total = (valor_final - total_investido) / total_investido

    # Exibir os resultados
    print(valor_carteira)

    # Visualizar o valor total da carteira no último dia
    print(f"Valor final da carteira em {fim}: ${valor_final:.2f}")

    # Visualizar o retorno total da carteira no período
    print(f"Retorno total da carteira de {inicio} a {fim}: {retorno_total * 100:.2f}%")

dic_compras = constants.dic_datas_compras
cont_erros = 0
list_erros = []

for ano in dic_compras.keys():
    dic_ano = dic_compras[ano]

    for mes in dic_ano.keys():
        data_mes = dic_ano[mes]

        # Definir as compras feitas
        compras = [
            {"ticker": "GRND3.SA", "data": data_mes, "valor_investido": 1000},
            {"ticker": "ITUB3.SA", "data": "2023-05-05", "valor_investido": 500},
            {"ticker": "TAEE11.SA", "data": "2023-05-05", "valor_investido": 500},
            {"ticker": "BBAS3.SA", "data": "2023-06-01", "valor_investido": 200},
            {"ticker": "ITUB3.SA", "data": "2023-08-10", "valor_investido": 300},
        ]

        try:

            gera_compras(compras)

        except Exception:
            logging.exception(f"Erro na data {data_mes}")
            cont_erros += 1
            list_erros.append(data_mes)

print(f"Simulações finalizadas. Erros: {cont_erros}")
print(list_erros)

