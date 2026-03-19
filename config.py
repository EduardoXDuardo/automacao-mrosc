import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_ID = "gemini-3.1-flash-lite-preview" 
    BLACKLIST = ['edital', 'chamamento', 'esporte', 'futebol', 'concurso', 'vaga', 'noticia']
