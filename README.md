# MusicData - Pedro Henrique Kruta, Igor de Melo, Erick Batista, João Vitor Costa

## Sobre o Projeto

O projeto **MusicData** visa a coleta, análise e processamento de dados relacionados à música. A coleta de dados é feita por meio de APIs como Spotify e Music.ai, além de técnicas de web scraping para extrair informações do YouTube.

O sistema realiza a extração, download e análise de características musicais (BPM, tonalidade) a partir de playlists do Spotify.

## Tecnologias Utilizadas

- **APIs**:
  - [Spotify Web API](https://developer.spotify.com/documentation/web-api/) - Para metadados de músicas, artistas e playlists
  - [Music.ai API](https://www.music.ai/docs) - Para análise de áudio e extração de características musicais

- **Web Scraping**:
  - Selenium - Para coleta de dados do YouTube
  - yt-dlp - Para download de áudios

- **Ferramentas**:
  - Python - Linguagem principal de desenvolvimento
  - Pandas - Para estruturação e manipulação de dados

## Componentes Principais

- **tracks.py** - Extrai informações de músicas do Spotify usando a API oficial
- **youtuber_catcher.py** - Busca músicas no YouTube usando nome da música e artista
- **downloader.py** - Baixa vídeos como arquivos MP3 usando yt_dlp
- **stems.py** - Processa áudio para extrair BPM, tonalidade e simular separação de instrumentos
- **update_dataset_from_debug.py** - Atualiza o dataset usando dados JSON armazenados
- **main.py** - Orquestra todo o processo end-to-end

## Dataset Final

O dataset gerado (`tracks_with_stems.csv`) contém:

| Campo | Descrição |
|-------|-----------|
| **nome** | Nome da música |
| **artistas** | Artistas que contribuíram na faixa |
| **album** | Nome do álbum |
| **release_date** | Data de lançamento |
| **BPM** | Batidas por minuto (tempo da música) |
| **Root_key** | Tonalidade/escala principal da música |
| **stem_path** | Caminho para o arquivo de instrumento isolado |
| **url**| Spotify link |
| **popularidade**| Popularidade extraida pelo Spotify |

## Fluxo de Trabalho

1. Extração de dados da playlist do Spotify
2. Busca das músicas no YouTube (nome + artista)
3. Download dos arquivos MP3
4. Processamento para extrair BPM e tonalidade
5. Atualização do dataset e limpeza de arquivos temporários

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

# Ou sincronizar pelo pyproject.toml (recomendado)
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
