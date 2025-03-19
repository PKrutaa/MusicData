# MusicData - Extrator e Processador de Músicas

Sistema para extração, download e análise de características musicais a partir de playlists do Spotify.

## Componentes Principais

- **tracks.py**: Extrai informações de músicas do Spotify usando a API oficial, retornando nome, artista e metadados.
- **youtuber_catcher.py**: Busca músicas no YouTube usando nomes de faixas e artistas extraídos do Spotify.
- **downloader.py**: Baixa os vídeos encontrados como arquivos MP3 usando yt_dlp.
- **stems.py**: Processa os arquivos de áudio para extrair BPM, tonalidade e simular separação de instrumentos.
- **update_dataset_from_debug.py**: Atualiza o dataset usando dados JSON armazenados durante o processamento.
- **main.py**: Orquestra todo o processo, desde extração do Spotify até processamento e atualização do dataset.

## Dataset

O dataset final (`tracks_with_stems.csv`) contém:

- **nome**: Nome da música
- **artistas**: Artistas que contribuíram na faixa
- **album**: Nome do álbum
- **release_date**: Data de lançamento
- **BPM**: Batidas por minuto (tempo da música)
- **Root_key**: Tonalidade/escala principal da música
- **stem_path**: Caminho para o arquivo de instrumento isolado
- Outros metadados como duração, popularidade, etc.

## Fluxo de Trabalho

1. Extração de informações de músicas da playlist do Spotify
2. Busca das músicas no YouTube usando nome da música + nome do artista
3. Download dos arquivos MP3
4. Processamento dos arquivos para extrair BPM e tonalidade
5. Atualização do dataset com as informações obtidas
6. Limpeza de arquivos temporários

## Como Executar

### Usando pip

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o pipeline completo
python main.py
```

### Usando UV (Recomendado)

UV é um gerenciador de pacotes Python mais rápido e eficiente que substitui pip e venv.

```bash
# Instalar UV (caso ainda não tenha)
curl -sSf https://install.theta.co/install.sh | sh

# Criar ambiente virtual e instalar dependências
uv venv
uv pip install -r requirements.txt

# Alternativamente, sincronizar o ambiente com os requisitos exatos
uv pip sync requirements.txt

# Alternativamente a alternativa, você pode sincronizar pelo pyproject.toml (recomendado)
uv sync

# Ativar o ambiente virtual
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows

# Executar o pipeline
uv run python main.py
# ou simplesmente após ativar o ambiente
python main.py
```

O ID da playlist padrão é '6MsGYGvosXuhO5wK93aqkX', mas pode ser modificado no código.

# MusicData - Pedro Henrique Kruta, Igor de Melo, Erick Batista, João Vitor Costa

**Descrição:**

O projeto **MusicData** visa a coleta, análise e processamento de dados relacionados à música. A coleta de dados será feita por meio de APIs de serviços como [Music.ai](https://www.music.ai) e [Spotify](https://developer.spotify.com), além de utilizar técnicas de web scraping para extrair informações de sites de áudio e vídeo como [YouTube](https://www.youtube.com).

**Objetivos do Projeto:**

- **Coleta de Dados**: Utilizar APIs para coletar informações sobre músicas, artistas e playlists.
    - [Spotify API](https://developer.spotify.com/documentation/web-api/)
    - [Music.ai API](https://www.music.ai/docs)
  
- **Web Scraping**: Implementar scraping para coletar dados de plataformas de vídeo e áudio.
    - Utilizar [Scrapy](https://scrapy.org) para extrair informações de sites como YouTube.

**Tecnologias Utilizadas:**

- **APIs**:
    - [Spotify Web API](https://developer.spotify.com/documentation/web-api/) - Para dados sobre músicas, artistas, álbuns e playlists.
    - [Music.ai](https://www.music.ai) - Para dados relacionados a áudio e análise de música.

- **Scrapy**:
    - [Scrapy Framework](https://scrapy.org) - Para a coleta de dados via scraping em plataformas de vídeo e áudio como o YouTube.

- **Linguagens**:
    - Python (para a implementação de scripts de coleta e processamento de dados)

**Como Usar:**

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/MusicData.git
