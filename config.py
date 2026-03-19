import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- Configurações da IA ---
    API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_ID = "gemini-3.1-flash-lite-preview" 

    # --- Configurações de Execução ---
    MAX_THREADS = 3 # Reservado para uso futuro
    TIMEOUT = 30 # Segundos de espera em requisições
    
    # --- Configurações de Processamento ---
    BLACKLIST = ['edital', 'chamamento', 'esporte', 'futebol', 'concurso', 'vaga', 'noticia']
    PDF_PAGES_TO_EXTRACT = 5
    OCR_PAGES_TO_EXTRACT = 3
    MAX_HTML_CHARS = 15000
    DOWNLOAD_CHUNK_SIZE = 8192
