import json
import logging
import re
import time
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from config import Config, logger
from prompts import get_analysis_prompt

class AnalysisResult(BaseModel):
    relevante: bool = Field(description="Booleano que indica se o documento é relevante para o assunto MROSC.")
    id_unico: str = Field(description="Um identificador curto e único para este documento baseado no título.")
    nome_arquivo_sugerido: str = Field(description="Um nome de arquivo curto, em snake_case, sem extensão, representando o arquivo.")
    tipo: str = Field(description="A categoria legal ou tipo do documento (ex: Edital, Portaria, Cartilha, etc).")
    titulo: str = Field(description="O título oficial ou manchete principal do documento.")
    consideracao: str = Field(description="Uma breve justificativa da sua análise informando por que é ou não é relevante.")

class DocumentProcessor:
    def __init__(self, api_key: str):
        if not api_key:
            logger.error("❌ GEMINI_API_KEY não configurada no .env")
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        self.client = genai.Client(api_key=api_key)
        self.cleanup_all_files()

    def cleanup_all_files(self):
        """Limpa arquivos que possam ter ficado no servidor Gemini de execuções anteriores, se houvesse erro de cancelamento ou falha"""
        try:
            files_to_delete = []
            for f in self.client.files.list():
                files_to_delete.append(f.name)
            
            for f_name in files_to_delete:
                try:
                    self.client.files.delete(name=f_name)
                    logger.info(f"🗑️ Arquivo órfão limpo internamente no Gemini: {f_name}")
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível limpar os arquivos antigos. {e}")

    def get_document_content(self, path: Path) -> List[types.Part]:
        parts = []
        text_content = ""
        try:
            if path.suffix == ".pdf":
                logger.info(f"📂 Fazendo upload nativo do PDF inteiro para API do Gemini: {path.name}")
                uploaded_file = self.client.files.upload(file=str(path))
                
                # Aguardar o processamento do arquivo no servidor do Google (necessário para PDFs longos)
                while str(uploaded_file.state).upper().endswith("PROCESSING"):
                    logger.info(f"⏳ O Gemini está lendo e indexando o PDF {path.name}... (Aguarde)")
                    time.sleep(2)
                    uploaded_file = self.client.files.get(name=uploaded_file.name)
                
                if "FAILED" in str(uploaded_file.state).upper():
                    logger.error(f"❌ O Gemini reportou erro interno ao tentar ler o PDF: {path.name}")
                else:
                    parts.append(uploaded_file)

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
                    response_mime_type="application/json",
                    response_schema=AnalysisResult
                )
            )
            
            raw_text = response.text.strip()
            raw_text = re.sub(r'```json\n?|```', '', raw_text)
            
            data = json.loads(raw_text)
            return data

        except Exception as e:
            logger.error(f"⚠️ Falha no parsing da análise Gemini: {e}")
            return None
        finally:
            # Limpeza do arquivo no Google GenAI caso tenha sido uploadado via File API
            for part in parts:
                if hasattr(part, 'name'):
                    try:
                        self.client.files.delete(name=part.name)
                        logger.info(f"🗑️ Arquivo {part.name} limpo do servidor do Gemini.")
                    except:
                        pass
