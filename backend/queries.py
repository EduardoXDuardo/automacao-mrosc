from typing import List, Dict

def get_search_queries(template_data: Dict, variables: Dict) -> List[str]:
    queries = template_data.get("queries", [])
    
    # Helper to safe format
    class SafeDict(dict):
        def __missing__(self, key):
            return '{' + key + '}'
    
    safe_vars = SafeDict(variables)
    
    formatted_queries = []
    for q in queries:
        try:
            formatted_queries.append(q.format_map(safe_vars))
        except Exception:
            formatted_queries.append(q)
            
    return formatted_queries
