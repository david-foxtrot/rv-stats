# Archivo: scripts/scraper.py
# Versión: 35.1 (Con detector de equipos faltantes)

import json
import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- FUNCIONES AUXILIARES ---

def load_team_map(project_root):
    """Carga el mapa de equipos base desde src/data/teams.json."""
    teams_path = os.path.join(project_root, 'src', 'data', 'teams.json')
    with open(teams_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_json_from_url(driver, url):
    """Navega a una URL y extrae el contenido JSON de la etiqueta <pre>."""
    driver.get(url)
    time.sleep(1.5)
    return json.loads(driver.find_element(By.TAG_NAME, "pre").text)

# --- FUNCIÓN MODIFICADA ---
def update_standings(driver, league_id, season_id, team_map):
    """Obtiene y formatea la tabla de clasificación. AHORA AVISA SI FALTA UN EQUIPO."""
    URL_API = f"https://api.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/standings/total"
    dados = get_json_from_url(driver, URL_API)
    if 'error' in dados: return []
    tabela_rows = dados.get('standings', [{}])[0].get('rows', [])
    tabela_formatada = []
    for row in tabela_rows:
        time_api = row.get('team', {}).get('name', 'N/A')
        
        # Comprobamos si el nombre del equipo de la API existe en nuestro mapa
        if time_api in team_map:
            # Si existe, lo procesamos normalmente
            equipe_base = team_map[time_api]
            equipe_formatada = {
                "pos": row.get('position', 0),
                "time": time_api,
                "display_name": equipe_base.get('display_name') or time_api,
                "slug": equipe_base['slug'],
                "logo": equipe_base['logo'],
                "pts": row.get('points', 0),
                "v": row.get('wins', 0),
                "e": row.get('draws', 0),
                "d": row.get('losses', 0),
                "gp": row.get('scoresFor', 0),
                "gc": row.get('scoresAgainst', 0),
                "sg": row.get('scoresFor', 0) - row.get('scoresAgainst', 0)
            }
            tabela_formatada.append(equipe_formatada)
        else:
            # --- ¡AVISO IMPORTANTE! ---
            # Si no existe, imprimimos un mensaje para saber qué equipo falta.
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(f"ATENCIÓN: El equipo '{time_api}' de la API no fue encontrado en tu 'teams.json' y será omitido.")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            
    return tabela_formatada

def format_event(evento, team_map):
    """Formatea un evento individual (partido) en el formato deseado."""
    time_casa_api = evento.get('homeTeam', {}).get('name', 'N/A')
    time_fora_api = evento.get('awayTeam', {}).get('name', 'N/A')
    if time_casa_api in team_map and time_fora_api in team_map:
        placar_casa = evento.get('homeScore', {}).get('current', None)
        placar_fora = evento.get('awayScore', {}).get('current', None)
        status_obj = evento.get('status', {})
        status_code = status_obj.get('code', 0)
        status_desc = status_obj.get('description', 'Agendado')
        canal = evento.get('tvChannel',{}).get('name', 'Não informado') if evento.get('tvChannel') else 'Não informado'
        info = status_desc.capitalize()
        if status_code == 0:
            timestamp = evento.get('startTimestamp', 0)
            info = datetime.fromtimestamp(timestamp).strftime('%d/%m %H:%M')
        return { "campeonato": evento.get('tournament', {}).get('name', 'N/A'), "canal": canal, "timeCasa": team_map[time_casa_api], "timeFora": team_map[time_fora_api], "placarCasa": placar_casa, "placarFora": placar_fora, "info": info }
    return None

def update_team_schedules(driver, team_id, team_map):
    """Obtiene los próximos y últimos partidos para un ID de equipo específico."""
    URL_NEXT = f"https://api.sofascore.com/api/v1/team/{team_id}/events/next/0"
    URL_LAST = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/0"
    next_events_data = get_json_from_url(driver, URL_NEXT)
    last_events_data = get_json_from_url(driver, URL_LAST)
    proximos_jogos = [p for p in [format_event(e, team_map) for e in next_events_data.get('events', [])] if p]
    ultimos_resultados = [p for p in [format_event(e, team_map) for e in last_events_data.get('events', [])] if p]
    return {"proximos_jogos": proximos_jogos[:5], "ultimos_resultados": ultimos_resultados[:5]}


# --- FUNCIÓN PRINCIPAL ---
def main():
    start_time = time.time()
    options = Options()
    options.add_argument('--headless'); options.add_argument('--no-sandbox')
    service = ChromeService(ChromeDriverManager().install()); driver = webdriver.Chrome(service=service, options=options)
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__)); project_root = os.path.dirname(script_dir)
        
        content_dir = os.path.join(project_root, 'src', 'content')
        teams_output_dir = os.path.join(content_dir, 'teams')
        standings_output_dir = os.path.join(content_dir, 'standings')
        os.makedirs(teams_output_dir, exist_ok=True)
        os.makedirs(standings_output_dir, exist_ok=True)
        
        print("🤖 Iniciando o robô v35.1 (Detector de equipos faltantes)...")
        
        team_map = load_team_map(project_root)
        print(f"✅ Mapa com {len(team_map)} equipes carregado.")

        print(" -> Obteniendo cookies de sesión de Sofascore...")
        driver.get("https://www.sofascore.com"); time.sleep(3)

        # --- TAREA 1: OBTENER TABLAS ---
        print("\n--- TAREA 1: OBTENIENDO TABLAS DE CLASIFICACIÓN ---")
        all_teams_map = {}
        all_leagues_info = [
            {"name": "Série A", "slug": "serie-a", "id": 325, "season_id": 72034},
            {"name": "Série B", "slug": "serie-b", "id": 390, "season_id": 72603}
        ]
        for league in all_leagues_info:
            print(f"📈 Atualizando tabela da {league['name']} usando season_id {league['season_id']}...")
            path = os.path.join(standings_output_dir, f"{league['slug']}.json")
            tabela_data = update_standings(driver, league['id'], league['season_id'], team_map) # Esta función ahora avisará si falta algo
            
            with open(path, 'w', encoding='utf-8') as f: json.dump(tabela_data, f, ensure_ascii=False, indent=4)
            print(f"   -> ✅ Tabela da {league['name']} salva.")

            for team_standings_info in tabela_data:
                team_name = team_standings_info['time']
                if team_name in team_map:
                    team_info_with_league = team_map[team_name].copy()
                    team_info_with_league['league_slug'] = league['slug']
                    all_teams_map[team_name] = team_info_with_league
        
        print("✅ Tabelas de classificação obtidas.")

        # --- TAREA 2: OBTENER CALENDARIOS ---
        print("\n--- TAREA 2: OBTENIENDO CALENDARIOS ---")
        teams_to_process = sorted(all_teams_map.items())
        total_teams = len(teams_to_process)

        for index, (team_name, team_info) in enumerate(teams_to_process):
            print(f"[{index+1}/{total_teams}] Processando {team_info['display_name']} (ID: {team_info['id']})...")
            
            schedule = update_team_schedules(driver, team_info['id'], team_map)
            
            team_file_content = {"team_info": team_info, **schedule}
            
            # DEBUG: Imprimir para verificar consistencia
            try:
                proximo_jogo = team_file_content["proximos_jogos"][0]
                time_casa = proximo_jogo["timeCasa"]["display_name"]
                time_fora = proximo_jogo["timeFora"]["display_name"]
                print(f"   -> ✅ Próximo partido para [{team_info['display_name']}]: {time_casa} vs {time_fora}")
            except (IndexError, KeyError):
                print(f"   -> ✅ No se encontraron próximos partidos para [{team_info['display_name']}].")

            team_file_path = os.path.join(teams_output_dir, f"{team_info['slug']}.json")
            with open(team_file_path, 'w', encoding='utf-8') as f: json.dump(team_file_content, f, ensure_ascii=False, indent=4)
        
        print("\n✅ Todos os calendários foram processados.")
    
    finally:
        driver.quit()
        end_time = time.time(); duration = end_time - start_time
        print(f"\n✅ Robô finalizado.")
        print(f"⏱️  Tempo de execução: {duration:.2f} segundos.")

if __name__ == "__main__":
    main()