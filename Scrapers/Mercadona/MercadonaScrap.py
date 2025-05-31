import re
import requests
import pandas as pd
import os

# Eliminar archivos CSV previos si existen
if os.path.exists("Mercadona.csv"):
    os.remove("Mercadona.csv")
    print("Archivo Mercadona.csv eliminado.")
if os.path.exists("errores.csv"):
    os.remove("errores.csv")
    print("Archivo errores.csv eliminado.")

# Obtener el sitemap de Mercadona
xmlSitemap = requests.get("https://tienda.mercadona.es/sitemap.xml").text
lineas = xmlSitemap.split('\n')
mercadona_productos = []

# Extraer códigos de producto del sitemap (máximo 100 productos)
for url in lineas:
    match = re.search(r'/product\/(\d+)/', url)
    if match:
        mercadona_productos.append(match.group(1))
        print("Encontrado el código: " + str(match.group(1)) + " en : " + url)

# Listas para almacenar datos y errores
productos = []
errores = []

# Recorrer productos y extraer información
for producto in mercadona_productos:
    try:
        print("Registrando el producto: " + producto)
        # Obtener datos del producto
        url_api = f"https://tienda.mercadona.es/api/products/{producto}"
        response = requests.get(url_api, headers={"Accept": "application/json"})
        data = response.json()

        # Extraer datos necesarios
        precio = round(float(data['price_instructions'].get('unit_price', 0)), 2)
        unidad_medida = data['price_instructions'].get('reference_format', '').lower()
        precio_unidad = f"{round(float(data['price_instructions'].get('reference_price', '0.00')), 2)}€/{unidad_medida}"
        imagen = data['thumbnail']
        nombre = data.get('display_name', 'Desconocido')
        categoria = data['categories'][0]['name'] if data.get('categories') else 'Sin categoría'
        marca = data.get('brand', 'Mercadona')
        id_producto = data['id']
        url_producto = data['share_url']

        # Crear diccionario con los datos extraídos
        producto_info = {
            "id": id_producto,
            "nombre": nombre,
            "precio": precio,
            "precio_por_unidad": precio_unidad,
            "categoria": categoria,
            "marca": marca,
            "imagen": imagen,
            "url": url_producto,
            "supermercado": "Mercadona"
        }

        # Añadir a la lista de productos
        productos.append(producto_info)

    except Exception as e:
        print(f"Error al obtener el producto {producto}: {e}")
        errores.append(producto)

# Crear DataFrame y guardar en CSV
df = pd.DataFrame(productos)
df.to_csv('productos_mercadona.csv', encoding='utf-8', index=False)

# Guardar errores en otro CSV
if errores:
    df_errores = pd.DataFrame(errores, columns=["ID del producto"])
    df_errores.to_csv('errores.csv', encoding='utf-8', index=False)

print("Proceso completado. Archivos generados: Mercadona.csv y errores.csv")
