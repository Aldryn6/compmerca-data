import json
import re
import pandas as pd
import requests

respuestaPrevia = "a"
respuesta = ""
pagina = 1
productos = []

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
    'Accept': '*/*',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer': 'https://supermercado.eroski.es/es/search/results/?q=%s&suggestionsFilter=false',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://supermercado.eroski.es',
    'DNT': '1',
    'Sec-GPC': '1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Connection': 'keep-alive',
}

params = {
    'suggestionsFilter': 'false',
}

# Modificar la función para incluir los campos requeridos
def extract_product_info(data):
    products = []

    for item in data['inits']:
        if isinstance(item, list) and len(item) > 3 and item[0].startswith(
                'components/product/productRatingStatistics:init'):
            product_id = item[2]
            product_url = item[3]

            tracking_data = next((x for x in data['inits'] if isinstance(x, list) and x[0] == 'common/tracking:init'),
                                 None)
            if tracking_data:
                tracking_info = json.loads(re.search(r'\{"event":"ProductList",.*\}', tracking_data[1]).group())
                impressions = tracking_info.get('ecommerce', {}).get('impressions', [])
                product_info = next((prod for prod in impressions if prod.get('id') == product_id), None)
                if product_info:
                    product_name = product_info.get('name')
                    product_price = product_info.get('price')
                    product_brand = product_info.get('brand')
                    product_category = product_info.get('category')
                    product_image = 'https://supermercado.eroski.es/images/' + product_id + '.jpg' # Añadimos la imagen
                    price_per_unit = product_info.get('price_per_unit', product_price + '€/ud')  # Precio por unidad opcional
                    supermercado = 'Eroski'  # Añadimos el supermercado

                    products.append({
                        'id': product_id,
                        'nombre': product_name,
                        'precio': product_price,
                        'precio_por_unidad': price_per_unit,
                        'categoria': product_category,
                        'marca': product_brand,
                        'imagen': product_image,
                        'url': product_url,
                        'supermercado': supermercado,
                    })

    return products


# Proceso de scraping con límite de 50 productos
while not(respuesta == respuestaPrevia):
    data = {
        't:zoneid': 'productListZone',
        'pageNumber': pagina,
    }

    response = requests.post(
        'https://supermercado.eroski.es/es/search/results.productlist:loadpage',
        params=params,
        headers=headers,
        data=data,
    )
    respuestaPrevia = respuesta
    respuesta = response.text

    nuevos_productos = extract_product_info(response.json()["_tapestry"])
    productos += nuevos_productos
    
    
    pagina += 1
    print(f"Scrapeando página {pagina}, total productos: {len(productos)}")





print("Scraping terminado")
df = pd.DataFrame(productos)
df.to_csv('productos_eroski.csv', encoding='utf-8', index=False)
