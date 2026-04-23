import shutil
import hashlib
import re
import pandas as pd
import threading
from pathlib import Path
from backend.config import logger

class OutputManager:
    def __init__(self, uf: str, estado: str, timestamp: str):
        self.uf = uf.upper()
        self.estado = estado
        
        self.base_dir = Path("output") / f"{self.uf}_{timestamp}"
        self.archives_dir = self.base_dir / "archives"
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.archives_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = []
        self.seen_ids = set()
        self._data_lock = threading.Lock()
        self._excel_lock = threading.Lock()

    def process_and_save_document(self, url: str, temp_path: Path, analysis: dict) -> bool:
        """Salva o documento nos resultados e o move para a pasta final. Retorna True se salvo com sucesso."""
        uid = analysis.get("id_unico", f"rand_{hashlib.sha256(url.encode()).hexdigest()[:16]}")
        
        result_dict = None
        with self._data_lock:
            if uid in self.seen_ids:
                return False
            
            self.seen_ids.add(uid)
            
            count = len(self.results) + 1
            doc_id = f"{self.uf}{count:02d}"
            ext = temp_path.suffix
            clean_name = re.sub(r'[^\w\-]', '_', str(analysis.get("nome_arquivo_sugerido", "documento")))
            
            final_filename = f"{doc_id}_{clean_name}{ext}"
            final_path = self.archives_dir / final_filename
            
            try:
                shutil.copy2(str(temp_path), str(final_path))
            except (OSError, shutil.Error) as e:
                logger.warning(f"[COPY_WARN] shutil.copy2 falhou ({e}), tentando shutil.move...")
                try:
                    shutil.move(str(temp_path), str(final_path))
                except Exception as move_err:
                    logger.error(f"[COPY_ERROR] Falha ao copiar/mover documento: {move_err}")
                    self.seen_ids.discard(uid)
                    return False
                    
            logger.info(f"[DB_SAVE] Documento arquivado -> {final_filename}")
            
            result_dict = {
                "UF / ESTADO": self.estado,
                "CÓDIGO DO DOCUMENTO": doc_id,
            }
            
            # Incorpora dinamicamente todos os campos que vieram no schema do LLM
            # com exceção de nomes técnicos indesejados na planilha final
            for key, val in analysis.items():
                if key not in ["id_unico", "nome_arquivo_sugerido", "relevante"]:
                    nome_coluna = str(key).replace("_", " ").upper()
                    result_dict[nome_coluna] = val
                    
            result_dict.update({
                "LINK": url,
                "ARQUIVO LOCAL": f"archives/{final_filename}"
            })
            
            self.results.append(result_dict)

        # Excel write happens OUTSIDE the data lock to avoid blocking other threads
        self.save_excel(incremental=True)
        return True

    def save_excel(self, incremental: bool = False):
        with self._excel_lock:
            # Snapshot the results list under data lock to avoid race
            with self._data_lock:
                if not self.results:
                    if not incremental:
                        logger.warning("[DB_WARN] Job finalizado sem nenhum artefato classificado como Relevante.")
                    return
                results_snapshot = list(self.results)
            
            try:
                df = pd.DataFrame(results_snapshot)
                excel_path = self.base_dir / "dados-compilados.xlsx"
                df.to_excel(excel_path, index=False)
                if not incremental:
                    logger.info(f"[DB_FINISH] Exportação Final concluída com SUCESSO.")
                    logger.info(f"[DB_FINISH] Planilha gerada no caminho: {excel_path}")
                else:
                    logger.info(f"[DB_OK] Planilha Dataframe Incremental atualizada. (Docs: {len(results_snapshot)})")
            except Exception as e:
                logger.error(f"[DB_ERROR] Falha de I/O ao gravar XLS: {e}")
