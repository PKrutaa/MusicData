import yt_dlp
import os
import concurrent.futures
from typing import List, Optional

def download_single(url: str, ydl_opts: dict) -> bool:
    """
    Baixa um único vídeo do YouTube.
    
    Args:
        url: URL do vídeo
        ydl_opts: Opções para o yt-dlp
        
    Returns:
        True se o download foi bem-sucedido, False caso contrário
    """
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return False

def download(urls: List[str], output_dir: str = "audios", max_workers: int = 2) -> List[bool]:
    """
    Baixa múltiplos vídeos do YouTube em paralelo.
    
    Args:
        urls: Lista de URLs dos vídeos
        output_dir: Diretório para salvar os arquivos baixados
        max_workers: Número máximo de downloads simultâneos
        
    Returns:
        Lista de resultados (True para sucesso, False para falha)
    """
    # Cria o diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Define o caminho completo para o arquivo de saída
    output_path = os.path.join(output_dir, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,  # Caminho completo incluindo a pasta
        'quiet': True,  # Reduzir saída no console
        'no_warnings': True,  # Não mostrar avisos
    }
    
    resultados = []
    
    # Limitamos o número de workers para não sobrecarregar a conexão
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submeter todos os downloads
        futures = [executor.submit(download_single, url, ydl_opts) for url in urls]
        
        # Coletar os resultados e mostrar progresso
        total = len(futures)
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            resultados.append(result)
            print(f"Download {i}/{total} concluído")
    
    return resultados