import re
import requests
import json
import time
import csv

class Product:
    def __init__(self, product_id: str = "", price: float = 0.0, price_per_unit: str = "00.00", image: str = "",
                 name: str = "", category: str = "", brand: str = "Aldi", url: str = "", supermarket: str = "Aldi"):
        self.product_id = product_id
        self.price = price
        self.price_per_unit = price_per_unit
        self.image = image
        self.name = name
        self.category = category
        self.brand = brand
        self.url = url
        self.supermarket = supermarket

class AldiScraper:
    market_uri = (
        "https://l9knu74io7-dsn.algolia.net/1/indexes/*/queries"
        "?X-Algolia-Api-Key=19b0e28f08344395447c7bdeea32da58"
        "&X-Algolia-Application-Id=L9KNU74IO7"
    )

    def get_body_post(self, page_offer: int = None, page_assortment: int = None) -> str:
        requests_list = []
        if page_offer is not None:
            requests_list.append({
                "indexName": "prod_es_es_es_offers",
                "params": (
                    f"clickAnalytics=true&facets=%5B%5D&highlightPostTag=%3C%2Fais-highlight-0000000000%3E"
                    f"&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=12"
                    f"&page={page_offer}&query=&tagFilters="
                )
            })
        if page_assortment is not None:
            requests_list.append({
                "indexName": "prod_es_es_es_assortment",
                "params": (
                    f"clickAnalytics=true&facets=%5B%5D&highlightPostTag=%3C%2Fais-highlight-0000000000%3E"
                    f"&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=12"
                    f"&page={page_assortment}&query=&tagFilters="
                )
            })
        body = {
            "requests": requests_list
        }
        return json.dumps(body)

    def get_product_list(self, response_json_obj: dict, seen_products: set) -> list:
        product_list = []
        results = response_json_obj.get("results", [])

        if not results:
            return product_list

        result = results[0]
        products_json_list = result.get("hits", [])
        for product_json in products_json_list:
            name = product_json.get("productName", "")
            if name and name not in seen_products:
                price = product_json.get("salesPrice", 0.0)

                # Formatear el precio por unidad
                base_price_value = product_json.get("basePriceValue", 0.0)
                base_price_scale = product_json.get("basePriceScale", "")
                unit_price = f"{base_price_value}€/{base_price_scale}" if base_price_value and base_price_scale else f"{price}€/ud"

                # Limpiar espacios adicionales
                unit_price = unit_price.replace(" ", "")

                brand = product_json.get("brandName", "Aldi") or "Aldi"
                image = product_json.get("productPicture", "")
                url = product_json.get("productUrl", "")

                # Extraer el ID de la URL
                match = re.search(r'(\d+-\d+-\d+)\.article\.html', url)
                product_id = match.group(1) if match else ""

                # Extraer la categoría
                categories = product_json.get("categories", [])
                category = categories[0] if categories else "Sin categoría"

                product = Product(
                    product_id=product_id,
                    price=price,
                    price_per_unit=unit_price,
                    image=image,
                    name=name,
                    category=category,
                    brand=brand,
                    url=url,
                    supermarket="Aldi"
                )
                product_list.append(product)
                seen_products.add(name)

        return product_list

    def scrape_products(self, max_pages: int = 1000) -> list:
        url = self.market_uri
        headers = {"Content-Type": "application/json"}
        products = []
        seen_products = set()

        for page_offer in range(max_pages):
            body = self.get_body_post(page_offer=page_offer)
            try:
                response = requests.post(url, headers=headers, data=body)
                if response.status_code == 200:
                    response_json = response.json()
                    page_products = self.get_product_list(response_json, seen_products)

                    if not page_products:
                        print(f"No se encontraron más productos en la página de ofertas {page_offer}")
                        break

                    products.extend(page_products)
                    print(f"Página de ofertas {page_offer} procesada: {len(page_products)} productos encontrados.")
                    time.sleep(1)
                else:
                    print(f"Error en la solicitud: estado {response.status_code} en la página de ofertas {page_offer}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Error de conexión en la página de ofertas {page_offer}: {e}")
                break

        for page_assortment in range(max_pages):
            body = self.get_body_post(page_assortment=page_assortment)
            try:
                response = requests.post(url, headers=headers, data=body)
                if response.status_code == 200:
                    response_json = response.json()
                    page_products = self.get_product_list(response_json, seen_products)

                    if not page_products:
                        print(f"No se encontraron más productos en la página de surtido {page_assortment}")
                        break

                    products.extend(page_products)
                    print(f"Página de surtido {page_assortment} procesada: {len(page_products)} productos encontrados.")
                    time.sleep(1)
                else:
                    print(f"Error en la solicitud: estado {response.status_code} en la página de surtido {page_assortment}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Error de conexión en la página de surtido {page_assortment}: {e}")
                break

        return products

    def save_to_csv(self, products: list, filename: str):
        fieldnames = ['id', 'nombre', 'precio', 'precio_por_unidad', 'categoria', 'marca', 'imagen', 'url', 'supermercado']
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for product in products:
                writer.writerow([
                    product.product_id,
                    product.name,
                    product.price,
                    product.price_per_unit,
                    product.category,
                    product.brand,
                    product.image,
                    product.url,
                    product.supermarket
                ])
        print(f"Datos guardados en el archivo {filename}")

if __name__ == "__main__":
    aldi_scraper = AldiScraper()
    products = aldi_scraper.scrape_products(max_pages=1000)
    print(f"Total de productos extraídos: {len(products)}")
    aldi_scraper.save_to_csv(products, 'productos_aldi.csv')
