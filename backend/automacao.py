#!/usr/bin/env python3
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.config import Config, logger
from backend.processor import DocumentProcessor
from backend.searcher import Searcher
from backend.downloader import Downloader
from backend.output_manager import OutputManager

class MROSCAutomator:
    def __init__(self, template_data: dict, variables: dict, limit: int = 10):
        self.template_data = template_data
        self.variables = variables
        
        estado_name = variables.get("estado", "Unknown")
        uf_code = variables.get("uf", "XX").upper()
        
        self.uf = uf_code
        self.estado = estado_name
        
        if limit < 1:
            raise ValueError("O parâmetro 'limit' deve ser >= 1")
        
        self.processor = DocumentProcessor(Config.get_api_key())
            
        self.searcher = Searcher(template_data, variables, limit=limit)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.output_manager = OutputManager(self.uf, self.estado, self.timestamp)
        self.downloader = Downloader(self.output_manager.base_dir)

    def _process_single_link(self, idx: int, total_links: int, url: str, ui_callback: Optional[callable] = None):
        logger.info(f"--- [ {idx:02d} / {total_links:02d} ] ---")
        logger.info(f"[DOWNLOAD] Inicializando captura: {url}")
        if ui_callback: ui_callback({"type": "downloading", "url": url, "current": idx, "total": total_links})
        
        temp_path = self.downloader.download(url)
        if not temp_path: 
            return

        try:
            if ui_callback: ui_callback({"type": "downloaded", "path": str(temp_path), "url": url})
            
            parts = self.processor.get_document_content(temp_path)
            if not parts:
                logger.warning(f"[EXTRACT_WARN] Nenhum conteúdo extraível - Abortando URL {url}")
                if ui_callback: ui_callback({"type": "error", "message": "Nenhum conteúdo extraído.", "url": url})
                return
            
            logger.info(f"[AI_ANALYSIS] Disparando requisição {Config.MODEL_ID} - {url}")
            if ui_callback: ui_callback({"type": "analyzing", "url": url})
            
            analysis = self.processor.analyze(parts, url, self.template_data, self.variables)
            
            if ui_callback: ui_callback({"type": "analysis_done", "url": url, "analysis": analysis})
            
            if isinstance(analysis, dict):
                is_relevante = analysis.get("relevante", True)
                if is_relevante:
                    salvo = self.output_manager.process_and_save_document(url, temp_path, analysis)
                if salvo:
                    if ui_callback: 
                        final_path = self.output_manager.archives_dir / Path(self.output_manager.results[-1]["ARQUIVO LOCAL"]).name
                        ui_callback({"type": "saved", "result": self.output_manager.results[-1], "path": str(final_path)})
                else:
                    logger.info(f"[SKIP] Descarte de Duplicata (Hash ID já indexado): {url}")
                    if ui_callback: ui_callback({"type": "ignored", "reason": "Duplicado", "url": url})
            else:
                logger.info(f"[SKIP] Classificado como IRRELEVANTE. {url}")
                if ui_callback: ui_callback({"type": "ignored", "reason": "Não relevante", "url": url})
        except Exception as e:
            logger.error(f"[AI_ERROR] Anomalia na análise do Gemini ({url}): {e}")
            if ui_callback: ui_callback({"type": "error", "message": str(e), "url": url})
        finally:
            if temp_path.exists(): 
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def run(self, ui_callback: Optional[callable] = None, max_workers: Optional[int] = None):
        if max_workers is None:
            max_workers = Config.MAX_THREADS

        # Limpar arquivos órfãos do Gemini antes de iniciar
        self.processor.cleanup_all_files()

        logger.info(f"[START] Automação MROSC inicializada | Job Dir: {self.output_manager.base_dir}")
        
        is_ui_mode = ui_callback is not None
        if is_ui_mode: 
            ui_callback({"type": "status", "message": f"Iniciando automação na UF {self.uf}..."})
        
        links = self.searcher.collect_links()
        
        total_links = len(links)
        logger.info(f"[PIPELINE] Trabalhos enfileirados: {total_links}")
        if is_ui_mode: ui_callback({"type": "links_found", "total": total_links, "links": links})
        
        if is_ui_mode:
            # Roda sequencial no Streamlit
            for idx, url in enumerate(links, 1):
                self._process_single_link(idx, total_links, url, ui_callback)
        else:
            # Roda em paralelo na CLI
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for idx, url in enumerate(links, 1):
                    futures.append(executor.submit(self._process_single_link, idx, total_links, url, None))
                    time.sleep(0.5)
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"[THREAD_ERROR] Problema catastrófico em worker: {e}")

        logger.info("[FINISH] Pipeline base concluído. Encerrando conexões IO.")
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
