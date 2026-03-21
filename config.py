import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configuração de Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/automacao.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mrosc_automator")

class Config:
    # --- Configurações da IA ---
    @classmethod
    def get_api_key(cls):
        load_dotenv(override=True)
        return os.getenv("GEMINI_API_KEY")

    MODEL_ID = "gemini-3.1-flash-lite-preview" 

    # --- Configurações de Execução ---
    MAX_THREADS = 3 # Reservado para uso futuro
    TIMEOUT = 30 # Segundos de espera em requisições
    
    # --- Configurações de Processamento ---
    BLACKLIST = ['edital', 'chamamento', 'esporte', 'futebol', 'concurso', 'vaga', 'noticia']

