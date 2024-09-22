import pandas as pd
import numpy as np
import yfinance as yf
import logging
import constants as c
# Configuração de log para exibir mensagens de nível INFO no terminal
logging.basicConfig(level=logging.INFO)

def get_ranking(df, indicador, ano, quantidade):

    # Filtrando com base em 'Indicador', 'Ano' e 'Valor'
    filtro = (df['Indicador'] == indicador) & (df['Ano'] == ano) & (df['Valor'] > 0)

    # Aplicando o filtro ao DataFrame
    df_filtrado = df[filtro]

    if indicador != "p_l":

        # Ordenando o DataFrame filtrado de forma decrescente pela coluna 'Valor'
        df_filtrado = df_filtrado.sort_values(by='Valor', ascending=False)

    else:
        # Ordenando o DataFrame filtrado de forma crescente pela coluna 'Valor'
        df_filtrado = df_filtrado.sort_values(by='Valor', ascending=True)

    df_filtrado = df_filtrado.head(quantidade)
    df_filtrado = df_filtrado.reset_index(drop=True)

    return df_filtrado

def gera_carteira(compras):
    # Definir o intervalo de datas
    inicio = "2023-01-13"
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

def gera_lista_rankings(df, lista_indicadores, lista_anos):

    lista_rankings_anual = []
    indicador_medio = "+".join(lista_indicadores)

    for ano in lista_anos:

        lista_rankings = []

        for indicador in lista_indicadores:
            df_ranking = get_ranking(df, indicador, ano, 100)
            lista_rankings.append(df_ranking)

        df_ranking_medio = gera_ranking_medio(lista_rankings)
        df_ranking_medio["Ano"] = ano
        df_ranking_medio["indicador_medio"] = indicador_medio
        lista_rankings_anual.append(df_ranking_medio)

    return lista_rankings_anual

def gera_ranking_medio(lista_rankings):

    dic_ranking_medio = {}

    for df_ranking in lista_rankings:
        for idx, linha in df_ranking.iterrows():
            papel = linha["Papel"]
            pontuacao = 100 - idx

            if papel not in dic_ranking_medio.keys():
                dic_ranking_medio[papel] = pontuacao
            else:
                dic_ranking_medio[papel] += pontuacao

    dic_ranking_medio = dict(sorted(dic_ranking_medio.items(), key=lambda x: x[1], reverse=True))

    df_rows_list = []

    for papel in dic_ranking_medio.keys():
        df_row = {}
        df_row["Papel"] = papel
        df_rows_list.append(df_row)

    return pd.DataFrame(df_rows_list)

def gera_compras(lista_ranking_medio, mes, qtd_acoes, criterio):

    compras = []

    for df in lista_ranking_medio:
        for idx, linha in df.iterrows():
            ticker = linha["Papel"]
            ano = str(linha["Ano"])
            data_compra = c.dic_datas_compras[ano][mes]

            dic_compras = {}
            dic_compras["ticker"] = ticker + ".SA"
            # dic_compras["valor_investido"] = get_valor_investido(qtd_acoes, criterio, idx)

            ###

            compras.append(dic_compras)

    return compras

def get_valor_investido(qtd_acoes, criterio, idx):
    pass

def main():
    # dados de 2012 são usados p comprar em 2013 e por ai vai...
    lista_anos = [2012,2013,2014,2015,2016,2017,2018,2019,2020,2021]

    # Leitura da planilha com info quant dos ativos
    df = pd.read_excel("Tabela_Info_Quant.xlsx")

    df = df.dropna()
    df = df.reset_index(drop=True)

    print(df)

    # rankings para as monstagens das carteiras
    ranking_dy = gera_lista_rankings(df, ["dy"], lista_anos)
    ranking_pl = gera_lista_rankings(df, ["p_l"], lista_anos)
    ranking_roa = gera_lista_rankings(df, ["roa"], lista_anos)
    ranking_roa_dy = gera_lista_rankings(df, ["roa", "dy"], lista_anos)
    ranking_pl_dy = gera_lista_rankings(df,["p_l","dy"],lista_anos)
    ranking_pl_roa = gera_lista_rankings(df,["p_l","roa"],lista_anos)
    ranking_dy_pl_roa = gera_lista_rankings(df,["dy","p_l","roa"],lista_anos)

    for i in ranking_dy:
        print(i)

    # compras = gera_compras(ranking_dy_pl_roa)

    # for ranking in lista_ranking_anual:
    #     print(ranking)

    # Definir as compras feitas
    compras = [
        {"ticker": "BBAS3.SA", "data": "2023-01-13", "valor_investido": 1000},
        {"ticker": "ITUB3.SA", "data": "2023-05-05", "valor_investido": 500},
        {"ticker": "TAEE11.SA", "data": "2023-05-05", "valor_investido": 500},
        {"ticker": "BBAS3.SA", "data": "2023-06-01", "valor_investido": 200},
        {"ticker": "ITUB3.SA", "data": "2023-08-10", "valor_investido": 300},
    ]

if __name__ == '__main__':
    main()