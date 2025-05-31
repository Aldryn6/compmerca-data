import requests
import time
import pandas as pd
import itertools
import string
import os
import urllib.parse

# Path to the existing 'ALCAMPO' folder
alcampo_folder = os.path.dirname(__file__)

def format_product_url(product_name, retailer_product_id):
    formatted_name = urllib.parse.quote(product_name.lower().replace(" ", "-"))
    return f"https://www.compraonline.alcampo.es/products/{formatted_name}/{retailer_product_id}"

def get_unit_price(price_data):
    unit_data = price_data.get("unit", {})
    unit_amount = unit_data.get("current", {}).get("amount")
    label = unit_data.get("label")

    label_map = {
        "fop.price.per.litre": "€/l",
        "fop.price.per.kg": "€/kg",
        "fop.price.per.each": "€/ud",
        "fop.price.per.ml": "€/ml",
        "fop.price.per.mg": "€/mg",
    }

    if unit_amount and label in label_map:
        unit_suffix = label_map[label]
        return f"{unit_amount}{unit_suffix}"
    
    if unit_amount:
        return f"{unit_amount}€/ud"

    return "N/A"

def get_product_list(data):
    products = []
    if "entities" in data and "product" in data["entities"]:
        for product_id, product_info in data["entities"]["product"].items():
            product_url = format_product_url(product_info["name"], product_info["retailerProductId"])
            
            price_per_unit = get_unit_price(product_info["price"])
            brand = product_info["brand"]
            if "alcampo" in brand.lower():
                brand = "Alcampo"
                
            product_name = product_info["name"]
            category_path = product_info.get("categoryPath", ["N/A"])[1] if len(product_info.get("categoryPath", [])) > 1 else "N/A"

            # Crear la entrada simplificada
            products.append({
                "id": product_info["productId"],
                "nombre": product_name,
                "precio": float(product_info["price"]["current"]["amount"]),
                "precio_por_unidad": price_per_unit,
                "categoria": category_path,
                "marca": brand,
                "imagen": product_info["image"]["src"],
                "url": product_url,
                "supermercado": "Alcampo"
            })
    return products

def generate_search_terms(base_terms):
    search_terms = set()
    for base in base_terms:
        search_terms.add(base.lower())
        search_terms.add(base.upper())
        search_terms.add(base.capitalize())

        for length in range(1, 4):
            for combo in itertools.product(base_terms, repeat=length):
                term = ''.join(combo)
                search_terms.add(term.lower())
                search_terms.add(term.upper())
                search_terms.add(term.capitalize())
    return search_terms

def fetch_all_products(search_terms, csv_file):
    seen_products = set()
    limit = 50

    if not os.path.exists(csv_file):
        df_existing = pd.DataFrame(columns=["id", "nombre", "precio", "precio_por_unidad", "categoria", "marca", "imagen", "url", "supermercado"])
        df_existing.to_csv(csv_file, index=False)

    for term in search_terms:
        offset = 0
        
        while True:
            if len(seen_products) >= 10471:
                print("No hay más productos.")
                return
            
            url = f"https://www.compraonline.alcampo.es/api/v5/products/search?offset={offset}&sort=price&term={term}"
            try:
                print(f"Haciendo solicitud a la API para el término '{term}' con offset {offset}...")
                response = requests.get(url)

                if response.status_code != 200:
                    print(f"Error en la solicitud: {response.status_code}")
                    print(f"Cuerpo de la respuesta: {response.text}")
                    break

                data = response.json()
                products = get_product_list(data)

                if not products:
                    print(f"No se encontraron más productos para el término '{term}'.")
                    break

                new_products = []
                for product in products:
                    product_id = product["id"]
                    if product_id not in seen_products:
                        new_products.append(product)
                        seen_products.add(product_id)
                        print(f"Producto añadido: {product['nombre']} - Precio: {product['precio']}")

                if new_products:
                    df_new = pd.DataFrame(new_products)
                    df_new.to_csv(csv_file, mode='a', header=False, index=False)
                    print(f"CSV actualizado. Nuevos productos guardados: {len(new_products)}")

                offset += limit
                time.sleep(1)

            except Exception as e:
                print(f"Error al procesar la solicitud: {e}")
                break

if __name__ == "__main__":
    csv_file = os.path.join(alcampo_folder, "productos_alcampo.csv")

    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"Archivo CSV eliminado: {csv_file}")

    base_terms = list(string.ascii_lowercase)
    search_terms = generate_search_terms(base_terms)

    fetch_all_products(search_terms, csv_file)
