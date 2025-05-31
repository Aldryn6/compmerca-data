import requests
import pandas as pd

dferror = pd.read_csv("errores.csv")
for error in dferror["0"]:
    print("Este me dio error: "+str(error))
    print("Motivo: "+str(requests.get("https://tienda.mercadona.es/api/products/" + str(error), headers={"Accept": "application/json"}).status_code))
