from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib.parse

def buscar_videos_youtube(nomes_videos: list) -> list:
    """
    Busca múltiplos vídeos no YouTube e retorna uma lista com os links dos primeiros resultados.
    
    Args:
        nomes_videos (list): Lista com nomes dos vídeos a serem buscados
    
    Returns:
        list: Lista de URLs dos primeiros vídeos encontrados para cada nome
    """    
    # Configurar opções do Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Inicializar o driver com as opções configuradas
    driver = webdriver.Chrome(options=chrome_options)
    
    resultados = []
    
    try:
        # Aceitar cookies apenas uma vez no início
        driver.get("https://www.youtube.com/")
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Accept')]"))
            ).click()
        except:
            pass  # Ignorar se não aparecer
            
        # Processar cada nome de vídeo
        for nome_video in nomes_videos:
            try:
                # Abrir o YouTube
                driver.get("https://www.youtube.com/")
                
                # Encontrar a caixa de pesquisa
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "search_query"))
                )
                
                # Inserir o termo de pesquisa e pressionar Enter
                search_box.clear()
                search_box.send_keys(nome_video)
                search_box.send_keys(Keys.RETURN)
                
                # Esperar pelos resultados da pesquisa
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "contents"))
                )
                
                # Pequena pausa para garantir que os resultados carreguem
                time.sleep(2)
                
                # Encontrar o primeiro vídeo (não playlist, não shorts)
                primeiro_video = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a#video-title"))
                )
                
                # Obter o link do vídeo
                video_url = primeiro_video.get_attribute("href")
                resultados.append(video_url)
                
            except Exception as e:
                print(f"Erro ao buscar vídeo '{nome_video}': {e}")
                resultados.append(None)  # Adicionar None para manter a mesma ordem da lista original
                
    finally:
        # Fechar o navegador
        driver.quit()
        
    return resultados

# Exemplo de uso
if __name__ == "__main__":
    # Solicitar entrada de nomes de vídeos separados por vírgula
    entrada = input("Digite os nomes dos vídeos que deseja buscar (separados por vírgula): ")
    nomes_dos_videos = [nome.strip() for nome in entrada.split(',')]
    
    links = buscar_videos_youtube(nomes_dos_videos)
    
    # Exibir os resultados
    for i, (nome, link) in enumerate(zip(nomes_dos_videos, links)):
        if link:
            print(f"{i+1}. '{nome}': {link}")
        else:
            print(f"{i+1}. '{nome}': Não foi possível encontrar o vídeo.")