from typing import Dict

def get_analysis_prompt(template_data: Dict, variables: Dict) -> str:
    prompt_template = template_data.get("instrucoes_prompt", "")
    
    class SafeDict(dict):
        def __missing__(self, key):
            return '{' + key + '}'
            
    safe_vars = SafeDict(variables)
    
    try:
        return prompt_template.format_map(safe_vars)
    except Exception:
        return prompt_template
