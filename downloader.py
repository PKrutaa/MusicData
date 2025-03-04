import yt_dlp
import os

def download(urls: list, output_dir: str = "audios"):
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
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            ydl.download([url])