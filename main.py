import pandas as pd
import os
from tracks import take_tracks
from youtuber_catcher import youtube_catcher
from downloader import download
from stems import separate_guitar, download_stem, process_audio_files, download_stems_parallel
import time
import concurrent.futures
import re
from typing import List, Tuple, Optional
from update_dataset_from_debug import update_dataset

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza o nome do arquivo removendo caracteres inválidos.
    """
    # Remover caracteres não permitidos em nomes de arquivos
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Substituir espaços por underscores
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def process_single_audio(audio_path: str) -> Tuple[str, float, str, str, str]:
    """
    Processa um único arquivo de áudio sem usar paralelismo.
    """
    print(f"Processando {audio_path}...")
    audio_url, bpm, root_key, original_name = separate_guitar(audio_path)
    print(f"Processamento concluído: {original_name}, BPM={bpm}, Tonalidade={root_key}")
    
    if audio_url:
        # Sanitizar o nome apenas para o download do stem
        sanitized_name = sanitize_filename(original_name)
        stem_path = download_stem(audio_url, sanitized_name)
        print(f"Stem baixado para: {stem_path}")
    else:
        stem_path = None
        print(f"Sem URL para baixar stem para {original_name}")
        
    return audio_url, bpm, root_key, original_name, stem_path

def main(playlist_id: str) -> None:
    """Main function to execute the entire pipeline."""
    print("Iniciando o processamento...")
    start_time = time.time()
    
    # Obtém informações das faixas e uma lista formatada para busca no YouTube
    print("Obtendo informações das faixas...")
    tracks_info, tracks_names = take_tracks(playlist_id)
    print(f"Total de faixas encontradas: {len(tracks_names)}")
    
    # Busca os vídeos no YouTube usando Selenium em paralelo com 2 workers
    print("Buscando vídeos no YouTube com Selenium (paralelizado)...")
    videos = youtube_catcher(tracks_names, max_workers=2)
    valid_count = len([v for v in videos if v is not None])
    print(f"URLs encontradas: {valid_count}/{len(videos)}")
    
    if valid_count == 0:
        print("Nenhum vídeo válido encontrado para download.")
        return
    
    # Filtra URLs None
    valid_videos = [url for url in videos if url is not None]
    
    if valid_videos:
        # Baixa os vídeos como MP3 usando paralelização (max_workers=2 na função download)
        print(f"Baixando {len(valid_videos)} vídeos...")
        try:
            download_results = download(valid_videos)
            success_count = sum(1 for r in download_results if r)
            print(f"Downloads concluídos: {success_count} de {len(valid_videos)}")
        except Exception as e:
            print(f"Erro durante o download dos vídeos: {e}")
    else:
        print("Nenhum vídeo válido encontrado para download.")
        return

    # Load the dataset with track information
    try:
        df = pd.read_csv('tracks_with_stems.csv', sep=';')
        print(f"Dataset carregado com {len(df)} registros.")
    except FileNotFoundError:
        # Cria um DataFrame a partir das informações das faixas
        df = pd.DataFrame(tracks_info)
        df['stem_path'] = None
        df['BPM'] = None
        df['Root_key'] = None
        print("Novo dataset criado.")
    except Exception as e:
        print(f"Erro ao carregar o dataset: {e}")
        # Cria um novo DataFrame
        df = pd.DataFrame(tracks_info)
        df['stem_path'] = None
        df['BPM'] = None
        df['Root_key'] = None
        print("Erro ao carregar dataset existente. Novo dataset criado.")

    # Ensure audios directory exists
    if not os.path.exists('audios'):
        os.makedirs('audios')

    # Coletar todos os arquivos de áudio para processamento
    audio_files = []
    
    try:
        for filename in os.listdir('audios'):
            if filename.endswith('.mp3'):
                audio_path = os.path.join('audios', filename)
                audio_files.append(audio_path)
        
        print(f"Total de arquivos de áudio encontrados: {len(audio_files)}")
    except Exception as e:
        print(f"Erro ao listar arquivos de áudio: {e}")
    
    if not audio_files:
        print("Nenhum arquivo de áudio encontrado para processar.")
        return
    
    # Processar cada arquivo individualmente para evitar problemas de paralelismo
    update_count = 0
    for audio_path in audio_files:
        try:
            # Processar e baixar stem sem paralelismo
            audio_url, bpm, root_key, original_name, stem_path = process_single_audio(audio_path)
            
            # Atualizar o dataframe diretamente após cada processamento
            if original_name:
                # Método 1: Usando contains case-insensitive
                idx1 = df[df['nome'].str.contains(original_name, case=False, na=False)].index
                
                # Método 2: Usando similiaridade de strings (se o nome contém ou é contido)
                idx2 = []
                for i, row in df.iterrows():
                    track_name = str(row['nome']).lower()
                    proc_name = original_name.lower()
                    if proc_name in track_name or track_name in proc_name:
                        idx2.append(i)
                
                # Combinando os dois métodos
                idx = list(set(idx1.tolist() + idx2))
                
                if len(idx) > 0:
                    print(f"Encontrada correspondência para '{original_name}'. Atualizando {len(idx)} registros.")
                    
                    # Update the dataframe with all extracted information
                    for i in idx:
                        # Atualiza registro por registro explicitamente
                        df.at[i, 'stem_path'] = stem_path  # Usando .at para acesso elemento a elemento
                        df.at[i, 'BPM'] = bpm
                        df.at[i, 'Root_key'] = root_key
                        update_count += 1
                        
                    # Removido salvamento incremental para evitar arquivos intermediários
                else:
                    print(f"⚠ Não foi possível encontrar correspondência para '{original_name}' no dataset")
                    sample = df['nome'].sample(min(5, len(df))).tolist()
                    print(f"Algumas entradas no dataset: {sample}")
        except Exception as e:
            print(f"Erro ao processar {audio_path}: {e}")
    
    print(f"Atualizados {update_count} registros no dataset.")
    
    # Verificar se os dados foram realmente atualizados
    bpm_count = df['BPM'].notnull().sum()
    key_count = df['Root_key'].notnull().sum()
    stem_count = df['stem_path'].notnull().sum()
    print(f"Contagem final no processamento direto: BPM={bpm_count}, Root_key={key_count}, stem_path={stem_count}")
    
    # Imprimir uma amostra do dataset atualizado para verificação
    print("\nAmostra do dataset atualizado no processamento direto:")
    sample_indices = min(5, len(df))
    if sample_indices > 0:
        sample_df = df.sample(sample_indices)
        for _, row in sample_df.iterrows():
            print(f"Nome: {row['nome']}, BPM: {row['BPM']}, Tonalidade: {row['Root_key']}, Stem: {row['stem_path']}")

    # Salvar o dataset após o processamento direto
    try:
        df.to_csv('tracks_with_stems.csv', index=False, sep=';')
        print("Dataset salvo após processamento direto!")
    except Exception as e:
        print(f"Erro ao salvar o dataset após processamento direto: {e}")

    # Calcular tempo parcial de execução
    mid_time = time.time()
    elapsed_time_direct = mid_time - start_time
    print(f"Processamento direto concluído em {elapsed_time_direct:.2f} segundos")
    
    # Chamada para a função update_dataset para garantir que todos os dados dos JSONs de debug são incorporados
    print("\n\n" + "="*80)
    print("INICIANDO ATUALIZAÇÃO A PARTIR DOS ARQUIVOS DE DEBUG")
    print("="*80 + "\n")
    
    # Chama a função de atualização a partir dos JSONs de debug
    try:
        update_dataset()
    except Exception as e:
        print(f"Erro ao executar update_dataset: {e}")
    
    # Calcular e mostrar o tempo total de execução
    end_time = time.time()
    elapsed_time_total = end_time - start_time
    elapsed_time_update = end_time - mid_time
    print(f"Tempo para atualização a partir dos arquivos de debug: {elapsed_time_update:.2f} segundos")
    print(f"Processamento total concluído em {elapsed_time_total:.2f} segundos")
    
    # Limpar arquivos temporários que possam ter sido criados
    try:
        temp_files = ['tracks_with_stems_incremental.csv', 
                     'tracks_with_stems_backup.csv', 
                     'tracks_with_stems_before_update.csv',
                     'tracks_with_stems_updated.csv']
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Arquivo temporário removido: {temp_file}")
                
        print("Todos os arquivos temporários foram removidos.")
    except Exception as e:
        print(f"Erro ao limpar arquivos temporários: {e}")


if __name__ == "__main__":
    main('6MsGYGvosXuhO5wK93aqkX')