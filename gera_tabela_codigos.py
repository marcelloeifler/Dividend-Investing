import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import logging

# Configuração de log para exibir mensagens de nível INFO no terminal
logging.basicConfig(level=logging.INFO)

def collect_segment(papel):

    url = f"https://statusinvest.com.br/acoes/{papel}"

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        page.wait_for_timeout(3000)

        # Obter o HTML da página
        page_content = page.content()

        segment = get_sector(page_content)

    return segment


def get_sector(page_content):
    
    # Exibir o HTML (ou processar conforme necessário)
    soup = BeautifulSoup(page_content, 'html.parser')
    #print(soup.prettify())
    # Encontrar o trecho HTML com a classe `info pl-md-2`
    info_section = soup.find('div', class_='info pl-md-2')

    # Verificar se a seção foi encontrada e procurar o segmento de atuação dentro dela
    if info_section:
        segment_element = info_section.find('strong', class_='value')
        segment = segment_element.text.strip() if segment_element else None
    else:
        segment = None

    return segment

def main():

    # Ler o arquivo .xlsx e converter para um DataFrame
    df = pd.read_excel("Tabela_Acoes_Limpo.xlsx")

    df = df.dropna()
    df = df.reset_index(drop=True)

    print(df)

    logging.info("Coletando o segmento de atuação das empresas... ")
    segment_list = []
    for papel in df['Papel']:
        try:
            segment = collect_segment(papel)
            logging.info(f"Segmento de {papel} : {segment}")
        except Exception as e:
            logging.warning(f"Erro inesperado: {e}")
            logging.warning(f"Não foi possível coletar o segmento de {papel}")
            segment = None
        
        segment_list.append(segment)

    logging.info("Segmentos coletados.")
    df['Segmento'] = segment_list

    #Especificar o caminho para salvar o novo arquivo .xlsx
    output_file_path = 'C:\\Users\\olive\\Documents\\Códigos\\TCC\\Tabela_Acoes_Setor.xlsx'

    #Salvar o DataFrame limpo em um arquivo Excel
    df.to_excel(output_file_path, index=False)

    # Exibir uma mensagem de confirmação
    print(f"DataFrame limpo salvo em: {output_file_path}")

if __name__ == '__main__':
    main()