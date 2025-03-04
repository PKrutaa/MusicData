from musicai_sdk import MusicAiClient
import os 
import dotenv
import requests

dotenv.load_dotenv()

def separate_guitar(file_path: str) -> str:
    name = file_path.split('/')[-1]
    if '.mp3' in name:
        name.replace('.mp3','')
    key = os.getenv('API_MUSIC_AI')

    client = MusicAiClient(api_key=key)

    # Get application info
    app_info = client.get_application_info()
    print('Application Info:', app_info)

    # Upload local file
    file_url = client.upload_file(file_path= file_path)
    print('File Url:', file_url)

    # Create Job
    workflow_params = {
        'inputUrl': file_url,
    }

    create_job_info = client.create_job(job_name='Stem guitar  - demo.ogg', workflow_id='untitled-workflow-12ca460',params=workflow_params)
    job_id = create_job_info['id']

    # Wait for job to complete
    job_info = client.wait_for_job_completion(job_id)

    # Get job info
    job_info = client.get_job(job_id=job_id)


    return job_info['result']['Output 1'], name

def download_stem(url: str,music_name: str ,output_dir: str = "stem - guitarra") -> str:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract the base filename without query parameters
    #filename = os.path.basename(url.split('?')[0])
    output_path = os.path.join(output_dir, music_name)

    response = requests.get(url, stream=True)
    response.raise_for_status()  # Check if the request was successful

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return output_path

if __name__ == "__main__":
    url,name = separate_guitar(r'/root/projeto-dados/icd/MusicData/audios/Vundabar - ＂Alien Blues＂ (Official Video).mp3')
    audio_path = download_stem(url,name)