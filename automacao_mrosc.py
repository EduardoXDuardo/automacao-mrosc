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

from config import Config, logger
from processor import DocumentProcessor
from searcher import Searcher
from downloader import Downloader
from output_manager import OutputManager

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

    def run(self, ui_callback: Optional[callable] = None):
        logger.info(f"🚀 Iniciando automação {self.uf} | Pasta: {self.output_manager.base_dir}")
        if ui_callback: ui_callback({"type": "status", "message": f"Iniciando automação {self.uf}..."})
        
        links = self.searcher.collect_links()
        
        total_links = len(links)
        logger.info(f"🎯 Total de links filtrados a serem analisados: {total_links}")
        if ui_callback: ui_callback({"type": "links_found", "total": total_links, "links": links})
        
        count = 1
        for idx, url in enumerate(links, 1):
            logger.info(f"")
            logger.info(f"--- [ {idx} / {total_links} ] ---")
            logger.info(f"🔍 Baixando e extraindo: {url}")
            if ui_callback: ui_callback({"type": "downloading", "url": url, "current": idx, "total": total_links})
            
            temp_path = self.downloader.download(url)
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
                            final_path = self.output_manager.archives_dir / Path(self.output_manager.results[-1]["ARQUIVO LOCAL"]).name
                            ui_callback({"type": "saved", "result": self.output_manager.results[-1], "path": str(final_path)})
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