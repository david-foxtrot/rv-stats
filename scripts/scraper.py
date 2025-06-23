import json
import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- TEAM_MAP DEFINITIVO (BASEADO NOS DADOS REAIS DA API) ---
TEAM_MAP = {
    # Série A
    "Flamengo": {"id": 1963, "sigla": "FLA", "logo": "/logos/flamengo.svg", "estadio": "Maracanã"},
    "Cruzeiro": {"id": 1969, "sigla": "CRU", "logo": "/logos/cruzeiro.svg", "estadio": "Mineirão"},
    "Red Bull Bragantino": {"id": 1982, "sigla": "BGT", "logo": "/logos/rb_bragantino.svg", "estadio": "Nabi Abi Chedid"},
    "Palmeiras": {"id": 1966, "sigla": "PAL", "logo": "/logos/palmeiras.svg", "estadio": "Allianz Parque"},
    "Bahia": {"id": 1957, "sigla": "BAH", "logo": "/logos/bahia.svg", "estadio": "Arena Fonte Nova"},
    "Fluminense": {"id": 1968, "sigla": "FLU", "logo": "/logos/fluminense.svg", "estadio": "Maracanã"},
    "Atlético Mineiro": {"id": 1977, "sigla": "CAM", "logo": "/logos/atletico_mg.svg", "estadio": "Arena MRV"},
    "Botafogo": {"id": 1958, "sigla": "BOT", "logo": "/logos/botafogo.svg", "estadio": "Nilton Santos"},
    "Corinthians": {"id": 1979, "sigla": "COR", "logo": "/logos/corinthians.svg", "estadio": "Neo Química Arena"},
    "Grêmio": {"id": 1954, "sigla": "GRE", "logo": "/logos/gremio.svg", "estadio": "Arena do Grêmio"},
    "Vasco da Gama": {"id": 1981, "sigla": "VAS", "logo": "/logos/vasco.svg", "estadio": "São Januário"},
    "São Paulo": {"id": 1960, "sigla": "SAO", "logo": "/logos/sao_paulo.svg", "estadio": "Morumbi"},
    "Santos": {"id": 1961, "sigla": "SAN", "logo": "/logos/santos.svg", "estadio": "Vila Belmiro"},
    "Vitória": {"id": 1978, "sigla": "VIT", "logo": "/logos/vitoria.svg", "estadio": "Barradão"},
    "Internacional": {"id": 1967, "sigla": "INT", "logo": "/logos/internacional.svg", "estadio": "Beira-Rio"},
    "Fortaleza": {"id": 1959, "sigla": "FOR", "logo": "/logos/fortaleza.svg", "estadio": "Castelão"},
    "Juventude": {"id": 1998, "sigla": "JUV", "logo": "/logos/juventude.svg", "estadio": "Alfredo Jaconi"},
    "Criciúma": {"id": 1974, "sigla": "CRI", "logo": "/logos/criciuma.svg", "estadio": "Heriberto Hülse"},
    "Atlético Goianiense": {"id": 5324, "sigla": "ATL-GO", "logo": "/logos/atletico_go.svg", "estadio": "Antônio Accioly"},
    "Cuiabá": {"id": 15486, "sigla": "CUI", "logo": "/logos/cuiaba.svg", "estadio": "Arena Pantanal"},
    "Athletico": {"id": 1970, "sigla": "CAP", "logo": "/logos/atletico_pr.svg", "estadio": "Ligga Arena"},
    
    # Série B (Completado com sua lista)
    "Goiás": {"id": 1956, "sigla": "GOI", "logo": "/logos/goias.svg", "estadio": "Serrinha"},
    "Novorizontino": {"id": 23419, "sigla": "NOV", "logo": "/logos/novorizontino.svg", "estadio": "Dr. Jorge Ismael de Biasi"},
    "Coritiba": {"id": 1972, "sigla": "CFC", "logo": "/logos/coritiba.svg", "estadio": "Couto Pereira"},
    "CRB": {"id": 1988, "sigla": "CRB", "logo": "/logos/crb.svg", "estadio": "Estádio Rei Pelé"},
    "Avaí": {"id": 1973, "sigla": "AVA", "logo": "/logos/avai.svg", "estadio": "Estádio da Ressacada"},
    "Remo": {"id": 1983, "sigla": "REM", "logo": "/logos/remo.svg", "estadio": "Baenão"},
    "Chapecoense": {"id": 3488, "sigla": "CHA", "logo": "/logos/chapecoense.svg", "estadio": "Arena Condá"},
    "América Mineiro": {"id": 1976, "sigla": "AMG", "logo": "/logos/america_mg.svg", "estadio": "Independência"},
    "Vila Nova FC": {"id": 1989, "sigla": "VIL", "logo": "/logos/vila_nova.svg", "estadio": "Onésio Brasileiro Alvarenga"},
    "Operário-PR": {"id": 23207, "sigla": "OPE", "logo": "/logos/operario_pr.svg", "estadio": "Germano Krüger"},
    "Botafogo-SP": {"id": 1994, "sigla": "BOT-SP", "logo": "/logos/botafogo_sp.svg", "estadio": "Santa Cruz"},
    "Amazonas FC": {"id": 292837, "sigla": "AMA", "logo": "/logos/amazonas.svg", "estadio": "Arena da Amazônia"},
    "Volta Redonda": {"id": 2007, "sigla": "VOL", "logo": "/logos/volta_redonda.svg", "estadio": "Raulino de Oliveira"},
    "Paysandu SC": {"id": 1985, "sigla": "PAY", "logo": "/logos/paysandu_sc.svg", "estadio": "Curuzu"},
    "Athletic Club": {"id": 37402, "sigla": "ATH", "logo": "/logos/athletic_club_mg.svg", "estadio": "Arena Unimed"},
    "Mirassol": {"id": 3467, "sigla": "MIR", "logo": "/logos/mirassol.svg", "estadio": "José Maria de Campos Maia"},
    "Ceará": {"id": 1987, "sigla": "CEA", "logo": "/logos/ceara.svg", "estadio": "Castelão"},
    "Sport Recife": {"id": 1962, "sigla": "SPO", "logo": "/logos/sport.svg", "estadio": "Ilha do Retiro"},
}

# Configuração do Selenium
options = Options()
options.add_argument('--headless'); options.add_argument('--no-sandbox'); options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
service = ChromeService(ChromeDriverManager().install()); driver = webdriver.Chrome(service=service, options=options)

# Caminhos dos arquivos
script_dir = os.path.dirname(__file__); project_root = os.path.dirname(script_dir)
partidos_output_path = os.path.join(project_root, 'src', 'data', 'partidos.json')
tabela_a_output_path = os.path.join(project_root, 'src', 'data', 'tabela-serie-a.json')
tabela_b_output_path = os.path.join(project_root, 'src', 'data', 'tabela-serie-b.json')
timestamp_output_path = os.path.join(project_root, 'src', 'data', 'last-update.json')

def get_json_from_url(url):
    driver.get(url)
    time.sleep(2)
    json_text = driver.find_element(By.TAG_NAME, "pre").text
    return json.loads(json_text)

def update_standings(league_name, league_id, season_id, output_path):
    print(f"📈 Atualizando tabela da {league_name}...")
    URL_API = f"https://api.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/standings/total"
    try:
        driver.get(URL_API)
        time.sleep(1)
        json_text = driver.find_element(By.TAG_NAME, "pre").text
        dados = json.loads(json_text)

        if 'error' in dados:
            print(f"❌ A API da {league_name} devolveu um erro INESPERADO.")
            return

        tabela_rows = dados.get('standings', [{}])[0].get('rows', [])
        tabela_formatada = []
        for row in tabela_rows:
            time_api = row.get('team', {}).get('name', 'N/A')
            if time_api in TEAM_MAP:
                equipe = { "pos": row.get('position', 0), "time": time_api, "slug": time_api.lower().replace(' ', '-').replace('é', 'e').replace('ã', 'a').replace('ê', 'e'), "logo": TEAM_MAP[time_api]['logo'], "pts": row.get('points', 0), "v": row.get('wins', 0), "e": row.get('draws', 0), "d": row.get('losses', 0), "gp": 0, "gc": 0, "sg": 0 }
                tabela_formatada.append(equipe)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tabela_formatada, f, ensure_ascii=False, indent=4)
        print(f"✅ Tabela da {league_name} salva com {len(tabela_formatada)} equipes.")
    except Exception as e:
        print(f"❌ Erro ao atualizar a tabela da {league_name}: {e}")

def main():
    print("🤖 Iniciando o robô FINAL...")
    try:
        print("➡️  Navegando para www.sofascore.com para obter cookies...")
        driver.get("https://www.sofascore.com")
        time.sleep(3)
        print("✅ Cookies obtidos.")

        # Foco exclusivo em obter as tabelas da API estável
        update_standings("Série A", 325, 72034, tabela_a_output_path)
        print("-" * 30)
        update_standings("Série B", 390, 72603, tabela_b_output_path)

        # Adicionar o timestamp no final
        print("-" * 30)
        print("🕒 Registrando o horário da atualização...")
        now_utc = datetime.utcnow()
        now_brasilia = now_utc - timedelta(hours=3)
        timestamp_str = now_brasilia.strftime('%d/%m/%Y às %H:%M')
        timestamp_data = {"last_update": f"{timestamp_str} (BRT)"}
        with open(timestamp_output_path, 'w', encoding='utf-8') as f:
            json.dump(timestamp_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Horário da atualização salvo!")
    finally:
        driver.quit()
        print("✅ Robô finalizado.")

if __name__ == "__main__":
    main()