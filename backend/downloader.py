import hashlib
import requests
import logging
import urllib3
from urllib.parse import urlparse
from urllib3.exceptions import InsecureRequestWarning
from pathlib import Path
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from backend.config import Config, logger

urllib3.disable_warnings(InsecureRequestWarning)

class Downloader:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.session = requests.Session()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _execute_download(self, url: str) -> Optional[Path]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        
        try:
            r = self.session.get(url, timeout=Config.TIMEOUT, verify=True, headers=headers, stream=True)
        except requests.exceptions.SSLError:
            logger.warning(f"⚠️ Falha SSL em {url}, tentando sem verificação de certificado (verify=False).")
            r = self.session.get(url, timeout=Config.TIMEOUT, verify=False, headers=headers, stream=True)
        
        path = None
        try:
            r.raise_for_status()

            # Verificar tamanho do arquivo antes de baixar
            content_length = r.headers.get('Content-Length')
            if content_length and int(content_length) > Config.MAX_FILE_SIZE:
                logger.warning(f"⚠️ Arquivo muito grande ({int(content_length) // (1024*1024)} MB), ignorando: {url}")
                return None

            ct = r.headers.get('Content-Type', '').lower()
            ext = ".pdf" if "pdf" in ct or url.lower().endswith('.pdf') else ".html"
            
            path = self.base_dir / f"temp_{url_hash}{ext}"
            
            downloaded_bytes = 0
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=Config.DOWNLOAD_CHUNK_SIZE):
                    if chunk:
                        downloaded_bytes += len(chunk)
                        if downloaded_bytes > Config.MAX_FILE_SIZE:
                            logger.warning(f"⚠️ Download excedeu limite de {Config.MAX_FILE_SIZE // (1024*1024)} MB, abortando: {url}")
                            raise IOError("Arquivo excede limite máximo de tamanho")
                        f.write(chunk)
            
            return path
        except Exception:
            if path is not None and path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass
            raise
        finally:
            r.close()

    def download(self, url: str) -> Optional[Path]:
        try:
            return self._execute_download(url)
        except Exception as e:
            logger.error(f"❌ Falha definitiva ao baixar {url} após retries: {e}")
            return None
