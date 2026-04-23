import logging
from typing import List, Dict
from urllib.parse import urlparse, urlunparse
import time
from ddgs import DDGS
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from backend.config import Config, logger
from backend.queries import get_search_queries

class Searcher:
    def __init__(self, template_data: Dict, variables: Dict, limit: int = 10):
        self.template_data = template_data
        self.variables = variables
        self.limit = max(1, limit)
        self.blacklist = template_data.get("blacklist", Config.BLACKLIST)
        self.sites_especificos = template_data.get("sites_especificos", [])

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _fetch_duckduckgo(self, query: str) -> List[dict]:
        with DDGS() as ddgs:
            return list(ddgs.text(query, region='br-pt', max_results=self.limit))

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normaliza URL para deduplicação mais eficaz."""
        parsed = urlparse(url)
        # Remove fragmento e trailing slash do path
        normalized_path = parsed.path.rstrip('/')
        return urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            normalized_path,
            parsed.params,
            parsed.query,
            ''  # remove fragment
        ))

    def _is_blacklisted(self, url: str) -> bool:
        """Verifica blacklist apenas no path da URL, não nos query params."""
        path = urlparse(url).path.lower()
        return any(term in path for term in self.blacklist)

    def collect_links(self) -> List[str]:
        found = []
        queries = get_search_queries(self.template_data, self.variables)
        
        estado_name = self.variables.get("estado", "Unknown")
        uf_code = self.variables.get("uf", "XX")
        logger.info(f"[SEARCH] Iniciando varredura DuckDuckGo | Estado: {estado_name} ({uf_code}) | Queries: {len(queries)}")
        
        for q in queries:
            try:
                res = self._fetch_duckduckgo(q)
                for r in res:
                    href = r.get('href', '')
                    if href and not self._is_blacklisted(href):
                        found.append(self._normalize_url(href))
                time.sleep(1.5)
            except Exception as e:
                logger.error(f"[SEARCH_ERROR] Falha persistente na query ('{q}'): {e}")
                
        if self.sites_especificos:
            logger.info(f"[SEARCH] Iniciando varredura de sites específicos: {len(self.sites_especificos)}")
            for site in self.sites_especificos:
                try:
                    # Format site URL with variables
                    class SafeDict(dict):
                        def __missing__(self, key):
                            return '{' + key + '}'
                    
                    formatted_site = site.format_map(SafeDict(self.variables))
                    
                    # Cria as querys acoplando restrição de site
                    # Para não cruzar com todas as querys, buscamos o termo principal do template.
                    # Mas se quiser cobrir *todas* querys em todos sites, pode ser um cartesian product (caro).
                    site_query = f"site:{formatted_site}"
                    
                    res = self._fetch_duckduckgo(site_query)
                    for r in res:
                        href = r.get('href', '')
                        if href and not self._is_blacklisted(href):
                            found.append(self._normalize_url(href))
                    time.sleep(1.5)
                except Exception as e:
                    logger.warning(f"[SEARCH_SITE_ERROR] Falha na busca por site ({site}): {e}")
        
        # Deduplica preservando ordem de inserção
        filtered = list(dict.fromkeys(found))
        logger.info(f"[SEARCH] Varredura concluída. Links brutos consolidados: {len(filtered)}")
        return filtered
