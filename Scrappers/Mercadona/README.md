# Proyecto Computación

El proyecto se compone de dos scripts de Python:  
**`MercadonaScrap.py`** y **`SegundaOpinion.py`**.

## MercadonaScrap.py

**MercadonaScrap** descarga el `sitemap.xml` de la página de Mercadona y scrapea su API para obtener los datos de sus productos.  
Genera dos archivos:

- **Mercadona.csv**: Un CSV con los JSON de los productos.
- **errores.csv**: Un CSV con los productos que han dado error al obtener sus datos.

## SegundaOpinion.py

**SegundaOpinion** comprueba los productos de `errores.csv`, realiza las requests de nuevo e imprime por pantalla los códigos de estado de las requests.
Sirve para determinar por qué no puedes descargar ciertos datos (Generalmente se debe a que hay enlaces que hacen referencia a productos que han sido borrados).
