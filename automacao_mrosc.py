#!/usr/bin/env python3
import os
import sys
import time
import argparse
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import Config, logger
from processor import DocumentProcessor
from searcher import Searcher
from downloader import Downloader
from output_manager import OutputManager

try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
except ImportError:
    add_script_run_ctx = None
    get_script_run_ctx = None

class MROSCAutomator:
    def __init__(self, uf: str, estado: str):
        self.uf = uf.upper()
        self.estado = estado
        
        try:
            self.processor = DocumentProcessor(Config.get_api_key())
        except ValueError:
            sys.exit(1)
            
        self.searcher = Searcher(self.uf, self.estado)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.output_manager = OutputManager(self.uf, self.estado, self.timestamp)
        self.downloader = Downloader(self.output_manager.base_dir)

    def process_and_save_document(self, url: str, temp_path: Path, analysis: dict) -> bool:
        return self.output_manager.process_and_save_document(url, temp_path, analysis)

    def _process_single_link(self, idx: int, total_links: int, url: str, ui_callback: Optional[callable] = None, ctx = None):
        if add_script_run_ctx and ctx:
            import threading
            add_script_run_ctx(threading.current_thread(), ctx)

        logger.info(f"")
        logger.info(f"--- [ {idx} / {total_links} ] ---")
        logger.info(f"🔍 Baixando e extraindo: {url}")
        if ui_callback: ui_callback({"type": "downloading", "url": url, "current": idx, "total": total_links})
        
        temp_path = self.downloader.download(url)
        if not temp_path: 
            return

        try:
            if ui_callback: ui_callback({"type": "downloaded", "path": str(temp_path), "url": url})
            
            parts = self.processor.get_document_content(temp_path)
            if not parts:
                logger.warning(f"⚠️ Nenhum conteúdo extraído. Pulando URL: {url}")
                if ui_callback: ui_callback({"type": "error", "message": "Nenhum conteúdo extraído.", "url": url})
                return
            
            logger.info(f"🧠 Solicitando análise ao Gemini para: {url}")
            if ui_callback: ui_callback({"type": "analyzing", "url": url})
            analysis = self.processor.analyze(parts, url, self.estado)
            
            if ui_callback: ui_callback({"type": "analysis_done", "url": url, "analysis": analysis})
            
            if isinstance(analysis, dict) and analysis.get("relevante"):
                salvo = self.process_and_save_document(url, temp_path, analysis)
                if salvo:
                    if ui_callback: 
                        final_path = self.output_manager.archives_dir / Path(self.output_manager.results[-1]["ARQUIVO LOCAL"]).name
                        ui_callback({"type": "saved", "result": self.output_manager.results[-1], "path": str(final_path)})
                else:
                    logger.info(f"⏭️ Documento duplicado ignorado. URL: {url}")
                    if ui_callback: ui_callback({"type": "ignored", "reason": "Duplicado", "url": url})
            else:
                logger.info(f"❌ Documento avaliado como NÃO RELEVANTE. URL: {url}")
                if ui_callback: ui_callback({"type": "ignored", "reason": "Não relevante", "url": url})
        except Exception as e:
            logger.error(f"❌ Erro ao processar arquivo ({url}): {e}")
            if ui_callback: ui_callback({"type": "error", "message": str(e), "url": url})
        finally:
            if temp_path.exists(): 
                try:
                    temp_path.unlink()
                except:
                    pass

    def run(self, ui_callback: Optional[callable] = None):
        logger.info(f"🚀 Iniciando automação {self.uf} | Pasta: {self.output_manager.base_dir}")
        if ui_callback: ui_callback({"type": "status", "message": f"Iniciando automação {self.uf}..."})
        
        links = self.searcher.collect_links()
        
        total_links = len(links)
        logger.info(f"🎯 Total de links filtrados a serem analisados: {total_links}")
        if ui_callback: ui_callback({"type": "links_found", "total": total_links, "links": links})
        
        # Uso do Pool de Threads baseado no config para Paralelismo
        max_workers = getattr(Config, 'MAX_THREADS', 3)
        logger.info(f"⚡ Iniciando processamento em lotes com {max_workers} threads...")
        
        ctx = get_script_run_ctx() if get_script_run_ctx else None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for idx, url in enumerate(links, 1):
                future = executor.submit(self._process_single_link, idx, total_links, url, ui_callback, ctx)
                futures.append(future)
                
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Erro na thread: {e}")

        logger.info(f"")
        self.output_manager.save_excel(incremental=False)
        if ui_callback: ui_callback({"type": "done", "results_count": len(self.output_manager.results), "excel": str(self.output_manager.base_dir / "dados-compilados.xlsx")})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("uf")
    parser.add_argument("estado")
    args = parser.parse_args()
    
    try:
        MROSCAutomator(args.uf, args.estado).run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrompido pelo usuário.")