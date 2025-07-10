# Archivo: scripts/verificar_ids_2025.py
# Propósito: Obtener una lista de Nombres e IDs de los equipos
# usando los IDs de temporada 2025 proporcionados.

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def get_json_from_url(driver, url):
    """Navega a una URL y extrae el contenido JSON."""
    driver.get(url)
    time.sleep(2)
    try:
        pre_element = driver.find_element(By.TAG_NAME, "pre")
        return json.loads(pre_element.text)
    except Exception as e:
        print(f"  -> No se pudo obtener el JSON de la URL: {url}")
        print(f"  -> Error: {e}")
        return None

def print_team_ids_from_league(driver, league_name, url):
    """Obtiene y imprime los nombres e IDs de los equipos de una URL de API específica."""
    print(f"\n--- OBTENIENDO IDs PARA: {league_name} ---\n")
    data = get_json_from_url(driver, url)
    
    if not data:
        print(f"No se pudieron obtener datos para {league_name}.")
        return

    try:
        rows = data.get('standings', [{}])[0].get('rows', [])
        if not rows:
            print(f"No se encontraron equipos para {league_name}.")
            return
            
        teams = sorted([row.get('team', {}) for row in rows], key=lambda x: x.get('name', ''))

        for team in teams:
            team_name = team.get('name', 'N/A')
            team_id = team.get('id', 'N/A')
            print(f"- {team_name}: {team_id}")
            
    except (KeyError, IndexError):
        print(f"La estructura de datos de la API para {league_name} es inesperada.")

def main():
    options = Options()
    options.add_argument('--headless'); options.add_argument('--no-sandbox')
    service = ChromeService(ChromeDriverManager().install()); driver = webdriver.Chrome(service=service, options=options)
    
    print("Iniciando la verificación de IDs de equipos (Temporada 2025)...")
    try:
        print(" -> Obteniendo cookies de sesión de Sofascore...")
        driver.get("https://www.sofascore.com"); time.sleep(3)
        
        # --- IDs de temporada para 2025 (según lo proporcionado) ---
        leagues_urls = [
            {
                "name": "Liga Futve  (Temporada 72034)",
                "url": "https://api.sofascore.com/api/v1/unique-tournament/231/season/71012/standings/total"
            },
            {
                "name": "Eliminatorias 2026 (Temporada 72603)",
                "url": "https://api.sofascore.com/api/v1/unique-tournament/295/season/53820/standings/total"
            }
        ]
        
        for league in leagues_urls:
            print_team_ids_from_league(driver, league['name'], league['url'])
            
    finally:
        driver.quit()
        
    print("\n--- VERIFICACIÓN COMPLETA ---")
    print("Usa esta lista para corregir los IDs en tu archivo 'src/data/teams.json'.")

if __name__ == "__main__":
    main()