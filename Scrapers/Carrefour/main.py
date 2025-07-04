from curl_cffi import requests
from datetime import datetime
import xml_carrefour as xml_c
import pandas as pd
import logging
import os
import time
import csv
import random

# Configuración de constantes
base_url = 'https://www.carrefour.es/cloud-api/plp-food-papi/v1'
csv_output = 'output/productos_carrefour.csv'

# Opciones de impersonate disponibles
impersonate_options = [
    "chrome99", "chrome100", "chrome101", "chrome104", "chrome107",
    "chrome110", "chrome116", "chrome119", "chrome120",
    "edge99", "edge101"
]

def get_impersonate():
    """Selecciona un impersonate aleatorio."""
    return random.choice(impersonate_options)

def main():
    # Configuración del logger
    timestamp = datetime.now()
    dt_string = timestamp.strftime("%d_%m_%Y_%H_%M_%S")
    try:
        logging.basicConfig(
            filename=f'log/{dt_string}_scraper.log',
            level=logging.WARNING,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    except FileNotFoundError:
        os.makedirs('log')
        logging.basicConfig(
            filename=f'log/{dt_string}_scraper.log',
            level=logging.WARNING,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    logging.warning('Scrapeo iniciado.')

    # Leer URLs del archivo CSV y quitar el prefijo si está presente
    with open('output/carrefour-categories.csv', 'r', encoding='utf-8') as csvfile:
        urls_to_scrape = [
            row['url'].replace('https://www.carrefour.es', '') for row in csv.DictReader(csvfile)
        ]
    
    if not urls_to_scrape:
        logging.warning("No se encontraron URLs para scrapear.")
        print("No se encontraron URLs para scrapear.")
        return

    fieldnames = ['id', 'nombre', 'precio', 'precio_por_unidad', 'categoria', 'marca', 'imagen', 'url', 'supermercado']
    with open(csv_output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for url in urls_to_scrape:
            print(f"Scrapeando URL: {url}")
            scrape_product_details(url, writer)

    logging.warning('Scrapeo terminado.')
    print('Scrapeo terminado.')

    clean_duplicates(csv_output)

def clean_duplicates(csv_file):
    """Elimina duplicados del archivo CSV basado en el campo 'id'."""
    df = pd.read_csv(csv_file)
    print(f"Limpiando duplicados en {csv_file}, número de elementos duplicados: {df.duplicated().sum()}")
    logging.warning(f"Limpiando duplicados en {csv_file}, número de elementos duplicados: {df.duplicated().sum()}")
    df.drop_duplicates(subset='id', inplace=True)
    df.to_csv(csv_file, index=False)

def scrape_product_details(url, writer):
    """Scrapea detalles de productos desde una URL paginada."""
    offset = 0
    while True:
        impersonate = get_impersonate()
        full_url = f"{base_url}{url}?offset={offset}"
        print(f"Accediendo a: {full_url} con impersonate: {impersonate}")
        
        response = None
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            response = requests.get(full_url, impersonate=impersonate)
            if response.status_code not in (403, 502):
                break
            retry_count += 1
            impersonate = get_impersonate()  # Cambiar impersonate en cada reintento
            logging.error(f"Error {response.status_code}: Reintentando acceso a {full_url} ({retry_count}/{max_retries})")
            print(f"Error {response.status_code}: Reintentando acceso a {full_url} ({retry_count}/{max_retries})")
            time.sleep(random.uniform(2, 5))  # Espera dinámica entre reintentos

        if response is None or response.status_code == 403:
            logging.error(f"Error 403 persistente: Acceso denegado a {full_url} tras {max_retries} intentos")
            print(f"Error 403 persistente: Acceso denegado a {full_url} tras {max_retries} intentos")
            break
        elif response.status_code == 206:
            print("No se encontraron más productos en esta página.")
            break
        elif response.status_code != 200:
            logging.error(f"Error al acceder a {full_url}: {response.status_code}")
            print(f"Error al acceder a {full_url}: {response.status_code}")
            break
        
        try:
            data = response.json()
        except ValueError:
            logging.error(f"Error al decodificar JSON de la respuesta en {full_url}")
            print(f"Error al decodificar JSON de la respuesta en {full_url}")
            break

        items = data.get('results', {}).get('items', [])
        category = data.get('category', {}).get('display_name', '')

        for item in items:
            name = item.get('name', '')
            marca = item.get('brand', {}).get('name', '')
            # Checkea si es marca blanca
            if 'Carrefour' in name:
                marca = 'Carrefour'

            # Procesar el precio para convertirlo en float
            precio_str = item.get('price', '').replace('€', '').replace(',', '.').strip()
            try:
                precio = float(precio_str) if precio_str else None
            except ValueError:
                precio = None  # En caso de fallo de conversión

            # Procesar el precio_por
            precio_por_str = item.get('price_per_unit', '').replace(',', '.').strip()
            precio_por = f"{precio_por_str}/{item.get('measure_unit', '')}" if precio_por_str else None

            product_data = {
                'id': item.get('product_id', ''),
                'url': 'https://www.carrefour.es' + item.get('url', ''),
                'nombre': name,
                'precio': precio,
                'precio_por_unidad': precio_por,
                'marca': marca,
                'categoria': category,
                'imagen': item.get('images', {}).get('desktop', ''),
                'supermercado': 'Carrefour'
            }
            writer.writerow(product_data)

        # Incrementar offset y pausar para evitar sobrecarga
        offset += 24
        time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    xml_c.guardarCSV()
    main()
    clean_duplicates(csv_output)
