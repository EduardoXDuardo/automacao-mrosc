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
import pandas as pd
import pdfplumber
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ddgs import DDGS
from pdf2image import convert_from_path
from urllib3.exceptions import InsecureRequestWarning

# --- CONFIGURAÇÃO ---
warnings.simplefilter('ignore', InsecureRequestWarning)
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("MROSC_ARCHIVER")

class Config:
    API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_ID = "gemini-3.1-flash-lite-preview" 
    BLACKLIST = ['edital', 'chamamento', 'esporte', 'futebol', 'concurso', 'vaga', 'noticia']

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
                    # Pega as primeiras 5 páginas para análise de contexto
                    text_content = "\n".join([p.extract_text() or "" for p in pdf.pages[:5]])
                
                if len(text_content.strip()) < 200:
                    logger.info(f"📸 PDF sem texto (OCR necessário) em {path.name}")
                    images = convert_from_path(path, first_page=1, last_page=1)
                    if images:
                        import io
                        img_byte_arr = io.BytesIO()
                        images[0].save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type="image/jpeg"))
            else:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    text_content = soup.get_text(separator=' ', strip=True)[:15000]

            if text_content:
                parts.append(types.Part.from_text(text=text_content))
            return parts
        except Exception as e:
            logger.error(f"❌ Erro ao processar arquivo {path.name}: {e}")
            return []

    def analyze(self, parts: List[types.Part], url: str, estado: str) -> Optional[Dict]:
        if not parts: return None
        
        prompt = f"""
        Você está analisando documentos oficiais do estado de {estado} relacionados às parcerias entre o poder público e Organizações da Sociedade Civil (MROSC – Lei 13.019/2014).

        Seu objetivo é identificar documentos RELEVANTES para análise de capacidades estatais.

        Critérios de relevância:
        - Regulamentação da Lei 13.019 (decretos, leis, portarias)
        - Instrumentos operacionais (manuais, guias, fluxos, sistemas)
        - Evidências de gestão de parcerias (monitoramento, avaliação, prestação de contas)
        - Estruturas institucionais (comissões, órgãos responsáveis, sistemas)
        - Procedimentos administrativos (chamamento público, seleção, execução)

        Classifique como NÃO relevante:
        - Notícias genéricas
        - Conteúdos jornalísticos sem detalhamento técnico
        - Menções superficiais à lei sem conteúdo operacional

        Para documentos relevantes, extraia:

        Retorne APENAS JSON:

        {{
            "relevante": true | false,
            "tipo": "Decreto" | "Lei" | "Portaria" | "Resolução" | "Manual" | "Guia" | "Sistema" | "Página institucional" | "Notícia",
            "titulo": "Título oficial completo do documento",
            "ano": "Ano do documento (se identificado)",
            "estado": "{estado}",
            "dimensao": "Normativa" | "Operacional" | "Governança" | "Controle" | "Capacitação",
            "instrumento_mrosc": "Regulamentação" | "Execução" | "Monitoramento" | "Prestação de contas" | "Chamamento público" | "Outro",
            "consideracao": "Resumo técnico objetivo destacando o que o documento regula ou operacionaliza",
            "tem_fluxo_operacional": true | false,
            "tem_instrumentos_gestao": true | false,
            "id_unico": "ID curto padronizado (ex: dec-61981-sp)",
            "nome_arquivo_sugerido": "Nome curto padronizado (ex: Decreto_61981_SP)"
        }}
        """
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
        self.processor = DocumentProcessor(Config.API_KEY)
        
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = Path("output") / f"{self.uf}_{self.timestamp}"
        self.archives_dir = self.base_dir / "archives"
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.archives_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = []
        self.seen_ids = set()

    def run(self):
        logger.info(f"🚀 Iniciando automação {self.uf} | Pasta: {self.base_dir}")
        links = self._collect_links()
        
        count = 1
        for url in links:
            logger.info(f"🔍 Analisando link: {url}")
            temp_path = self._download(url)
            if not temp_path: continue

            parts = self.processor.get_document_content(temp_path)
            analysis = self.processor.analyze(parts, url, self.estado)
            
            # Verificação segura de dicionário e chave 'relevante'
            if isinstance(analysis, dict) and analysis.get("relevante"):
                uid = analysis.get("id_unico", f"rand_{hash(url)}")
                if uid not in self.seen_ids:
                    self.seen_ids.add(uid)
                    
                    doc_id = f"{self.uf}{count:02d}"
                    ext = temp_path.suffix
                    clean_name = re.sub(r'[^\w\-]', '_', str(analysis.get("nome_arquivo_sugerido", "documento")))
                    
                    final_filename = f"{doc_id}_{clean_name}{ext}"
                    final_path = self.archives_dir / final_filename
                    
                    temp_path.replace(final_path)
                    logger.info(f"💾 Salvo em archives: {final_filename}")
                    
                    self.results.append({
                        "UNIDADE FEDERATIVA": self.estado,
                        "CÓDIGO DO DOCUMENTO": doc_id,
                        "TIPO": analysis.get("tipo", "N/A"),
                        "TITULO": analysis.get("titulo", "N/A"),
                        "LINK": url,
                        "CONSIDERAÇÃO": analysis.get("consideracao", ""),
                        "ARQUIVO LOCAL": f"archives/{final_filename}"
                    })
                    count += 1
                else:
                    logger.info(f"⏭️ Documento duplicado ignorado: {uid}")
                    temp_path.unlink()
            else:
                if temp_path.exists(): temp_path.unlink()
            
            time.sleep(1) # Delay anti-bloqueio

        self._save()

    def _collect_links(self) -> List[str]:
        found = []
        queries = [
            # Base legal direta
            f'"Lei 13.019" {self.estado}',
            f'marco regulatório organizações sociedade civil {self.estado}',
            f'MROSC {self.estado} regulamentação',

            # Decretos e normativas
            f'decreto regulamenta lei 13.019 {self.estado}',
            f'decreto parcerias OSC {self.estado}',
            f'instrução normativa MROSC {self.estado}',
            f'resolução parcerias sociedade civil {self.estado}',
            f'portaria parcerias OSC {self.estado}',

            # Instrumentos operacionais
            f'manual parcerias OSC {self.estado}',
            f'guia MROSC {self.estado}',
            f'cartilha organizações sociedade civil {self.estado}',
            f'fluxo prestação de contas OSC {self.estado}',

            # Sistemas e gestão
            f'sistema gestão parcerias OSC {self.estado}',
            f'plataforma parcerias governo {self.estado}',
            f'chamamento público OSC {self.estado}',

            # Transparência e controle
            f'diário oficial {self.estado} organizações sociedade civil',
            f'transferências voluntárias OSC {self.estado}',
            f'prestação de contas parceria OSC {self.estado}',

            # Busca restrita a domínios oficiais
            f'site:{self.uf.lower()}.gov.br "organizações da sociedade civil"',
            f'site:{self.uf.lower()}.gov.br "parcerias"',
            f'site:{self.uf.lower()}.gov.br "chamamento público"',
            
            # Queries com a liguagem da burocracia
            f'"termo de colaboração" {self.estado}',
            f'"termo de fomento" {self.estado}',
            f'"acordo de cooperação" OSC {self.estado}',
            f'"comissão de monitoramento" OSC {self.estado}',

            # Queries orientadas ao seu framework analítico
            f'monitoramento avaliação parcerias OSC {self.estado}',
            f'capacitação OSC governo {self.estado}',
            f'governança parcerias sociedade civil {self.estado}',
            f'fluxo administrativo parcerias OSC {self.estado}',
            f'indicadores parceria governo OSC {self.estado}'
        ]
        with DDGS() as ddgs:
            for q in queries:
                try:
                    res = ddgs.text(q, region='br-pt', max_results=10)
                    for r in res:
                        if not any(b in r['href'].lower() for b in Config.BLACKLIST):
                            found.append(r['href'])
                except Exception as e:
                    logger.warning(f"⚠️ Erro na busca DuckDuckGo: {e}")
        return list(set(found))

    def _download(self, url: str) -> Optional[Path]:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(url, timeout=30, verify=False, headers=headers)
            ct = r.headers.get('Content-Type', '').lower()
            ext = ".pdf" if "pdf" in ct or url.lower().endswith('.pdf') else ".html"
            
            path = self.base_dir / f"temp_{hash(url)}{ext}"
            path.write_bytes(r.content)
            return path
        except: return None

    def _save(self):
        if self.results:
            df = pd.DataFrame(self.results)
            excel_path = self.base_dir / "dados-compilados.xlsx"
            df.to_excel(excel_path, index=False)
            logger.info(f"✨ PROCESSO CONCLUÍDO!")
            logger.info(f"📂 Planilha: {excel_path}")
        else:
            logger.warning("⚠️ Nenhum documento válido foi encontrado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("uf")
    parser.add_argument("estado")
    args = parser.parse_args()
    
    try:
        MROSCAutomator(args.uf, args.estado).run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrompido pelo usuário.")