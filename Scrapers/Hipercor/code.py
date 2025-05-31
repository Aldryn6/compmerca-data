import random
import time
import csv
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# User Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/107.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"
]

# Configuración de Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-webgl")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

# Inicializar el controlador de Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL de Hipercor
url = 'https://www.hipercor.es/supermercado/alimentacion/'
driver.get(url)

# Aceptar cookies
try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    ).click()
    print("Cookies aceptadas.")
except Exception as e:
    print("No se encontró el botón de cookies:", e)

# Lista para almacenar datos
data = []

# Función para limpiar almacenamiento
def clear_storage():
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
    except Exception as e:
        print("Error al limpiar el almacenamiento:", e)


# Obtener el número total de páginas
def get_total_pages():
    try:
        pagination_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pagination-current"))
        ).text
        total_pages = int(pagination_text.split()[-1])
        return total_pages
    except Exception as e:
        print("Error al obtener el número total de páginas:", e)
        return 1

# Obtener el total de páginas
total_pages = get_total_pages()
print(f"Total de páginas encontradas: {total_pages}")

# Bucle a través de todas las páginas
for page in range(total_pages):
    clear_storage()
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product_tile'))
        )
        productos = driver.find_elements(By.CSS_SELECTOR, 'div.product_tile')

        for producto in productos:
            data_json = producto.get_attribute('data-json')

            if data_json:
                product_info = json.loads(data_json)

                nombre = str(product_info.get('name', 'No disponible'))
                marca = str(product_info.get('brand', ''))
                categoria = ' > '.join(map(str, product_info.get('category', [])))
                precio = float(product_info.get('price', {}).get('final', '0'))
                id_producto = str(product_info.get('id', 'No disponible'))

                image_element = producto.find_element(By.CSS_SELECTOR, 'img')
                image_url = image_element.get_attribute('src')

                product_url_element = producto.find_element(By.CSS_SELECTOR, 'a')
                product_url = product_url_element.get_attribute('href')

                # Calcular precio por unidad
                precio_por_unidad = str(precio) + '€/ud'

                if id_producto == 'No disponible':
                    continue

                # Añadir datos a la lista
                data.append([
                    id_producto, nombre, precio, precio_por_unidad, categoria,
                    marca, image_url, product_url, 'Hipercor'
                ])

        # Clic en el botón "Siguiente" si no es la última página
        if page < total_pages - 1:
            siguiente_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'Siguiente'))
            )
            siguiente_btn.click()
            print(f"Clic en 'Siguiente'. Página: {page + 2} de {total_pages}")
            time.sleep(random.uniform(1, 2))
    except Exception as e:
        print("Error al cargar productos:", e)
        break

# Guardar los datos en un archivo CSV
with open('productos_hipercor.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'nombre', 'precio', 'precio_por_unidad', 'categoria', 'marca',
                     'imagen', 'url', 'supermercado'])
    writer.writerows(data)

print("Datos guardados en 'productos_hipercor.csv'")

# Cerrar el navegador
driver.quit()
