import json
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# TEAM_MAP COMPLETO E VERIFICADO
TEAM_MAP = {
    "Flamengo": {"sigla": "FLA", "logo": "/logos/flamengo.svg", "estadio": "Maracanã"},"Cruzeiro": {"sigla": "CRU", "logo": "/logos/cruzeiro.svg", "estadio": "Mineirão"},"Red Bull Bragantino": {"sigla": "BGT", "logo": "/logos/rb_bragantino.svg", "estadio": "Nabi Abi Chedid"},"Palmeiras": {"sigla": "PAL", "logo": "/logos/palmeiras.svg", "estadio": "Allianz Parque"},"Bahia": {"sigla": "BAH", "logo": "/logos/bahia.svg", "estadio": "Arena Fonte Nova"},"Fluminense": {"sigla": "FLU", "logo": "/logos/fluminense.svg", "estadio": "Maracanã"},"Atlético Mineiro": {"sigla": "CAM", "logo": "/logos/atletico_mg.svg", "estadio": "Arena MRV"},"Botafogo": {"sigla": "BOT", "logo": "/logos/botafogo.svg", "estadio": "Nilton Santos"},"Corinthians": {"sigla": "COR", "logo": "/logos/corinthians.svg", "estadio": "Neo Química Arena"},"Grêmio": {"sigla": "GRE", "logo": "/logos/gremio.svg", "estadio": "Arena do Grêmio"},"Vasco da Gama": {"sigla": "VAS", "logo": "/logos/vasco.svg", "estadio": "São Januário"},"São Paulo": {"sigla": "SAO", "logo": "/logos/sao_paulo.svg", "estadio": "Morumbi"},"Santos": {"sigla": "SAN", "logo": "/logos/santos.svg", "estadio": "Vila Belmiro"},"Vitória": {"sigla": "VIT", "logo": "/logos/vitoria.svg", "estadio": "Barradão"},"Internacional": {"sigla": "INT", "logo": "/logos/internacional.svg", "estadio": "Beira-Rio"},"Fortaleza": {"sigla": "FOR", "logo": "/logos/fortaleza.svg", "estadio": "Castelão"},"Juventude": {"sigla": "JUV", "logo": "/logos/juventude.svg", "estadio": "Alfredo Jaconi"},"Criciúma": {"sigla": "CRI", "logo": "/logos/criciuma.svg", "estadio": "Heriberto Hülse"},"Atlético Goianiense": {"sigla": "ATL-GO", "logo": "/logos/atletico_go.svg", "estadio": "Antônio Accioly"},"Cuiabá": {"sigla": "CUI", "logo": "/logos/cuiaba.svg", "estadio": "Arena Pantanal"},"Athletico": {"sigla": "CAP", "logo": "/logos/atletico_pr.svg", "estadio": "Ligga Arena"},"Goiás": {"sigla": "GOI", "logo": "/logos/goias.svg", "estadio": "Serrinha"},"Novorizontino": {"sigla": "NOV", "logo": "/logos/novorizontino.svg", "estadio": "Dr. Jorge Ismael de Biasi"},"Coritiba": {"sigla": "CFC", "logo": "/logos/coritiba.svg", "estadio": "Couto Pereira"},"CRB": {"sigla": "CRB", "logo": "/logos/crb.svg", "estadio": "Estádio Rei Pelé"},"Avaí": {"sigla": "AVA", "logo": "/logos/avai.svg", "estadio": "Estádio da Ressacada"},"Remo": {"sigla": "REM", "logo": "/logos/remo.svg", "estadio": "Baenão"},"Chapecoense": {"sigla": "CHA", "logo": "/logos/chapecoense.svg", "estadio": "Arena Condá"},"América Mineiro": {"sigla": "AMG", "logo": "/logos/america_mg.svg", "estadio": "Independência"},"Vila Nova FC": {"sigla": "VIL", "logo": "/logos/vila_nova.svg", "estadio": "Onésio Brasileiro Alvarenga"},"Operário-PR": {"sigla": "OPE", "logo": "/logos/operario_pr.svg", "estadio": "Germano Krüger"},"Botafogo-SP": {"sigla": "BOT-SP", "logo": "/logos/botafogo_sp.svg", "estadio": "Santa Cruz"},"Amazonas FC": {"sigla": "AMA", "logo": "/logos/amazonas.svg", "estadio": "Arena da Amazônia"},"Volta Redonda": {"sigla": "VOL", "logo": "/logos/volta_redonda.svg", "estadio": "Raulino de Oliveira"},"Paysandu SC": {"sigla": "PAY", "logo": "/logos/paysandu_sc.svg", "estadio": "Curuzu"},"Athletic Club": {"sigla": "ATH", "logo": "/logos/athletic_club_mg.svg", "estadio": "Arena Unimed"},"Mirassol": {"sigla": "MIR", "logo": "/logos/mirassol.svg", "estadio": "José Maria de Campos Maia"},"Ceará": {"sigla": "CEA", "logo": "/logos/ceara.svg", "estadio": "Castelão"},"Sport Recife": {"sigla": "SPO", "logo": "/logos/sport.svg", "estadio": "Ilha do Retiro"},"Ferroviária": {"sigla": "FER", "logo": "/logos/ferroviaria.svg", "estadio": "Arena da Fonte Luminosa"},
}

# Configuração do Selenium
options = Options()
options.add_argument('--headless'); options.add_argument('--no-sandbox'); options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
service = ChromeService(ChromeDriverManager().install()); driver = webdriver.Chrome(service=service, options=options)

# Caminhos dos arquivos
script_dir = os.path.dirname(__file__); project_root = os.path.dirname(script_dir)
tabela_a_output_path = os.path.join(project_root, 'src', 'data', 'tabela-serie-a.json')
tabela_b_output_path = os.path.join(project_root, 'src', 'data', 'tabela-serie-b.json')

def update_standings(league_name, league_id, season_id, output_path):
    print(f"📈 Atualizando tabela da {league_name}...")
    # Usamos a URL que você confirmou que funciona: /standings/total
    URL_API = f"https://api.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/standings/total"
    try:
        # O Selenium já tem os cookies da visita anterior
        driver.get(URL_API)
        time.sleep(1) # Pausa curta
        
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
                # Usamos os nomes de campo que você encontrou: scoresFor e scoresAgainst
                gols_pro = row.get('scoresFor', 0)
                gols_contra = row.get('scoresAgainst', 0)
                saldo_gols = gols_pro - gols_contra
                
                equipe = { "pos": row.get('position', 0), "time": time_api, "slug": time_api.lower().replace(' ', '-').replace('é', 'e').replace('ã', 'a').replace('ê', 'e'), "logo": TEAM_MAP[time_api]['logo'], "pts": row.get('points', 0), "v": row.get('wins', 0), "e": row.get('draws', 0), "d": row.get('losses', 0), "gp": gols_pro, "gc": gols_contra, "sg": saldo_gols }
                tabela_formatada.append(equipe)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tabela_formatada, f, ensure_ascii=False, indent=4)
        print(f"✅ Tabela da {league_name} salva com {len(tabela_formatada)} equipes.")

    except Exception as e:
        print(f"❌ Erro ao atualizar a tabela da {league_name}: {e}")

def main():
    print("🤖 Iniciando o robô v18 (Cookie Hunter Mode)...")
    try:
        # PASSO 1: Visitar a página principal para obter cookies de sessão.
        print("➡️  Navegando para www.sofascore.com para obter cookies...")
        driver.get("https://www.sofascore.com")
        time.sleep(3) # Esperamos 3 segundos para que tudo carregue
        print("✅ Cookies obtidos.")

        # PASSO 2: Agora, com os cookies, pedimos os dados das tabelas.
        # Usando os IDs que você confirmou que funcionam.
        update_standings("Série A", 325, 72034, tabela_a_output_path)
        print("-" * 30)
        update_standings("Série B", 390, 72603, tabela_b_output_path)

    finally:
        driver.quit()
        print("✅ Robô finalizado.")

if __name__ == "__main__":
    main()