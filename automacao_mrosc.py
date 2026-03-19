#!/usr/bin/env python3
import os
import sys
import time
import json
import logging
import argparse
import requests
import warnings
import re
import hashlib
import pandas as pd
import pdfplumber
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from ddgs import DDGS
from pdf2image import convert_from_path
from urllib3.exceptions import InsecureRequestWarning

from config import Config, logger
from prompts import get_analysis_prompt
from queries import get_search_queries

# --- CONFIGURAÇÃO ---
warnings.simplefilter('ignore', InsecureRequestWarning)

class DocumentProcessor:
    def __init__(self, api_key: str):
        if not api_key:
            logger.error("❌ GEMINI_API_KEY não configurada no .env")
            sys.exit(1)
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
            
            # Limpeza e parsing resiliente
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

class MROSCAutomator:
    def __init__(self, uf: str, estado: str):
        self.uf = uf.upper()
        self.estado = estado
        self.processor = DocumentProcessor(Config.get_api_key())
        
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = Path("output") / f"{self.uf}_{self.timestamp}"
        self.archives_dir = self.base_dir / "archives"
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.archives_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = []
        self.seen_ids = set()

    def process_and_save_document(self, url: str, temp_path: Path, analysis: dict) -> bool:
        """Salva o documento nos resultados e o move para a pasta final. Retorna True se salvo com sucesso."""
        uid = analysis.get("id_unico", f"rand_{hashlib.md5(url.encode()).hexdigest()}")
        if uid not in self.seen_ids:
            self.seen_ids.add(uid)
            
            # Conta apenas os já aprovados iterativamente para gerar doc_id incremental
            count = len(self.results) + 1
            doc_id = f"{self.uf}{count:02d}"
            ext = temp_path.suffix
            clean_name = re.sub(r'[^\w\-]', '_', str(analysis.get("nome_arquivo_sugerido", "documento")))
            
            final_filename = f"{doc_id}_{clean_name}{ext}"
            final_path = self.archives_dir / final_filename
            
            try:
                import shutil
                shutil.copy(str(temp_path), str(final_path))
            except Exception:
                temp_path.replace(final_path)
                
            logger.info(f"✅ DOCUMENTO SALVO! Tipo: {analysis.get('tipo', 'N/A')} -> {final_filename}")
            
            result_dict = {
                "UNIDADE FEDERATIVA": self.estado,
                "CÓDIGO DO DOCUMENTO": doc_id,
                "TIPO": analysis.get("tipo", "N/A"),
                "TITULO": analysis.get("titulo", "N/A"),
                "LINK": url,
                "CONSIDERAÇÃO": analysis.get("consideracao", ""),
                "ARQUIVO LOCAL": f"archives/{final_filename}"
            }
            self.results.append(result_dict)
            self._save(incremental=True)
            return True
        return False

    def run(self, ui_callback: Optional[callable] = None):
        logger.info(f"🚀 Iniciando automação {self.uf} | Pasta: {self.base_dir}")
        if ui_callback: ui_callback({"type": "status", "message": f"Iniciando automação {self.uf}..."})
        
        links = self._collect_links()
        
        total_links = len(links)
        logger.info(f"🎯 Total de links filtrados a serem analisados: {total_links}")
        if ui_callback: ui_callback({"type": "links_found", "total": total_links, "links": links})
        
        count = 1
        for idx, url in enumerate(links, 1):
            logger.info(f"")
            logger.info(f"--- [ {idx} / {total_links} ] ---")
            logger.info(f"🔍 Baixando e extraindo: {url}")
            if ui_callback: ui_callback({"type": "downloading", "url": url, "current": idx, "total": total_links})
            
            temp_path = self._download(url)
            if not temp_path: 
                continue

            try:
                if ui_callback: ui_callback({"type": "downloaded", "path": str(temp_path), "url": url})
                
                parts = self.processor.get_document_content(temp_path)
                if not parts:
                    logger.warning("⚠️ Nenhum conteúdo extraído. Pulando.")
                    if ui_callback: ui_callback({"type": "error", "message": "Nenhum conteúdo extraído."})
                    continue
                
                logger.info("🧠 Solicitando análise ao Gemini...")
                if ui_callback: ui_callback({"type": "analyzing", "url": url})
                analysis = self.processor.analyze(parts, url, self.estado)
                
                if ui_callback: ui_callback({"type": "analysis_done", "url": url, "analysis": analysis})
                
                # Verificação segura de dicionário e chave 'relevante'
                if isinstance(analysis, dict) and analysis.get("relevante"):
                    salvo = self.process_and_save_document(url, temp_path, analysis)
                    if salvo:
                        if ui_callback: 
                            final_path = self.archives_dir / Path(self.results[-1]["ARQUIVO LOCAL"]).name
                            ui_callback({"type": "saved", "result": self.results[-1], "path": str(final_path)})
                        count += 1
                    else:
                        logger.info(f"⏭️ Documento duplicado ignorado.")
                        if ui_callback: ui_callback({"type": "ignored", "reason": "Duplicado"})
                else:
                    logger.info("❌ Documento avaliado como NÃO RELEVANTE pelo modelo.")
                    if ui_callback: ui_callback({"type": "ignored", "reason": "Não relevante"})
            except Exception as e:
                logger.error(f"❌ Erro ao processar arquivo: {e}")
                if ui_callback: ui_callback({"type": "error", "message": str(e)})
            finally:
                if temp_path.exists(): 
                    temp_path.unlink()
            
            time.sleep(1) # Delay anti-bloqueio

        logger.info(f"")
        self._save(incremental=False)
        if ui_callback: ui_callback({"type": "done", "results_count": len(self.results), "excel": str(self.base_dir / "dados-compilados.xlsx")})

    def _collect_links(self) -> List[str]:
        found = []
        queries = get_search_queries(self.uf, self.estado)
        
        logger.info(f"🔎 Realizando web search (DDGo) para '{self.estado}' usando {len(queries)} queries...")
        
        with DDGS() as ddgs:
            for q in queries:
                try:
                    res = ddgs.text(q, region='br-pt', max_results=10)
                    for r in res:
                        if not any(b in r['href'].lower() for b in Config.BLACKLIST):
                            found.append(r['href'])
                except Exception as e:
                    logger.warning(f"⚠️ Erro na busca DuckDuckGo ('{q}'): {e}")
        
        filtered = list(set(found))
        logger.info(f"✅ Web search finalizada. Links únicos encontrados: {len(filtered)}")
        return filtered

    def _download(self, url: str) -> Optional[Path]:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            url_hash = hashlib.md5(url.encode()).hexdigest()
            
            with requests.get(url, timeout=Config.TIMEOUT, verify=False, headers=headers, stream=True) as r:
                r.raise_for_status()
                ct = r.headers.get('Content-Type', '').lower()
                ext = ".pdf" if "pdf" in ct or url.lower().endswith('.pdf') else ".html"
                
                path = self.base_dir / f"temp_{url_hash}{ext}"
                
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=Config.DOWNLOAD_CHUNK_SIZE):
                        f.write(chunk)
                return path
        except Exception as e:
            logger.warning(f"⚠️ Erro ao baixar {url}: {e}")
            return None

    def _save(self, incremental: bool = False):
        if self.results:
            try:
                df = pd.DataFrame(self.results)
                excel_path = self.base_dir / "dados-compilados.xlsx"
                df.to_excel(excel_path, index=False)
                if not incremental:
                    logger.info(f"✨ PROCESSO CONCLUÍDO!")
                    logger.info(f"📂 Planilha final gerada em: {excel_path}")
                else:
                    logger.info(f"💾 Planilha ATUALIZADA (Total: {len(self.results)} docs)...")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar planilha Excel: {e}")
        else:
            if not incremental:
                logger.warning("⚠️ PROCESSO CONCLUÍDO, mas nenhum documento válido foi encontrado/cadastrado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("uf")
    parser.add_argument("estado")
    args = parser.parse_args()
    
    try:
        MROSCAutomator(args.uf, args.estado).run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrompido pelo usuário.")