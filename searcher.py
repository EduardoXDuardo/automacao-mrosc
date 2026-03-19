import logging
from typing import List
from ddgs import DDGS

from config import Config, logger
from queries import get_search_queries

class Searcher:
    def __init__(self, uf: str, estado: str):
        self.uf = uf
        self.estado = estado

    def collect_links(self) -> List[str]:
        found = []
        queries = get_search_queries(self.uf, self.estado)
        
        logger.info(f"🔎 Realizando web search (DDGo) para '{self.estado}' usando {len(queries)} queries...")
        
        with DDGS() as ddgs:
            for q in queries:
                try:
                    res = ddgs.text(q, region='br-pt', max_results=10)
                    for r in res:
                        if not any(b in r['href'].lower() for b in Config.BLACKLIST):
                            found.append(r['href'])
                except Exception as e:
                    logger.warning(f"⚠️ Erro na busca DuckDuckGo ('{q}'): {e}")
        
        filtered = list(set(found))
        logger.info(f"✅ Web search finalizada. Links únicos encontrados: {len(filtered)}")
        return filtered
