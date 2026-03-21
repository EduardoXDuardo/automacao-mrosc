import logging
from typing import List
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
        
        logger.info(f"🔎 Realizando web search (DDGo) para '{self.estado}' usando {len(queries)} queries...")
        
        for q in queries:
            try:
                res = self._fetch_duckduckgo(q)
                for r in res:
                    if not any(b in r['href'].lower() for b in Config.BLACKLIST):
                        found.append(r['href'])
            except Exception as e:
                logger.error(f"⚠️ Erro persistente na busca DuckDuckGo ('{q}'): {e}")
        
        filtered = list(set(found))
        logger.info(f"✅ Web search finalizada. Links únicos encontrados: {len(filtered)}")
        return filtered
