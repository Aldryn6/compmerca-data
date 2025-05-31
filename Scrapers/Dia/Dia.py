#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reescrito para usar curl_cffi con impersonation
"""
from curl_cffi import requests
import time
import random
import csv

# URL base de la API de DIA
base_url = u"https://www.dia.es/api/v1/search-back/search/?q=\u0022\u0022&page_size=150&page="
base_site_url = "https://www.dia.es"

# Lista para almacenar todos los productos
all_products = []

# Comienza en la página 1
page = 1

# Lista de versiones impersonate para rotar
impersonate_versions = [
    "chrome99", "chrome100", "chrome101", "chrome104", "chrome107",
    "chrome110", "chrome116", "chrome119", "chrome120", "chrome123", 
    "chrome124", "chrome99_android", "edge99", "edge101", 
    "safari15_3", "safari15_5", "safari17_0"
]

# Función para realizar la solicitud HTTP con curl_cffi, alternando impersonate
def fetch_url(url):
    impersonate_version = random.choice(impersonate_versions)  # Selecciona una versión aleatoria
    response = requests.get(url, impersonate=impersonate_version)
    response.raise_for_status()
    return response.json()

while True:
    # Construye la URL con el número de página
    url = f"{base_url}{page}"
    
    try:
        # Realiza la solicitud a la API
        data = fetch_url(url)
        
        # Verifica si hay productos en esta página
        if 'search_items' in data and len(data['search_items']) > 0:
            # Procesa cada producto y agrega a la lista
            for producto in data['search_items']:
                all_products.append(producto)  # Agrega el producto a la lista
            
            print(f"Página {page}: {len(data['search_items'])} productos descargados")
            
            # Opción: imprime los primeros productos para verificar la estructura
            if page == 1:  # Solo imprime la primera página
                print("Ejemplo de productos:", data['search_items'][:5])  # Imprime los primeros 5 productos
                print("Claves disponibles en un producto:", data['search_items'][0].keys())  # Muestra las claves de un producto
            
            # Pasa a la siguiente página
            page += 1
            
            # Pausa aleatoria entre 1 y 5 segundos para no sobrecargar el servidor
            wait_time = random.uniform(1, 5)
            time.sleep(wait_time)
        else:
            # Si no hay más productos, detiene el bucle
            print(f"No se encontraron más productos en la página {page}. Finalizando.")
            break
    except Exception as e:
        print(f"Error al obtener la página {page}: {e}")
        break

# Guardar los productos en un archivo CSV
if all_products:
    csv_file_path = "productos_dia.csv"  # Ruta completa al archivo CSV

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        # Especificar los nombres de las columnas en el orden deseado
        fieldnames = [
            'id',
            'nombre',
            'precio',
            'precio_por_unidad',
            'categoria',
            'marca',
            'imagen',
            'url',
            'supermercado'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Escribir la cabecera
        writer.writeheader()

        # Función auxiliar para normalizar las unidades a minúsculas
        def normalizar_unidad(unidad):
            unidad = unidad.lower()
            if unidad == "kilo":
                return "kg"
            elif unidad == "litro":
                return "l"
            return unidad  # Devuelve la unidad en minúscula si no necesita más cambios

        # Escribir cada producto en el CSV
        for producto in all_products:
            # Extrae el ID del producto desde la URL
            url_producto = producto.get('url', '')  # URL parcial del producto
            producto_id = url_producto.split('/')[-1]  # Solo el último segmento numérico de la URL
            
            # Extrae los demás campos y realiza la limpieza/formateo solicitado
            nombre = producto.get('display_name', '').strip()  # Nombre limpio
            precio = round(float(producto.get('prices', {}).get('price', 0)), 2)  # Precio (float con dos decimales)
            
            # Precio por unidad con unidad en minúsculas y formato correcto
            precio_unidad = producto.get('prices', {}).get('price_per_unit', 0)
            unidad_medida = producto.get('prices', {}).get('measure_unit', '')
            unidad_medida = normalizar_unidad(unidad_medida)  # Convierte unidad a minúscula
            precio_por_unidad = f"{round(float(precio_unidad), 2)}€/{unidad_medida}" if precio_unidad else ""
            
            # Solo categoría_2 para la categoría
            categoria = producto.get('l2_category_description', '').strip()  # Solo categoría de segundo nivel
            
            # Marca (limpiando caracteres especiales)
            marca = producto.get('brand', '').replace("®", "").replace("©", "").replace("™", "").strip()  # Marca limpia
            
            # Imagen con extensión válida
            image_path = producto.get('image', '')
            if image_path.endswith(('.png', '.jpg', '.webp')):  # Verifica extensiones válidas
                imagen = base_site_url + image_path  # URL completa de la imagen
            else:
                imagen = ""  # Si no es una extensión válida, deja vacío
            
            # URL completa del producto
            url_producto_completa = base_site_url + url_producto
            
            # Escribir la fila en el CSV con el formato final
            writer.writerow({
                'id': producto_id,
                'nombre': nombre,
                'precio': precio,
                'precio_por_unidad': precio_por_unidad,
                'categoria': categoria,
                'marca': marca,
                'imagen': imagen,
                'url': url_producto_completa,
                'supermercado': 'Dia'
            })

    print(f"Total de productos obtenidos: {len(all_products)}")
    print(f"Los productos se han guardado en: {csv_file_path}")
else:
    print("No se encontraron productos.")

