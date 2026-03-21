import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configuração de Logging
os.makedirs("logs", exist_ok=True)

class ProfessionalFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',      # Azul
        'INFO': '\033[92m',       # Verde
        'WARNING': '\033[93m',    # Amarelo
        'ERROR': '\033[91m',      # Vermelho
        'CRITICAL': '\033[95m'    # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        log_fmt = f"%(asctime)s | %(levelname)-8s | %(message)s"
        
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.RESET)
        
        formatter = logging.Formatter(f"{color}{log_fmt}{self.RESET}", datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

file_handler = logging.FileHandler("logs/automacao.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt='%Y-%m-%d %H:%M:%S'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(ProfessionalFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger("Automacao_MROSC")

class Config:
    # --- Configurações da IA ---
    @classmethod
    def get_api_key(cls):
        load_dotenv(override=True)
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError(
                "GEMINI_API_KEY não configurada. "
                "Crie um arquivo .env com: GEMINI_API_KEY=sua_chave_aqui"
            )
        return key

    MODEL_ID = "gemini-3.1-flash-lite-preview" 

    # --- Configurações de Execução ---
    MAX_THREADS = 3 # Reservado para uso futuro
    TIMEOUT = 30 # Segundos de espera em requisições
    DOWNLOAD_CHUNK_SIZE = 8192 # Tamanho do chunk para downloads
    MAX_HTML_CHARS = 100000 # Limite de caracteres para HTML

    # --- Configurações de Processamento ---
    BLACKLIST = ['esporte', 'futebol', 'concurso', 'vaga', 'noticia']
