import logging
from typing import List
import time
from ddgs import DDGS
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from config import Config, logger
from queries import get_search_queries

class Searcher:
    def __init__(self, uf: str, estado: str):
        self.uf = uf
        self.estado = estado

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _fetch_duckduckgo(self, query: str) -> List[dict]:
        with DDGS() as ddgs:
            return list(ddgs.text(query, region='br-pt', max_results=10))

    def collect_links(self) -> List[str]:
        found = []
        queries = get_search_queries(self.uf, self.estado)
        
        logger.info(f"[SEARCH] Iniciando varredura DuckDuckGo | Estado: {self.estado} ({self.uf}) | Queries: {len(queries)}")
        
        for q in queries:
            try:
                res = self._fetch_duckduckgo(q)
                for r in res:
                    if not any(b in r['href'].lower() for b in Config.BLACKLIST):
                        found.append(r['href'])
                time.sleep(1.5)
            except Exception as e:
                logger.error(f"[SEARCH_ERROR] Falha persistente na query ('{q}'): {e}")
        
        filtered = list(set(found))
        logger.info(f"[SEARCH] Varredura concluída. Links brutos consolidados: {len(filtered)}")
        return filtered
