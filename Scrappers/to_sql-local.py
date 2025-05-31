import csv
import sqlite3
from datetime import datetime

# Nombre del archivo de la base de datos SQLite
db_file = 'compmerca.db'

# Conexión a la base de datos SQLite
conexion = sqlite3.connect(db_file)
cursor = conexion.cursor()

# Función para verificar si el precio ha cambiado
def precio_cambiado(cursor, id_producto, nuevo_precio):
    query = """
    SELECT Precio FROM HistorialPrecios 
    WHERE IDProducto = ? 
    ORDER BY Date DESC LIMIT 1
    """
    cursor.execute(query, (id_producto,))
    resultado = cursor.fetchone()
    if resultado:
        precio_actual = resultado[0]
        return nuevo_precio != precio_actual
    return True  # Si no hay registros, el precio se considera cambiado

# Leer el archivo CSV
csv_file = 'data' + datetime.now().strftime('%d_%m_%Y') + '.csv'
counter = 0  # Contador de productos procesados

try:
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print("Leyendo datos del archivo CSV...")

        for row in reader:
            # Insertar en la tabla Supermercado si no existe
            supermercado_nombre = row['supermercado']
            cursor.execute("SELECT IDSuper FROM Supermercado WHERE Nombre = ?", (supermercado_nombre,))
            supermercado_result = cursor.fetchone()
            if not supermercado_result:
                cursor.execute("INSERT INTO Supermercado (Nombre) VALUES (?)", (supermercado_nombre,))
                conexion.commit()
                id_super = cursor.lastrowid
            else:
                id_super = supermercado_result[0]

            # Insertar en la tabla Productos si no existe
            cursor.execute("SELECT IDProducto FROM Productos WHERE URLProducto = ?", (row['url'],))
            producto_result = cursor.fetchone()
            if not producto_result:
                precio = float(row['precio'])
                cursor.execute("""
                    INSERT INTO Productos 
                    (IDInterno, Nombre, Precio, PrecioUnidad, Imagen, Supermercado, Categoria, Marca, URLProducto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['id'],
                    row['nombre'],
                    precio,
                    row['precio_por_unidad'],
                    row['imagen'],
                    id_super,
                    row['categoria'],
                    row['marca'],
                    row['url']
                ))
                conexion.commit()
                id_producto = cursor.lastrowid
            else:
                id_producto = producto_result[0]
                # Actualizar el precio y otros detalles del producto existente
                cursor.execute("""
                    UPDATE Productos
                    SET Precio = ?, PrecioUnidad = ?, Imagen = ?, Categoria = ?, Marca = ?
                    WHERE IDProducto = ?
                """, (
                    float(row['precio']),
                    row['precio_por_unidad'],
                    row['imagen'],
                    row['categoria'],
                    row['marca'],
                    id_producto
                ))
                conexion.commit()

            # Insertar en HistorialPrecios si el precio ha cambiado
            if precio_cambiado(cursor, id_producto, float(row['precio'])):
                cursor.execute("""
                    INSERT INTO HistorialPrecios (Date, Precio, IDProducto)
                    VALUES (?, ?, ?)
                """, (datetime.now().strftime('%Y-%m-%d'), float(row['precio']), id_producto))
                conexion.commit()

            # Incrementar el contador de productos procesados
            counter += 1
            if counter % 100 == 0:
                print(f"{counter} productos procesados...")
                
except FileNotFoundError:
    print(f"El archivo {csv_file} no se encuentra en el directorio actual.")
    exit(1)

# SQL para consolidar productos duplicados y actualizar historial de precios
print("Consolidando productos duplicados...")

# Crear la tabla temporal
cursor.executescript("""
-- Crear una tabla temporal para identificar productos duplicados
CREATE TEMPORARY TABLE ProductosDuplicados AS
SELECT 
    MAX(IDProducto) AS IDPrincipal, -- Mantener el último ID registrado
    IDProducto AS IDDuplicado,
    Nombre,
    Supermercado
FROM Productos
GROUP BY Nombre, Supermercado
HAVING COUNT(*) > 1;
""")

# Actualizar el Historial de Precios
cursor.execute("""
UPDATE HistorialPrecios
SET IDProducto = (
    SELECT PD.IDPrincipal
    FROM ProductosDuplicados PD
    WHERE PD.IDDuplicado = HistorialPrecios.IDProducto
)
WHERE IDProducto IN (
    SELECT IDDuplicado
    FROM ProductosDuplicados
);
""")
conexion.commit()

# Consolidar los campos dinámicos en Productos
cursor.execute("""
UPDATE Productos
SET 
    IDInterno = (SELECT P.IDInterno FROM Productos P WHERE P.IDProducto = (
        SELECT PD.IDPrincipal FROM ProductosDuplicados PD WHERE PD.IDPrincipal = Productos.IDProducto
    )),
    Precio = (SELECT P.Precio FROM Productos P WHERE P.IDProducto = (
        SELECT PD.IDPrincipal FROM ProductosDuplicados PD WHERE PD.IDPrincipal = Productos.IDProducto
    )),
    PrecioUnidad = (SELECT P.PrecioUnidad FROM Productos P WHERE P.IDProducto = (
        SELECT PD.IDPrincipal FROM ProductosDuplicados PD WHERE PD.IDPrincipal = Productos.IDProducto
    )),
    Imagen = (SELECT P.Imagen FROM Productos P WHERE P.IDProducto = (
        SELECT PD.IDPrincipal FROM ProductosDuplicados PD WHERE PD.IDPrincipal = Productos.IDProducto
    )),
    URLProducto = (SELECT P.URLProducto FROM Productos P WHERE P.IDProducto = (
        SELECT PD.IDPrincipal FROM ProductosDuplicados PD WHERE PD.IDPrincipal = Productos.IDProducto
    ))
WHERE IDProducto IN (
    SELECT IDPrincipal FROM ProductosDuplicados
);
""")
conexion.commit()

# Eliminar los productos duplicados en la tabla Productos
cursor.execute("""
DELETE FROM Productos
WHERE IDProducto IN (
    SELECT IDDuplicado
    FROM ProductosDuplicados
    WHERE IDDuplicado != IDPrincipal
);
""")
conexion.commit()

# Logeo de estadísticas antes de dropear la tabla
cursor.execute("SELECT COUNT(*) FROM ProductosDuplicados")
duplicados_mergeados = cursor.fetchone()[0]
print(f"Productos duplicados mergeados: {duplicados_mergeados}")

# Limpiar la tabla temporal
cursor.execute("DROP TABLE IF EXISTS ProductosDuplicados;")
conexion.commit()

# Verificar el total de entradas en HistorialPrecios después de consolidación
cursor.execute("SELECT COUNT(*) FROM HistorialPrecios")
total_historial = cursor.fetchone()[0]
print(f"Total de entradas en HistorialPrecios después de consolidación: {total_historial}")
