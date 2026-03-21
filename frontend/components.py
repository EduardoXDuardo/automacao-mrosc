import os
import streamlit as st


def format_log_html(lines: list[str]) -> str:
    """Formata linhas de log para exibição HTML no terminal visual."""
    log_content = "".join(lines)
    formatted = (
        log_content
        .replace("INFO", "<span class='log-info'>[INFO]</span>")
        .replace("ERROR", "<span class='log-error'>[ERROR]</span>")
        .replace("WARNING", "<span class='log-warning'>[WARNING]</span>")
    )
    return formatted


def render_hero_header():
    """Renderiza o header principal do app com gradiente animado."""
    st.markdown('''
    <div class="hero-header">
        <div class="hero-icon">⚡</div>
        <div class="hero-title">Automação MROSC</div>
        <div class="hero-subtitle">Inteligência Artificial direcionada à análise de documentos e parcerias públicas do Marco Regulatório das OSCs</div>
        <div class="hero-badge">Powered by Gemini AI</div>
    </div>
    ''', unsafe_allow_html=True)


def render_terminal(lines: list[str], title: str = "Automação MROSC") -> str:
    """Retorna HTML de um terminal estilizado macOS-style com logs reversos (mais recentes no topo)."""
    reversed_lines = list(reversed(lines))
    formatted = format_log_html(reversed_lines)
    return f'''
    <div class="terminal-container">
        <div class="terminal-header">
            <span class="terminal-dot red"></span>
            <span class="terminal-dot yellow"></span>
            <span class="terminal-dot green"></span>
            <span class="terminal-title-text">{title}</span>
        </div>
        <div class="terminal-body">{formatted}</div>
    </div>
    '''


def render_section_header(icon: str, title: str):
    """Renderiza um header de seção estilizado com ícone e linha."""
    st.markdown(f'''
    <div class="section-header">
        <span class="section-header-icon">{icon}</span>
        <span class="section-header-title">{title}</span>
        <div class="section-header-line"></div>
    </div>
    ''', unsafe_allow_html=True)


def render_log_panel(placeholder=None, title: str = "Log de Execução", max_lines: int = 50):
    """Renderiza o painel de logs no local dado (ou cria um novo).
    
    Lê o arquivo de log, inverte as linhas (mais recentes no topo),
    e renderiza dentro do terminal macOS-style.
    Retorna o placeholder usado para atualizações futuras.
    """
    if placeholder is None:
        placeholder = st.empty()

    render_section_header("📋", "Logs em Tempo Real")
    
    log_path = "logs/automacao.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-max_lines:]
            if lines:
                placeholder.markdown(render_terminal(lines, title), unsafe_allow_html=True)
            else:
                placeholder.info("Log vazio. Inicie uma automação para gerar registros.")
    else:
        placeholder.info("Nenhum log gerado ainda.")
    
    return placeholder


def render_divider():
    """Renderiza um divisor estilizado."""
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
