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

        Para documentos relevantes, extraia todas as informações solicitadas pelo schema de resposta.
        Retorne APENAS o JSON conforme o schema fornecido.
    """
