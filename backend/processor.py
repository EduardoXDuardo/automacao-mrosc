import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, create_model
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

from backend.config import Config, logger
from backend.prompts import get_analysis_prompt

def _build_analysis_model(schema_fields: List[Dict]) -> type:
    """Builds AnalysisResult model dynamically from schema definition."""
    field_definitions = {}
    for config in schema_fields:
        field_name = config.get("nome")
        if not field_name:
            continue
            
        field_type_str = config.get("tipo", "str")
        description = config.get("descricao", "")
        
        if field_type_str == "bool":
            field_type = bool
            field_definitions[field_name] = (field_type, Field(description=description))
        elif field_type_str == "bool_opt":
            field_type = Optional[bool]
            field_definitions[field_name] = (field_type, Field(default=None, description=description))
        elif field_type_str == "str_opt":
            field_type = Optional[str]
            field_definitions[field_name] = (field_type, Field(default=None, description=description))
        else: # default a "str"
            field_type = str
            field_definitions[field_name] = (field_type, Field(description=description))
    
    if not field_definitions:
        # Fallback de segurança mínimo
        field_definitions["resumo"] = (str, Field(description="Resumo do documento."))
        
    return create_model("AnalysisResult", **field_definitions)

class DocumentProcessor:
    MAX_FILE_PROCESSING_WAIT = 120  # segundos máximos para aguardar processamento de PDF no Gemini

    def __init__(self, api_key: str):
        if not api_key:
            logger.error("❌ GEMINI_API_KEY não configurada no .env")
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        self.client = genai.Client(api_key=api_key)

    def cleanup_all_files(self):
        """Limpa arquivos que possam ter ficado no servidor Gemini de execuções anteriores."""
        try:
            files_to_delete = [f.name for f in self.client.files.list()]
            
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
        try:
            if path.suffix.lower() == ".pdf":
                logger.info(f"📂 Fazendo upload nativo do PDF inteiro para API do Gemini: {path.name}")
                uploaded_file = self.client.files.upload(file=str(path))
                
                elapsed = 0
                while str(uploaded_file.state).upper().endswith("PROCESSING"):
                    if elapsed >= self.MAX_FILE_PROCESSING_WAIT:
                        logger.error(f"⏰ Timeout aguardando processamento do PDF {path.name} ({elapsed}s)")
                        try:
                            self.client.files.delete(name=uploaded_file.name)
                        except Exception:
                            pass
                        return []
                    logger.info(f"⏳ O Gemini está lendo e indexando o PDF {path.name}... (Aguarde)")
                    time.sleep(2)
                    elapsed += 2
                    uploaded_file = self.client.files.get(name=uploaded_file.name)
                
                if "FAILED" in str(uploaded_file.state).upper():
                    logger.error(f"❌ O Gemini reportou erro interno ao tentar ler o PDF: {path.name}")
                    try:
                        self.client.files.delete(name=uploaded_file.name)
                    except Exception:
                        pass
                    return []
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=15),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _call_gemini(self, prompt: str, parts: List[types.Part], response_model: type) -> dict:
        """Chama a API Gemini com retry automático para erros transientes."""
        response = self.client.models.generate_content(
            model=Config.MODEL_ID,
            contents=[prompt] + parts,
            config=types.GenerateContentConfig(
                temperature=0.0, 
                response_mime_type="application/json",
                response_schema=response_model
            )
        )
        
        if not response.text or not response.text.strip():
            raise ValueError("Resposta vazia recebida da API Gemini")
        
        return json.loads(response.text.strip())

    def analyze(self, parts: List[types.Part], url: str, template_data: Dict, variables: Dict) -> Optional[Dict]:
        if not parts:
            return None
        
        prompt = get_analysis_prompt(template_data, variables)
        response_model = _build_analysis_model(template_data.get("schema_de_saida", []))
        
        try:
            return self._call_gemini(prompt, parts, response_model)
        except Exception as e:
            logger.error(f"⚠️ Falha na análise Gemini após retries: {e}")
            return None
        finally:
            for part in parts:
                if hasattr(part, 'name'):
                    try:
                        self.client.files.delete(name=part.name)
                        logger.info(f"🗑️ Arquivo {part.name} limpo do servidor do Gemini.")
                    except Exception:
                        pass
