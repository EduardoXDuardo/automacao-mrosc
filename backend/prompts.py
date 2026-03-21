def get_analysis_prompt(estado: str) -> str:
    return f"""
        Você está analisando documentos oficiais do estado de {estado} relacionados às parcerias entre o poder público e Organizações da Sociedade Civil (MROSC – Lei 13.019/2014).

        Seu objetivo é identificar documentos RELEVANTES para análise de capacidades estatais.

        Critérios de relevância:
        - Regulamentação da Lei 13.019 (decretos, leis, portarias)
        - Instrumentos operacionais (manuais, guias, fluxos, sistemas)
        - Evidências de gestão de parcerias (monitoramento, avaliação, prestação de contas)
        - Estruturas institucionais (comissões, órgãos responsáveis, sistemas)
        - Procedimentos administrativos (chamamento público, seleção, execução)

        Classifique como NÃO relevante:
        - Notícias genéricas
        - Conteúdos jornalísticos sem detalhamento técnico
        - Menções superficiais à lei sem conteúdo operacional

        Para documentos relevantes, extraia:

        Retorne APENAS JSON:

        {{
            "relevante": true | false,
            "tipo": "Decreto" | "Lei" | "Portaria" | "Resolução" | "Manual" | "Guia" | "Sistema" | "Página institucional" | "Notícia",
            "titulo": "Título oficial completo do documento",
            "ano": "Ano do documento (se identificado)",
            "estado": "{estado}",
            "dimensao": "Normativa" | "Operacional" | "Governança" | "Controle" | "Capacitação",
            "instrumento_mrosc": "Regulamentação" | "Execução" | "Monitoramento" | "Prestação de contas" | "Chamamento público" | "Outro",
            "consideracao": "Resumo técnico objetivo destacando o que o documento regula ou operacionaliza",
            "tem_fluxo_operacional": true | false,
            "tem_instrumentos_gestao": true | false,
            "id_unico": "ID curto padronizado (ex: dec-61981-sp)",
            "nome_arquivo_sugerido": "Nome curto padronizado (ex: Decreto_61981_SP)"
        }}
    """
