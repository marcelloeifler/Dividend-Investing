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
    inicio = "2013-01-01"
    fim = "2023-12-31"

    # Baixar os dados históricos de fechamento ajustado e dividendos para os tickers
    tickers = list(set([compra["ticker"] for compra in compras]))
    dados = yf.download(tickers, start=inicio, end=fim, actions=True)

    # Inicializar um DataFrame para armazenar a quantidade de ações compradas
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
        preco_compra = dados["Adj Close"].loc[data_compra, ticker]

        # Quantidade de ações compradas
        quantidade_acoes = valor_investido / preco_compra

        # Adicionar a quantidade de ações compradas ao DataFrame de quantidade de ações
        quantidade_acoes_df.loc[data_compra:, ticker] += quantidade_acoes

    # Calcular o valor da carteira ao longo do tempo
    valor_carteira = pd.DataFrame(index=dados.index)
    for ticker in tickers:
        valor_carteira[ticker] = quantidade_acoes_df[ticker] * dados["Adj Close"][ticker]

    # Calcular os dividendos recebidos ao longo do tempo
    dividendos_totais = pd.DataFrame(0.0, index=dados.index, columns=tickers)
    dividendos_acumulados = 0  # Inicializando a soma total dos dividendos

    if 'Dividends' in dados.columns:
        for ticker in tickers:
            # Verifica se existem dividendos e preenche valores NaN com 0
            if 'Dividends' in dados.columns:
                dividendos_por_ticker = quantidade_acoes_df[ticker] * dados['Dividends'][ticker].fillna(0)
                dividendos_totais[ticker] = dividendos_por_ticker
                dividendos_acumulados += dividendos_por_ticker.sum()  # Somando todos os dividendos ao longo do tempo
    else:
        print("Nenhum dado de dividendos encontrado para o período ou ticker.")

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

    # Calcular o retorno anualizado (considerando 11 anos)
    anos = 11
    retorno_anualizado = ((1 + retorno_total) ** (1 / anos)) - 1

    # Visualizar o retorno anualizado
    print(f"Retorno anualizado ao longo de {anos} anos: {retorno_anualizado * 100:.2f}%")

    retorno_final = round(retorno_anualizado * 100, 2)

    return retorno_final, dividendos_acumulados

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

        df = df.head(qtd_acoes)
        df = df.reset_index(drop=True)

        for idx, linha in df.iterrows():
            ticker = linha["Papel"]
            ano = str(linha["Ano"] + 1) # será realizado a compra um ano após o ano do ranking
            data_compra = c.dic_datas_compras[ano][mes]

            dic_compras = {}
            dic_compras["ticker"] = ticker + ".SA"
            dic_compras["data"] = data_compra
            dic_compras["valor_investido"] = get_valor_investido(qtd_acoes, criterio, idx)

            ###

            compras.append(dic_compras)

    return compras

def get_valor_investido(qtd_acoes, criterio, idx):

    valor_base = 1000
    peso_10 = [0.2, 0.2, 0.15, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05]
    peso_7 = [0.3, 0.2, 0.2, 0.1, 0.1, 0.05, 0.05]
    peso_5 = [0.35, 0.25, 0.25, 0.1, 0.05]
    peso_3 = [0.6, 0.3, 0.1]

    if criterio == "igual":
        return valor_base / qtd_acoes
    else:
        if qtd_acoes == 3:
            return peso_3[idx] * valor_base
        if qtd_acoes == 5:
            return peso_5[idx] * valor_base
        if qtd_acoes == 7:
            return peso_7[idx] * valor_base
        if qtd_acoes == 10:
            return peso_10[idx] * valor_base
        return valor_base

def gera_compra_indice(ticker,mes, lista_anos):
    compras = []

    for ano in lista_anos:

        ano_compra = str(ano + 1)
        data_compra = c.dic_datas_compras[ano_compra][mes]

        dic_compras = {}
        dic_compras["ticker"] = ticker
        dic_compras["data"] = data_compra
        dic_compras["valor_investido"] = 1000

        ###

        compras.append(dic_compras)

    return compras

def gera_carteira_indice(compras):
    # Definir o intervalo de datas
    inicio = "2013-01-01"
    fim = "2023-12-31"

    # Como só temos um ticker, vamos garantir que seja único
    ticker = compras[0]["ticker"]

    # Baixar os dados históricos de fechamento ajustado para o ticker
    dados = yf.download(ticker, start=inicio, end=fim)["Adj Close"]

    # Inicializar um DataFrame para armazenar a quantidade de ações compradas
    quantidade_acoes_df = pd.Series(0.0, index=dados.index)

    # Inicializar o total investido
    total_investido = 0

    # Processar cada compra
    for compra in compras:
        data_compra = compra["data"]
        valor_investido = compra["valor_investido"]

        # Somar ao total investido
        total_investido += valor_investido

        # Preço de fechamento ajustado na data da compra
        preco_compra = dados.loc[data_compra]

        # Quantidade de ações compradas
        quantidade_acoes = valor_investido / preco_compra

        # Adicionar a quantidade de ações compradas ao DataFrame de quantidade de ações
        quantidade_acoes_df.loc[data_compra:] += quantidade_acoes

    # Calcular o valor da carteira ao longo do tempo
    valor_carteira = quantidade_acoes_df * dados

    # Calcular o valor final da carteira
    valor_final = valor_carteira.iloc[-1]

    # Calcular o retorno total da carteira
    retorno_total = (valor_final - total_investido) / total_investido

    # Exibir os resultados
    print(valor_carteira)

    # Visualizar o valor total da carteira no último dia
    print(f"Valor final da carteira em {fim}: ${valor_final:.2f}")

    # Visualizar o retorno total da carteira no período
    print(f"Retorno total da carteira de {inicio} a {fim}: {retorno_total * 100:.2f}%")

    # Calcular o retorno anualizado (considerando 11 anos)
    anos = 11
    retorno_anualizado = ((1 + retorno_total) ** (1 / anos)) - 1

    # Visualizar o retorno anualizado
    print(f"Retorno anualizado ao longo de {anos} anos: {retorno_anualizado * 100:.2f}%")

    retorno_final = round(retorno_anualizado * 100,2)

    return retorno_final

def gera_simulacao(ranking, criterio):

    lista_meses = ["Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    lista_qtd_acoes = [1, 3, 5, 7, 10]

    dic_simulacao = c.dic_simulacao

    for mes in lista_meses:
        for qtd_acao in lista_qtd_acoes:

            compras = gera_compras(ranking, mes, qtd_acao, criterio)
            retorno, dividendos = gera_carteira(compras)

            #print(dividendos)

            key_qtd_acao = str(qtd_acao)
            #dic_simulacao[mes][key_qtd_acao] = float(retorno)
            dic_simulacao[mes][key_qtd_acao] = round(float(dividendos),2)

            logging.info(f"Mês: {mes}, Qtd_acao: {qtd_acao} completo.")

    return dic_simulacao

def gera_simulacao_indice(ticker):
    lista_meses = ["Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    lista_anos = [2012,2013,2014,2015,2016,2017,2018,2019,2020,2021]

    dic_simulacao = {"Julho":{}, "Agosto":{}, "Setembro":{}, "Outubro":{}, "Novembro":{}, "Dezembro":{}}

    for mes in lista_meses:

        compras = gera_compra_indice(ticker,mes, lista_anos)
        retorno = gera_carteira_indice(compras)

        dic_simulacao[mes] = float(retorno)

        logging.info(f"Mês: {mes} completo.")

    return dic_simulacao

def main():
    # dados de 2012 são usados p comprar em 2013 e por ai vai...
    lista_anos = [2012,2013,2014,2015,2016,2017,2018,2019,2020,2021]

    # Leitura da planilha com info quant dos ativos
    df = pd.read_excel("Tabela_Info_Quant.xlsx")
    df = df.drop(df[df['Papel'] == 'ENAT3'].index)
    df = df.drop(df[df['Papel'] == 'ARZZ3'].index)

    df = df.dropna()
    df = df.reset_index(drop=True)

    # rankings para as monstagens das carteiras
    ranking_dy = gera_lista_rankings(df, ["dy"], lista_anos)
    ranking_pl = gera_lista_rankings(df, ["p_l"], lista_anos)
    ranking_roa = gera_lista_rankings(df, ["roa"], lista_anos)
    ranking_roa_dy = gera_lista_rankings(df, ["roa", "dy"], lista_anos)
    ranking_pl_dy = gera_lista_rankings(df,["p_l","dy"],lista_anos)
    ranking_pl_roa = gera_lista_rankings(df,["p_l","roa"],lista_anos)
    ranking_dy_pl_roa = gera_lista_rankings(df,["dy","p_l","roa"],lista_anos)

    # for i in ranking_dy:
    #     print(i)

    print(ranking_dy_pl_roa)

    #compras = gera_compras(ranking_dy_pl_roa,"Julho",3,"proporcional")
    #compras = gera_compra_indice("BOVA11.SA","Julho",lista_anos)

    #print(compras)
    #retorno = gera_carteira(compras)
    #gera_carteira_indice(compras)
    #print(retorno)

    # logging.info("Gerando simulação ...")
    # dic_simulacao = gera_simulacao(ranking_dy_pl_roa,"proporcional")
    # #dic_simulacao = gera_simulacao_indice("BOVA11.SA")
    #
    # print(dic_simulacao)


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
