from youtuber_catcher import buscar_videos_youtube
from tracks import take_tracks, create_dataset
from downloader import download
import pandas as pd

def main():
    infos,tracks = take_tracks("61J5C8CDCqTnK7Zxu72eDG")
    df = create_dataset(infos)
    video_url = buscar_videos_youtube(tracks)
    download(video_url)



if __name__ == "__main__":
    main()