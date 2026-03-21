import hashlib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path
from typing import Optional

from config import Config, logger

class Downloader:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.session = requests.Session()
        
        retries = Retry(
            total=3, 
            backoff_factor=1, 
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def download(self, url: str) -> Optional[Path]:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            url_hash = hashlib.md5(url.encode()).hexdigest()
            
            with self.session.get(url, timeout=Config.TIMEOUT, verify=False, headers=headers, stream=True) as r:
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
