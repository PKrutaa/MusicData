import os
import dotenv
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Carregar variáveis de ambiente (API_CLIENT_ID e API_CLIENT_SECRET)
dotenv.load_dotenv()

def take_tracks(playlist_id: str) -> list:
    # Autenticação usando credenciais do Spotify
    client_id = os.getenv('API_CLIENT_ID')
    client_secret = os.getenv('API_CLIENT_SECRET')
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, 
        client_secret=client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    tracks_info = []
    tracks_list = []
    # Obter a primeira página com faixas da playlist
    results = sp.playlist_tracks(playlist_id)
    
    # Loop para coletar todas as páginas (caso haja mais de 100 faixas)
    while results:
        for item in results['items']:
            track = item['track']
            # Evitar casos em que o track pode ser None (por exemplo, se foi removido)
            if track is None:
                continue
                
            # Obtém nome da música e nome do artista principal para a lista de busca
            nome_musica = track.get('name')
            nome_artista = track['artists'][0].get('name') if track.get('artists') else ""
            tracks_list.append((nome_musica, nome_artista))

            # Coletar informações desejadas
            track_data = {
                'id': track.get('id'),
                'nome': track.get('name'),
                'artistas': ', '.join([artist.get('name') for artist in track.get('artists', [])]),
                'album': track['album'].get('name'),
                'release_date': track['album'].get('release_date'),
                'duracao_ms': track.get('duration_ms'),
                'popularity': track.get('popularity'),
                'explicit': track.get('explicit'),
                'url': track['external_urls'].get('spotify')
            }
            tracks_info.append(track_data)

        # Verifica se existe próxima página de resultados
        if results.get('next'):
            results = sp.next(results)
        else:
            break
    print(tracks_list)
    return tracks_info, tracks_list

def create_dataset(playlist_id: str) -> pd.DataFrame:
    # Coleta as informações das faixas
    tracks_info, _ = take_tracks(playlist_id)
    # Cria um DataFrame a partir da lista de dicionários
    df = pd.DataFrame(tracks_info)
    return df

if __name__ == '__main__':
    playlist_id = "412w3Lnu74m4k442qNn2Va"
    df = create_dataset(playlist_id)
    # Exibe as 5 primeiras linhas do dataset
    print(df.head())
    # Salva o dataset em um arquivo CSV
    df.to_csv("spotify_tracks_dataset.csv", index=False)