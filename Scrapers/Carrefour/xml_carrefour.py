from curl_cffi import requests
from io import BytesIO
from lxml import etree
import csv
import os
import random

# Lista de impersonates válidos
impersonate_options = [
    "chrome99",
    "chrome100",
    "chrome101",
    "chrome104",
    "chrome107",
    "chrome110",
    "chrome116",
    "chrome119",
    "chrome120",
    "chrome123",
    "chrome124",
    "chrome131",
    "chrome99_android",
    "edge99",
    "edge101"
]

# Elegir un impersonate al azar
selected_impersonate = random.choice(impersonate_options)
print(f"Usando impersonate: {selected_impersonate}")

url = 'https://www.carrefour.es/sitemap/food/categories/categorySitemap-00000-of-00001.xml'

response = requests.get(url, impersonate=selected_impersonate)

if response.status_code != 200:
    print(f"Error al obtener la URL: {response.status_code}")
    exit()

def guardarCSV():
    # Asegurar que el directorio 'output' existe
    if not os.path.exists('output'):
        os.makedirs('output')

    # Extraer datos y guardarlos en el archivo CSV
    with open('output/carrefour-categories.csv', mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['url', 'lastmod'])  # Encabezados del CSV
        print(f"Extrayendo datos de: {url}")

        try:
            # Parsear el XML
            tree = etree.parse(BytesIO(response.content))
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls_extracted = tree.xpath('//ns:url/ns:loc/text()', namespaces=ns)
            lastmod_dates_extracted = tree.xpath('//ns:url/ns:lastmod/text()', namespaces=ns)

            # Filtrar y escribir solo las URLs que son subcategorías
            for extracted_url, lastmod in zip(urls_extracted, lastmod_dates_extracted):
                # Contar el número de segmentos en la URL
                segments = extracted_url.split('/')
                if len(segments) == 9:  # Solo guarda si tiene exactamente 9 segmentos (indicativo de una subsubcategoría)
                    writer.writerow([extracted_url, lastmod])

        except etree.XMLSyntaxError as e:
            print(f"Error al parsear el XML: {e}")
            exit()

# Ejecutar la función
guardarCSV()
