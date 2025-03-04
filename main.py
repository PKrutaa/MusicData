from youtuber_catcher import buscar_videos_youtube
from tracks import take_tracks, create_dataset
from downloader import download
import pandas as pd
from stems import separate_guitar, download_stem
import os

def main():
    playlist_id = "61J5C8CDCqTnK7Zxu72eDG"
    infos,tracks = take_tracks(playlist_id)
    df = create_dataset(playlist_id)
    video_url = buscar_videos_youtube(tracks)
    download(video_url)
    # Create a new column for stem paths
    df['stem_path'] = None
    
    # Ensure audios directory exists
    if os.path.exists('audios'):
        # Process all audio files in the directory
        for filename in os.listdir('audios'):
            if filename.endswith('.mp3'):
                # Extract the song name without extension
                song_name = os.path.splitext(filename)[0]
                
                # Find the corresponding row in the dataframe
                idx = df[df['nome'] == song_name].index
                
                if len(idx) > 0:
                    # Process the audio file
                    url, name = separate_guitar(f'audios/{filename}')
                    stem_path = download_stem(url, name)
                    
                    # Update the dataframe with stem path
                    df.loc[idx, 'stem_path'] = stem_path
    
    # Save the updated dataframe
    df.to_csv('tracks_with_stems.csv', index=False)




if __name__ == "__main__":
    main()