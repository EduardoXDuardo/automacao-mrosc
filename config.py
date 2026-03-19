import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_ID = "gemini-3.1-flash-lite-preview" 
    BLACKLIST = ['edital', 'chamamento', 'esporte', 'futebol', 'concurso', 'vaga', 'noticia']
    
    # --- Configurações de Processamento ---
    PDF_PAGES_TO_EXTRACT = 5
    OCR_PAGES_TO_EXTRACT = 3
    MAX_HTML_CHARS = 15000
    DOWNLOAD_TIMEOUT = 30
    DOWNLOAD_CHUNK_SIZE = 8192
