#!/usr/bin/env python3
"""
Script para atualizar o dataset com informações dos JSONs de debug.
Usa os arquivos em /debug para atualizar o dataset sem executar todo o pipeline.
"""

import os
import json
import pandas as pd
import re
from typing import Dict, List, Optional, Tuple

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza o nome do arquivo removendo caracteres inválidos.
    """
    # Remover caracteres não permitidos em nomes de arquivos
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Substituir espaços por underscores
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def load_debug_files(debug_dir: str = 'debug') -> List[Dict]:
    """
    Carrega todos os arquivos JSON da pasta de debug.
    
    Args:
        debug_dir: Diretório dos arquivos de debug
        
    Returns:
        Lista de dicionários com dados de cada arquivo
    """
    results = []
    
    if not os.path.exists(debug_dir):
        print(f"Diretório {debug_dir} não encontrado.")
        return results
    
    json_files = [f for f in os.listdir(debug_dir) if f.endswith('.json')]
    print(f"Encontrados {len(json_files)} arquivos JSON em {debug_dir}.")
    
    for filename in json_files:
        try:
            with open(os.path.join(debug_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
                print(f"Carregado: {filename}")
        except Exception as e:
            print(f"Erro ao carregar {filename}: {e}")
    
    return results

def find_matching_records(df: pd.DataFrame, track_name: str) -> List[int]:
    """
    Encontra registros no DataFrame que correspondem ao nome da faixa.
    
    Args:
        df: DataFrame com o dataset
        track_name: Nome da faixa a buscar
        
    Returns:
        Lista de índices dos registros correspondentes
    """
    # Método 1: Usando contains case-insensitive
    idx1 = df[df['nome'].str.contains(track_name, case=False, na=False)].index.tolist()
    
    # Método 2: Usando similiaridade de strings (se o nome contém ou é contido)
    idx2 = []
    for i, row in df.iterrows():
        db_track_name = str(row['nome']).lower()
        search_name = track_name.lower()
        if search_name in db_track_name or db_track_name in search_name:
            idx2.append(i)
    
    # Combinando os dois métodos
    idx = list(set(idx1 + idx2))
    
    return idx

def update_dataset():
    """
    Função principal para atualizar o dataset com dados dos JSONs de debug.
    """
    # Carregar o dataset
    try:
        df = pd.read_csv('tracks_with_stems.csv', sep=';')
        print(f"Dataset carregado com {len(df)} registros.")
    except FileNotFoundError:
        print("Arquivo de dataset não encontrado.")
        return
    except Exception as e:
        print(f"Erro ao carregar o dataset: {e}")
        return
    
    # Carregar os arquivos de debug
    debug_data = load_debug_files()
    if not debug_data:
        print("Nenhum dado de debug encontrado. Nada a atualizar.")
        return
    
    # Atualizar o dataset
    update_count = 0
    for data in debug_data:
        try:
            # Usar o nome original (não sanitizado) para buscar correspondências
            name = data.get('name', '')
            if not name:
                continue
                
            result = data.get('result', {})
            bpm = result.get('bpm')
            root_key = result.get('root_key')
            url = result.get('url')
            
            if not (bpm or root_key):
                print(f"Dados incompletos para {name}. Pulando.")
                continue
            
            # Determinar o stem_path
            stem_path = None
            if url:
                # Usar o nome sanitizado para paths de arquivo
                sanitized_name = data.get('sanitized_name', sanitize_filename(name))
                
                if 'guitar_stems' not in os.listdir():
                    os.makedirs('guitar_stems')
                
                if url.startswith('https://example.com'):
                    # URL simulada
                    stem_path = f"guitar_stems/{sanitized_name}.wav"
                else:
                    # URL real
                    stem_filename = f"{sanitized_name}.wav"
                    stem_path = f"guitar_stems/{stem_filename}"
                    
                # Verificar se o arquivo existe
                if not os.path.exists(stem_path):
                    print(f"Aviso: arquivo stem {stem_path} não existe.")
            
            # Encontrar registros correspondentes usando o nome original
            matches = find_matching_records(df, name)
            
            if matches:
                print(f"Encontrada correspondência para '{name}'. Atualizando {len(matches)} registros.")
                
                # Atualizar cada registro
                for idx in matches:
                    df.at[idx, 'stem_path'] = stem_path
                    df.at[idx, 'BPM'] = bpm
                    df.at[idx, 'Root_key'] = root_key
                    update_count += 1
            else:
                print(f"⚠ Nenhuma correspondência encontrada para '{name}'")
                # Mostrar alguns exemplos do dataset
                sample = df['nome'].sample(min(3, len(df))).tolist()
                print(f"  Exemplos do dataset: {sample}")
                print(f"  Valores não adicionados: BPM={bpm}, Tonalidade={root_key}")
        
        except Exception as e:
            print(f"Erro ao processar dados de debug: {e}")
    
    # Verificar se os dados foram atualizados
    bpm_count = df['BPM'].notnull().sum()
    key_count = df['Root_key'].notnull().sum()
    stem_count = df['stem_path'].notnull().sum()
    
    print(f"\nAtualizados {update_count} registros no dataset.")
    print(f"Contagem final: BPM={bpm_count}, Root_key={key_count}, stem_path={stem_count}")
    
    # Mostrar amostra do dataset atualizado
    print("\nAmostra do dataset atualizado:")
    sample_size = min(5, len(df))
    if sample_size > 0:
        sample = df.sample(sample_size)
        for _, row in sample.iterrows():
            print(f"Nome: {row['nome']}, BPM: {row['BPM']}, Tonalidade: {row['Root_key']}")
    
    # Salvar apenas o dataset final
    try:
        df.to_csv('tracks_with_stems.csv', index=False, sep=';')
        print("\nDataset atualizado e salvo com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar o dataset: {e}")

if __name__ == "__main__":
    update_dataset() 