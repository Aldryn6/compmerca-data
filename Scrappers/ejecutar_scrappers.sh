#!/bin/bash

cd /opt/python_data
echo ejecutando alcampo
python3 Alcampo/alcampo.py >> alcampo.log
echo ejecutando aldi
python3 Aldi/AldiScrap.py >> aldi.log
echo ejecutando carrefour
python3 Carrefour/main.py >> carrefour.log
echo ejecutando dia
python3 Dia/Dia.py >> dia.log
echo ejecutando eroski
python3 Eroski/Eroski_Scrap.py >> eroski.log
echo ejecutando hipercor
python3 Hipercor/code.py >> hipercor.log
echo ejecutando mercadona
python3 Mercadona/MercadonaScrap.py >> mercadona.log
echo ejecutando csv_c
python3 csv_c.py >> csvc.log
echo ejecutando to_sql
python3 to_sql.py >> tosql.log
echo ejecutando to_sql-local
python3 to_sql-local.py >> tosql-local-log
curl -XPOST 'http://db.aldryng.xyz/boot' -H "Transfer-Encoding: chunked" --upload-file compmerca.db



