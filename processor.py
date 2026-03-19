import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from pdf2image import convert_from_path

from config import Config, logger
from prompts import get_analysis_prompt

class DocumentProcessor:
    def __init__(self, api_key: str):
        if not api_key:
            logger.error("❌ GEMINI_API_KEY não configurada no .env")
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        self.client = genai.Client(api_key=api_key)

    def get_document_content(self, path: Path) -> List[types.Part]:
        parts = []
        text_content = ""
        try:
            if path.suffix == ".pdf":
                with pdfplumber.open(path) as pdf:
                    # Pega as priemeiras X páginas para análise de contexto
                    text_content = "\n".join([p.extract_text() or "" for p in pdf.pages[:Config.PDF_PAGES_TO_EXTRACT]])
                
                if len(text_content.strip()) < 200:
                    logger.info(f"📸 PDF sem texto (OCR necessário) em {path.name} - pegando primeiras {Config.OCR_PAGES_TO_EXTRACT} pags")
                    images = convert_from_path(path, first_page=1, last_page=Config.OCR_PAGES_TO_EXTRACT)
                    if images:
                        import io
                        for index, img in enumerate(images):
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format='JPEG')
                            parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type="image/jpeg"))
            else:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    text_content = soup.get_text(separator=' ', strip=True)[:Config.MAX_HTML_CHARS]

            if text_content:
                parts.append(types.Part.from_text(text=text_content))
            return parts
        except Exception as e:
            logger.error(f"❌ Erro ao processar arquivo {path.name}: {e}")
            return []

    def analyze(self, parts: List[types.Part], url: str, estado: str) -> Optional[Dict]:
        if not parts: return None
        
        prompt = get_analysis_prompt(estado)
        
        try:
            response = self.client.models.generate_content(
                model=Config.MODEL_ID,
                contents=[prompt] + parts,
                config=types.GenerateContentConfig(
                    temperature=0.0, 
                    response_mime_type="application/json"
                )
            )
            
            # Limpeza e parsing
            raw_text = response.text.strip()
            # Remove blocos de código markdown se o modelo ignorar o response_mime_type
            raw_text = re.sub(r'```json\n?|```', '', raw_text)
            
            data = json.loads(raw_text)

            # Tratamento de erro: se retornar uma lista, pega o primeiro elemento
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            
            return data if isinstance(data, dict) else None

        except Exception as e:
            logger.error(f"⚠️ Falha no parsing da análise Gemini: {e}")
            return None
