import shutil
import hashlib
import re
import pandas as pd
import threading
from pathlib import Path
from config import logger

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
        self.lock = threading.Lock()

    def process_and_save_document(self, url: str, temp_path: Path, analysis: dict) -> bool:
        """Salva o documento nos resultados e o move para a pasta final. Retorna True se salvo com sucesso."""
        uid = analysis.get("id_unico", f"rand_{hashlib.md5(url.encode()).hexdigest()}")
        
        with self.lock:
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
                self.save_excel(incremental=True)
                return True
            return False

    def save_excel(self, incremental: bool = False):
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
