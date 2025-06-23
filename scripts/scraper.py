import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- DICIONÁRIO "TRADUTOR" DE EQUIPES v2.0 ---
# Agora com as rotas de logo CORRETAS e os ESTÁDIOS de cada time.
TEAM_MAP = {
    "Avaí": {"sigla": "AVA", "logo": "/logos/avai.svg", "estadio": "Estádio da Ressacada"},
    "Athletico": {"sigla": "CAP", "logo": "/logos/atletico_pr.svg", "estadio": "Ligga Arena"},
    "Remo": {"sigla": "REM", "logo": "/logos/remo.svg", "estadio": "Baenão"},
    "Paysandu SC": {"sigla": "PAY", "logo": "/logos/paysandu_sc.svg", "estadio": "Curuzu"},
    "Ferroviária": {"sigla": "FER", "logo": "/logos/ferroviaria.svg", "estadio": "Arena da Fonte Luminosa"},
    "CRB": {"sigla": "CRB", "logo": "/logos/crb.svg", "estadio": "Estádio Rei Pelé"},
    "Atlético Goianiense": {"sigla": "ATL-GO", "logo": "/logos/atletico_go.svg", "estadio": "Antônio Accioly"},
    "Volta Redonda": {"sigla": "VOL", "logo": "/logos/volta_redonda.svg", "estadio": "Raulino de Oliveira"},
    "Coritiba": {"sigla": "COR", "logo": "/logos/coritiba.svg", "estadio": "Couto Pereira"},
    "Cuiabá": {"sigla": "CUI", "logo": "/logos/cuiaba.svg", "estadio": "Arena Pantanal"},
    "Amazonas FC": {"sigla": "AMA", "logo": "/logos/amazonas.svg", "estadio": "Arena da Amazônia"},
    "Vila Nova FC": {"sigla": "VIL", "logo": "/logos/vila_nova.svg", "estadio": "Onésio Brasileiro Alvarenga"},
    # Adicione aqui outros times que precisar
}


# --- O resto do scraper continua igual ---
hoje = datetime.now().strftime("%Y-%m-%d")
URL_API = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{hoje}"
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print("🤖 Iniciando o robô v7 (Final Data Mode)...")

script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)
output_path = os.path.join(project_root, 'src', 'data', 'partidos.json')

try:
    driver.get(URL_API)
    print("✅ API acessada com sucesso!")
    
    json_text = driver.find_element(By.TAG_NAME, "pre").text
    dados = json.loads(json_text)
    jogos_do_dia = dados.get('events', [])
    
    nossos_partidos = []
    id_partido_counter = 1

    for jogo in jogos_do_dia:
        campeonato = jogo.get('tournament', {}).get('name', 'N/A')

        if 'Brasileirão Série A' in campeonato or 'Brasileirão Série B' in campeonato:
            time_casa_api = jogo.get('homeTeam', {}).get('name', 'N/A')
            time_fora_api = jogo.get('awayTeam', {}).get('name', 'N/A')

            if time_casa_api in TEAM_MAP and time_fora_api in TEAM_MAP:
                placar_casa = jogo.get('homeScore', {}).get('current', None)
                placar_fora = jogo.get('awayScore', {}).get('current', None)
                status = jogo.get('status', {}).get('description', 'Agendado')
                
                if status == 'Not started':
                    timestamp = jogo.get('startTimestamp', 0)
                    info = datetime.fromtimestamp(timestamp).strftime('%d/%m - %H:%M')
                else:
                    info = status.capitalize()

                partido_formatado = {
                    "id": id_partido_counter,
                    "campeonato": campeonato,
                    # --- MUDANÇA PRINCIPAL AQUI ---
                    # Pegamos o estádio do time da casa do nosso mapa
                    "estadio": TEAM_MAP[time_casa_api].get('estadio', 'Estádio não informado'),
                    "timeCasa": TEAM_MAP[time_casa_api],
                    "timeFora": TEAM_MAP[time_fora_api],
                    "placarCasa": placar_casa,
                    "placarFora": placar_fora,
                    "info": info
                }
                nossos_partidos.append(partido_formatado)
                id_partido_counter += 1

    if nossos_partidos:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(nossos_partidos, f, ensure_ascii=False, indent=4)
        print(f"✅ Sucesso! {len(nossos_partidos)} jogos foram salvos em partidos.json.")
    else:
        print("🟡 Nenhum jogo das ligas brasileiras encontrado para salvar hoje.")

except Exception as e:
    print(f"❌ Ocorreu um erro inesperado: {e}")

finally:
    driver.quit()
    print("✅ Robô finalizado.")