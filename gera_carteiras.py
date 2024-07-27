import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import logging

# Configuração de log para exibir mensagens de nível INFO no terminal
logging.basicConfig(level=logging.INFO)


def main():

    # Ler o arquivo .xlsx e converter para um DataFrame
    df = pd.read_excel("Tabela_Info_Quant.xlsx")

    df = df.dropna()
    df = df.reset_index(drop=True)

    print(df)


if __name__ == '__main__':
    main()