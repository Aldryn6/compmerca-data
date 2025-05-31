import subprocess

# URL del servidor local
BASE_URL = "https://apimerca.aldryng.xyz"
LOGIN_URL = f"{BASE_URL}/admin/login/"  # Ajusta según tu endpoint de login
IMPORT_URL = f"{BASE_URL}/productos/importar-csv/"

# Obtener la cookie CSRF usando curl
subprocess.run(f"curl -c cookies.txt {LOGIN_URL}", shell=True, check=True)

# Extraer el token CSRF desde las cookies
csrf_token = subprocess.run("grep csrftoken cookies.txt | awk '{print $7}'", shell=True, check=True, capture_output=True, text=True).stdout.strip()

if not csrf_token:
    print("Error: No se pudo obtener el token CSRF")
    exit(1)

print(f"CSRF Token: {csrf_token}")

# Realizar la petición POST con el token CSRF usando curl
subprocess.run(
    f"curl -v -c cookies.txt -b cookies.txt "
    f"-H 'X-CSRFToken: {csrf_token}' "
    f"-H 'Referer: {BASE_URL}' "
    f"-X POST {IMPORT_URL}",
    shell=True, check=True
)
