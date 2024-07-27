import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from playwright.sync_api import sync_playwright
import logging
import time

# Configuração de log para exibir mensagens de nível INFO no terminal
logging.basicConfig(level=logging.INFO)

def get_quant_info_response(papel):

    url = "https://statusinvest.com.br/acao/indicatorhistoricallist"
    headers = {
            # ":authority": "statusinvest.com.br",
            # ":method": "POST",
            # ":path": "/acao/indicatorhistoricallist",
            # ":scheme": "https",
            #"Accept": "*/*",
            #"Accept-Encoding": "gzip, deflate, br, zstd",
            #"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            #"Content-Length": "57",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            #"Cookie": "_adasys=12dc2114-b78f-4a69-a533-0dea2176c593; _fbp=fb.2.1677181329855.1524045252; hubspotutk=56b074c73ba762827e783eaaae06f1ef; pg_mm2_cookie_a=2441b944-1d8b-4b19-8c58-89ab6adbecd5; G_ENABLED_IDPS=google; _hjSessionUser_1931042=eyJpZCI6ImExN2M5OGVjLTc5MmQtNWNiNy1iZDQ1LTdlOTU0ZGU3NjBjYSIsImNyZWF0ZWQiOjE2ODQyNTcwOTk0NzIsImV4aXN0aW5nIjp0cnVlfQ==; _fs=16427822731-15146663495; _ga=GA1.1.1678513896.1677181330; suno_checkout_userid=4585cd5a-416b-46d0-826e-0b114bd86858; messagesUtk=6507b1b12cd040c5ad0da4e6f7891699; _gcl_au=1.1.2084453905.1719699987; _cc_id=839bd564332834229d9b91b4630cd49e; panoramaId_expiry=1720304790192; panoramaId=c7b860399c02afc7d64050e94e23185ca02c29a4e7b2ff0f0b4c43bfb397f1fe; panoramaIdType=panoDevice; __hssrc=1; _clck=4fbnh2%7C2%7Cfn3%7C0%7C1315; _hjSession_1931042=eyJpZCI6IjQ0NjllYmJiLWQ0N2MtNDVkZi04M2Q1LWUxYzRkMGMzMTc2MyIsImMiOjE3MTk4NzQwNzQ5NjYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; __hstc=176625274.56b074c73ba762827e783eaaae06f1ef.1677181344511.1719801904325.1719874081156.117; __gads=ID=b386d831e68d19a7:T=1711329073:RT=1719874273:S=ALNI_MavEg4BFEn31HcO7CMA9AR1FDVMSw; __gpi=UID=00000dacb25822bb:T=1711329073:RT=1719874273:S=ALNI_Ma1mqxHZhaFNYz9YNGj7jnxhtASjg; __eoi=ID=7d524a1415c6546f:T=1709907372:RT=1719874273:S=AA-AfjbT8Pgvk6BILZIFUjkSGJnA; _clsk=nmgj8v%7C1719874559279%7C3%7C1%7Cu.clarity.ms%2Fcollect; cf_clearance=2gGc8Itw1eWH0WwJv8NfYDgLj0xn_ZaEdegNpata6EQ-1719874559-1.0.1.1-FidwWi4r3yjn8QedgdnepDwtfDWixFJg7Lgg4p.cmnNs6z9ClZ.buTZgnJTFyBY5k6GpStKFKE7Cl3k803oLGg; .StatusAdThin=1; _ga_69GS6KP6TJ=GS1.1.1719874074.146.1.1719874563.33.0.0; FCNEC=%5B%5B%22AKsRol8LY3freSfkK2PXSRzCEoilQ3y7EpGsskQasRpd5J0uR0RqOq79AaQH_yQLNa4MBrHew8wQhoWkUbKyPdfM2nwaA4wuOzQU7quXTMM1tvKDHp6ajudg1SX1vdD3QZDm5r-4672feSY6bhKC35dUCcA-g3be9w%3D%3D%22%5D%5D; __hssc=176625274.2.1719874081156; hs-messages-hide-welcome-message=true",
            #"Origin": "https://statusinvest.com.br",
            #"Priority": "u=1, i",
            #"Referer": "https://statusinvest.com.br/acoes/bbas3",
            #"Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
            #"Sec-Ch-Ua-Mobile": "?0",
            #"Sec-Ch-Ua-Platform": '"Windows"',
            #"Sec-Fetch-Dest": "empty",
            #"Sec-Fetch-Mode": "cors",
            #"Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        }

    data = f"codes%5B%5D={papel}&time=5&byQuarter=false&futureData=false"

    # Realizar a requisição POST
    response = requests.post(url, headers=headers, data=data)

    return response

def get_quant_info(papel):
    response = get_quant_info_response(papel)
    indicator_list = json.loads(response.content)
    data = indicator_list['data'][papel]
    
    df_data_rows = []

    for info in data:

        indicador = info['key']
        historical_info = info['ranks']
        
        for history in historical_info:
            try:
                if history['rank_F'] != 'ATUAL':
                    if 'value' in history.keys():
                    
                        df_data_row = {}

                        df_data_row['Papel'] = papel.upper()
                        df_data_row['Indicador'] = indicador
                        df_data_row['Valor'] = history['value']
                        df_data_row['Ano'] = history['rank_F']

                        df_data_rows.append(df_data_row)

            except Exception as e:
                logging.warning(e)
                continue

    df = pd.DataFrame(df_data_rows)

    return df

def main():

    # Ler o arquivo .xlsx e converter para um DataFrame
    df = pd.read_excel("Tabela_Acoes_Setor.xlsx")

    df = df.dropna()
    df = df.reset_index(drop=True)

    logging.info("Coletando a série histórica dos indicadores das ações...")

    dfs_to_concat = []
    cont_erro = 0

    for papel in df['Papel']:
        try:
            papel_lower = papel.lower()
            df_quant_info = get_quant_info(papel_lower)
            dfs_to_concat.append(df_quant_info)

            logging.info(f"Coletada as informações de {papel}")
            time.sleep(3)

        except Exception as e:
            logging.warning(e)
            logging.warning(f"Não foi possível coletar as informações de {papel}")
            cont_erro += 1

    if dfs_to_concat:
        df_quant_info = pd.concat(dfs_to_concat, ignore_index=True)

    df_quant_info = df_quant_info.reset_index(drop=True)
    print(df_quant_info)

    logging.info(f"Erros encontrados: {cont_erro}")

    logging.info("Dados coletados. Gerando Excel de saída ...")

    #Especificar o caminho para salvar o novo arquivo .xlsx
    output_file_path = 'C:\\Users\\olive\\Documents\\Códigos\\TCC\\Tabela_Info_Quant.xlsx'

    #Salvar o DataFrame limpo em um arquivo Excel
    df_quant_info.to_excel(output_file_path, index=False)

    # Exibir uma mensagem de confirmação
    logging.info(f"DataFrame de Info Quant em: {output_file_path}")

if __name__ == '__main__':
    main()