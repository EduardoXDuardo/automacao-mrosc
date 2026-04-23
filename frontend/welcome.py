import os
import streamlit as st
from frontend.state import safe_rerun
from frontend.components import render_section_header, render_terminal, render_divider


def render_welcome(modo_manual: bool):
    """Renderiza a página idle/welcome com feature cards, botão CTA, e logs laterais."""
    
    # Layout principal: conteúdo à esquerda, logs à direita
    col_main, col_logs = st.columns([2.5, 1])
    
    with col_main:
        st.markdown('''
        <div class="welcome-info">
            <strong>Bem-vindo à Plataforma de Automação & Análise.</strong> Este sistema utiliza Inteligência Artificial para buscar, baixar e classificar automaticamente documentos através de templates modulares. Selecione um template na barra lateral e inicie a automação.
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Busca Inteligente</div>
                <div class="feature-desc">Varredura automática em portais oficiais utilizando suas queries ativas do Template carregado.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">Análise com Gemini AI</div>
                <div class="feature-desc">Cada documento é analisado pela IA que extrai as exatas colunas que você configurar e extrai metadados estruturados.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Relatórios Consolidados</div>
                <div class="feature-desc">Resultados exportados em planilhas XLSX montadas dinamicamente com base nas respostas arquivados.</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("")

        col_btn, _ = st.columns([1, 2])
        with col_btn:
            is_ready = st.session_state.get("template_data") is not None
            if st.button("🚀  Iniciar Automação", use_container_width=True, type="primary", disabled=not is_ready):
                os.makedirs("logs", exist_ok=True)
                if not os.path.exists("logs/automacao.log"):
                    open("logs/automacao.log", "w", encoding="utf-8").close()
                    
                st.session_state.modo_manual = modo_manual
                st.session_state.running_state = "running_manual" if modo_manual else "running_auto"
                safe_rerun()

    with col_logs:
        render_section_header("📋", "Histórico de Logs")
        
        log_path = "logs/automacao.log"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-50:]
                if lines:
                    st.markdown(render_terminal(lines, "automacao.log"), unsafe_allow_html=True)
                else:
                    st.info("Log vazio.")
            
            st.markdown("")
            if st.button("🗑️  Limpar Logs", type="secondary", use_container_width=True):
                open(log_path, "w").close()
                st.rerun()
        else:
            st.info("Nenhum log gerado ainda.")

