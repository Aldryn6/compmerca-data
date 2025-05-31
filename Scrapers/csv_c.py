import pandas as pd
import os
from datetime import datetime

# Configuración del logger
timestamp = datetime.now()
dt_string = timestamp.strftime("%d_%m_%Y")

# Obtener la ruta del directorio donde se encuentra el script
ruta_actual = os.path.dirname(os.path.abspath(__file__))

# Crear una lista para almacenar los DataFrames
lista_csv = []

# Diccionario extensivo de categorías
mapa_categorias = {
    # Alimentación general
    "Aceites y Vinagres": ["aceite", "vinagre", "especias", "sazonadores", "aderezos", "condimentos"],
    "Salsas y Untables": ["salsas", "mayonesa", "ketchup", "mostaza", "guacamole", "hummus", "pesto"],
    "Snacks y Aperitivos": ["aperitivos", "frutos secos", "snacks", "patatas fritas", "galletas saladas", "chips", "kikos"],
    "Panadería y Repostería": ["pan", "bollería", "pastelería", "galletas", "bizcochos", "donuts", "croissants"],
    "Dulces y Postres": ["chocolates", "turrones", "mousse", "natillas", "flanes", "golosinas", "mermeladas"],
    "Frutas Frescas": ["frutas", "manzanas", "peras", "uvas", "cítricos", "tropicales", "plátanos"],
    "Verduras y Hortalizas": ["verduras", "hortalizas", "ensaladas", "patatas", "cebollas", "ajos", "zanahorias"],
    "Lácteos": ["leche", "queso", "yogur", "nata", "mantequilla", "cremas lácteas", "kefir"],
    "Huevos": ["huevos", "claras de huevo", "ovoproductos"],
    "Carnes Frescas": ["carne", "pollo", "vacuno", "cerdo", "cordero", "hamburguesas", "salchichas"],
    "Charcutería y Fiambres": ["jamón", "fiambres", "embutidos", "chorizo", "pavo", "salami", "salchichón"],
    "Pescados y Mariscos": ["pescado", "atún", "sardinas", "pulpo", "calamares", "mariscos", "gambas"],
    "Pastas y Arroces": ["pasta", "arroz", "couscous", "fideos", "tallarines", "espaguetis"],
    "Legumbres": ["lentejas", "garbanzos", "alubias", "frijoles", "soja"],
    "Congelados": ["congelados", "croquetas", "empanadas", "pizzas", "tartas heladas", "verduras congeladas"],
    "Platos Preparados": ["platos preparados", "lasañas", "canelones", "caldos", "sopas", "purés", "ensaladas preparadas"],
    "Comida Internacional": ["mexicana", "oriental", "italiana", "sushi", "tex-mex", "latina", "hindú", "thai"],
    "Conservas Vegetales": ["conservas", "encurtidos", "aceitunas", "alcaparras", "pepinos", "berenjenas"],
    "Conservas de Carne": ["atún", "sardinas", "calamares", "pescado enlatado", "salchichas enlatadas"],
    "Salsas y Aliños": ["aliños", "vinagreta", "salsas dulces", "salsas picantes", "pasta para untar"],
    "Harinas y Panificación": ["harinas", "masa", "pan rallado", "levaduras", "sémolas", "preparados para pan"],
    
    # Bebidas
    "Agua y Bebidas Sin Gas": ["agua", "aguas con gas", "bebidas sin gas", "agua saborizada"],
    "Zumos y Néctares": ["zumos", "jugos", "néctares", "batidos", "smoothies"],
    "Bebidas Vegetales": ["leche de soja", "bebidas de avena", "bebidas de almendra", "leche vegetal", "bebidas ecológicas"],
    "Cerveza y Sidras": ["cerveza", "sidra", "cervezas especiales", "cervezas sin alcohol"],
    "Vinos y Licores": ["vino", "vino blanco", "vino tinto", "licores", "cava", "espumosos", "vermouth"],
    "Café e Infusiones": ["café", "té", "infusiones", "kombucha", "capuccino", "expresso"],
    
    # Higiene y cuidado personal
    "Cuidado del Cabello": ["champú", "acondicionadores", "mascarillas", "tratamientos capilares"],
    "Cuidado de la Piel": ["cremas", "lociones", "hidratantes", "cuidado facial", "crema solar", "antiedad"],
    "Higiene Bucal": ["cepillos dentales", "pasta de dientes", "colutorios", "hilo dental"],
    "Higiene Íntima": ["compresas", "tampones", "gel íntimo", "protegeslips"],
    "Cuidado Masculino": ["afeitado", "aftershave", "productos para barba"],
    
    # Limpieza y hogar
    "Limpieza General": ["detergentes", "suavizantes", "limpiadores", "desinfectantes"],
    "Limpieza de Cocina": ["lavavajillas", "limpiadores de horno", "quitagrasas"],
    "Limpieza de Baño": ["limpiadores de baño", "antical", "ambientadores"],
    "Ambientación y Fragancias": ["ambientadores", "aromatizantes", "velas aromáticas"],
    "Menaje y Cocina": ["utensilios de cocina", "platos", "cubiertos", "vasos", "manteles"],
    
    # Mascotas
    "Alimentos para Mascotas": ["perros", "gatos", "pienso", "comida húmeda para mascotas"],
    "Accesorios para Mascotas": ["juguetes para mascotas", "camas para mascotas", "higiene mascotas"],
    
    # Ocio, deportes y tecnología
    "Electrodomésticos": ["frigoríficos", "lavadoras", "microondas", "cafeteras", "planchas"],
    "Pequeños Electrodomésticos": ["batidoras", "aspiradoras", "tostadoras", "licuadoras"],
    "Electrónica": ["móviles", "tablets", "ordenadores", "gaming", "consolas"],
    "Material Deportivo": ["bicicletas", "patinetes", "material deportivo", "pesas", "yoga"],
    "Juguetes": ["juguetes", "puzzles", "muñecas", "juegos de mesa", "figuras de acción"],
    "Papelería": ["papelería", "bolígrafos", "libretas", "material escolar"],
    
    # Salud y bienestar
    "Botiquín y Salud": ["antisépticos", "vitaminas", "primeros auxilios", "parafarmacia"],
    "Productos Nutricionales": ["proteínas", "sustitutivos alimenticios", "superalimentos", "control de peso"],
    
    # Otros
    "Decoración y Hogar": ["decoración", "jardinería", "almohadas", "textil hogar"],
    "Vehículos y Accesorios": ["aceites para coche", "aditivos", "limpiaparabrisas"],
    "Temporada": ["navidad", "roscones", "dulces de temporada", "cestas navideñas"],
    "Otros": []  # Categorías no clasificadas
}

def simplificar_categoria(categoria):
    if not isinstance(categoria, str):  # Verificar si no es una cadena
        return "Otros"  # Asignar una categoría por defecto
    categoria = categoria.lower()  # Convertir la categoría a minúsculas
    for nueva_categoria, palabras_clave in mapa_categorias.items():
        if any(palabra in categoria for palabra in palabras_clave):
            return nueva_categoria
    return "Otros"

# Recorrer todos los subdirectorios y archivos
for raiz, directorios, archivos in os.walk(ruta_actual):
    for archivo in archivos:
        if "productos_" in archivo:  # Filtrar archivos que contengan '_productos.csv' en su nombre
            print(f"Encontrado archivo: {archivo}")
            ruta_completa = os.path.join(raiz, archivo)
            df = pd.read_csv(ruta_completa)  # Leer cada CSV como un DataFrame
            lista_csv.append(df)

# Combinar todos los DataFrames en uno solo
if lista_csv:  # Verificar que haya archivos encontrados
    df_combinado = pd.concat(lista_csv, ignore_index=True)

    # Simplificar las categorías
    if 'categoria' in df_combinado.columns:
        df_combinado['categoria'] = df_combinado['categoria'].fillna("Otros")  # Reemplazar NaN por "Otros"
        df_combinado['categoria'] = df_combinado['categoria'].apply(simplificar_categoria)
        
    # Contar duplicados antes de eliminarlos
    duplicados = df_combinado.duplicated(subset=['nombre', 'supermercado']).sum()
    print(f"Número de duplicados encontrados: {duplicados}")

    # Eliminar duplicados
    df_combinado.drop_duplicates(subset=['nombre', 'supermercado'], inplace=True)

    # Guardar el CSV combinado en el mismo directorio
    ruta_guardado = os.path.join(ruta_actual, "data" + dt_string + ".csv") 
    df_combinado.to_csv(ruta_guardado, index=False)

    print(f"CSV combinado guardado exitosamente en {ruta_guardado}.")
    
    #Borrar los archivos originales cuando se haya terminado
    for raiz, directorios, archivos in os.walk(ruta_actual):
        for archivo in archivos:
            if "productos_" in archivo:  # Filtrar archivos que contengan '_productos.csv' en su nombre
                print(f"Borrando archivo: {ruta_completa}")
                ruta_completa = os.path.join(raiz, archivo)
                os.remove(ruta_completa)
else:
    print("No se encontraron archivos con 'productos_' en su nombre.")
