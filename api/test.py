import requests
def generate_country(ip_address):
    api_token = "3c6521274af1bf"
    url = f"https://ipinfo.io/{ip_address}?token={api_token}"

    try:
        response = requests.get(url, timeout=1)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP (4xx, 5xx)
        data = response.json()
        return data.get('country', "Unknown")  # Utilisation de `.get()` pour éviter une KeyError
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")  # Afficher l'erreur pour debug
        return "Unknown"
ip_adress=["120.159.135.8","160.117.111.61","148.143.48.225","51.156.107.137","189.114.247.106","109.64.46.138","64.237.19.118"]
for ip in ip_adress:
 print(generate_country(ip))