from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib.parse
import concurrent.futures
from typing import List, Optional, Tuple

def buscar_unico_video(termo_busca: str) -> Optional[str]:
    """
    Busca um único vídeo no YouTube usando Selenium.
    
    Args:
        termo_busca: Termo de busca para o vídeo (formato: 'nome_musica - nome_album')
        
    Returns:
        URL do vídeo encontrado ou None se não encontrado
    """
    # Configurar opções do Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--headless")  # Executar em modo headless para maior eficiência
    
    # Inicializar o driver com as opções configuradas
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Abrir o YouTube
        driver.get("https://www.youtube.com/")
        
        # Tentar aceitar cookies
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Accept')]"))
            ).click()
        except:
            pass  # Ignorar se não aparecer
        
        # Encontrar a caixa de pesquisa
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        
        # Inserir o termo de pesquisa e pressionar Enter
        search_box.clear()
        search_box.send_keys(termo_busca)
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
        print(f"Encontrado vídeo para '{termo_busca}': {video_url}")
        return video_url
        
    except Exception as e:
        print(f"Erro ao buscar vídeo '{termo_busca}': {e}")
        return None
        
    finally:
        # Fechar o navegador
        driver.quit()

def youtube_catcher(musicas_info: List[Tuple[str, str]], max_workers: int = 3) -> List[Optional[str]]:
    """
    Busca múltiplos vídeos no YouTube em paralelo usando Selenium.
    
    Args:
        musicas_info: Lista de tuplas contendo (nome_da_musica, nome_do_artista)
        max_workers: Número máximo de workers para paralelização
    
    Returns:
        Lista de URLs dos vídeos encontrados para cada música
    """
    resultados = [None] * len(musicas_info)  # Inicializar lista com None
    
    # Formatar os termos de busca como "nome_musica - nome_artista"
    termos_busca = [f"{nome_musica} - {nome_artista}" for nome_musica, nome_artista in musicas_info]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Mapear a função de busca para cada termo formatado
        futuros = {executor.submit(buscar_unico_video, termo): i for i, termo in enumerate(termos_busca)}
        
        # Coletar os resultados na medida em que forem concluídos
        for futuro in concurrent.futures.as_completed(futuros):
            indice = futuros[futuro]
            try:
                resultado = futuro.result()
                resultados[indice] = resultado
                nome_musica, nome_artista = musicas_info[indice]
                print(f"Concluída busca {indice+1}/{len(musicas_info)}: '{nome_musica} - {nome_artista}'")
            except Exception as e:
                print(f"Erro na busca {indice+1}: {e}")
                resultados[indice] = None
    
    return resultados

# Exemplo de uso
if __name__ == "__main__":
    # Solicitar entrada de nomes de vídeos separados por vírgula
    entrada = input("Digite os nomes das músicas e artistas (formato: 'música,artista;música2,artista2'): ")
    pares = entrada.split(';')
    musicas_info = []
    
    for par in pares:
        if ',' in par:
            musica, artista = par.split(',', 1)
            musicas_info.append((musica.strip(), artista.strip()))
    
    if musicas_info:
        links = youtube_catcher(musicas_info)
        
        # Exibir os resultados
        for i, ((musica, artista), link) in enumerate(zip(musicas_info, links)):
            termo = f"{musica} - {artista}"
            if link:
                print(f"{i+1}. '{termo}': {link}")
            else:
                print(f"{i+1}. '{termo}': Não foi possível encontrar o vídeo.")
    else:
        print("Nenhuma música e artista válidos foram fornecidos. Use o formato: 'música,artista;música2,artista2'")