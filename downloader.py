import hashlib
import requests
import logging
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from pathlib import Path
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from config import Config, logger

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
    def _execute_download(self, url: str) -> Path:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url_hash = hashlib.md5(url.encode()).hexdigest()
        path = None
        success = False
        
        try:
            try:
                r = self.session.get(url, timeout=Config.TIMEOUT, verify=True, headers=headers, stream=True)
            except requests.exceptions.SSLError:
                logger.warning(f"⚠️ Falha SSL em {url}, tentando sem verificação de certificado (verify=False).")
                r = self.session.get(url, timeout=Config.TIMEOUT, verify=False, headers=headers, stream=True)
                
            with r:
                r.raise_for_status()
                ct = r.headers.get('Content-Type', '').lower()
                ext = ".pdf" if "pdf" in ct or url.lower().endswith('.pdf') else ".html"
                
                path = self.base_dir / f"temp_{url_hash}{ext}"
                
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=Config.DOWNLOAD_CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
            
            success = True
            return path
        finally:
            if not success and path is not None and path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass

    def download(self, url: str) -> Optional[Path]:
        try:
            return self._execute_download(url)
        except Exception as e:
            logger.error(f"❌ Falha definitiva ao baixar {url} após retries: {e}")
            return None
