import os
import base64
import shutil
import streamlit as st
import streamlit.components.v1 as components

from backend.config import logger
from backend.automacao import MROSCAutomator
from frontend.state import NOMES_ESTADOS, reset_state, safe_rerun
from frontend.components import render_section_header, render_terminal, render_divider


def render_auto_mode(template_data: dict, variables: dict, limite: int):
    """Renderiza o modo de execução automática com logs sempre visíveis na lateral."""
    template_nome = template_data.get("nome", "Sem Nome")

    _, col_stop = st.columns([4, 1])
    with col_stop:
        if st.button("🛑  Parar", use_container_width=True, type="secondary"):
            reset_state()
            safe_rerun()

    render_divider()
    
    col_main, col_logs = st.columns([2.5, 1])

    with col_main:
        render_section_header("⚡", "Execução Automática em Andamento")
        st.markdown('<span class="status-chip running">● Processando</span>', unsafe_allow_html=True)
        st.markdown("")
        
        m1, m2, m3 = st.columns(3)
        metric_total = m1.empty()
        metric_current = m2.empty()
        metric_saved = m3.empty()
        
        metric_total.metric("🔗 Links Encontrados", "0")
        metric_current.metric("⏳ Processando Agora", "0 / 0")
        metric_saved.metric("💾 Documentos Salvos", "0")
        
        render_divider()
        progress_bar = st.progress(0)
        status_text = st.empty()
        render_divider()
        
        c_viewer, c_ia = st.columns(2)
        with c_viewer:
            st.markdown('<div class="panel-header"><span>📄</span> Último Arquivo</div>', unsafe_allow_html=True)
            viewer_placeholder = st.empty()
        with c_ia:
            st.markdown('<div class="panel-header"><span>🤖</span> Análise da IA</div>', unsafe_allow_html=True)
            ai_placeholder = st.empty()

    with col_logs:
        render_section_header("📋", "Logs em Tempo Real")
        log_placeholder = st.empty()
        _update_log_panel(log_placeholder)

    if not st.session_state.automator:
        st.session_state.automator = MROSCAutomator(template_data=template_data, variables=variables, limit=limite)

    def automator_callback(event):
        try:
            _handle_event(event, metric_total, metric_current, metric_saved,
                          progress_bar, status_text, viewer_placeholder, ai_placeholder)
            _update_log_panel(log_placeholder)
        except Exception as err:
            logger.debug(f"[UI_CALLBACK] Erro não-fatal: {err}")

    st.session_state.automator.run(ui_callback=automator_callback)
    
    _render_post_execution()


def _handle_event(event, metric_total, metric_current, metric_saved,
                   progress_bar, status_text, viewer_placeholder, ai_placeholder):
    """Processa um evento do callback da automação."""
    etype = event["type"]
    
    if etype == "status":
        status_text.info(f"**Status:** {event['message']}")
    elif etype == "links_found":
        metric_total.metric("🔗 Links Encontrados", event['total'])
        status_text.success(f"Busca finalizada. **{event['total']}** links encontrados.")
    elif etype == "downloading":
        pct = event["current"] / event["total"]
        progress_bar.progress(pct)
        metric_current.metric("⏳ Processando Agora", f"{event['current']} / {event['total']}")
        status_text.warning(f"**Baixando:** {event['url']}")
        ai_placeholder.info("Aguardando IA...")
        viewer_placeholder.info("Baixando arquivo...")
    elif etype == "downloaded":
        _render_downloaded(event, viewer_placeholder)
    elif etype == "analysis_done":
        _render_analysis(event, ai_placeholder)
    elif etype == "saved":
        saved = len(st.session_state.automator.output_manager.results)
        metric_saved.metric("💾 Documentos Salvos", f"{saved}")
    elif etype == "done":
        progress_bar.progress(1.0)
        status_text.success(f"**Finalizado!** {event['results_count']} docs salvos.")


def _render_downloaded(event, viewer_placeholder):
    """Renderiza o arquivo baixado no viewer."""
    path = event["path"]
    try:
        viewer_placeholder.empty()
        if path.endswith(".html"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                with viewer_placeholder.container():
                    components.html(
                        f"<div style='height:500px;padding:15px;overflow-y:auto;background:#fff;color:#1e293b;font-family:Inter,sans-serif;font-size:13px;border-radius:8px;'>{content}</div>",
                        height=520, scrolling=False
                    )
        elif path.endswith(".pdf"):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            viewer_placeholder.markdown(
                f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="520" style="border:none;border-radius:8px;"></iframe>',
                unsafe_allow_html=True
            )
        else:
            viewer_placeholder.info(f"Arquivo recebido: {path}")
    except Exception as e:
        viewer_placeholder.error(f"Não foi possível visualizar: {e}")


def _render_analysis(event, ai_placeholder):
    """Renderiza resultado da análise da IA."""
    analysis = event.get("analysis")
    ai_placeholder.empty()
    with ai_placeholder.container():
        if isinstance(analysis, dict):
            if analysis.get("relevante"):
                st.success(f"**Relevante:** {analysis.get('titulo', 'Sem título')}")
            else:
                st.error("**Não Relevante:** Descartado.")
            st.json(analysis, expanded=True)
        else:
            st.warning("Falha na análise.")


def _update_log_panel(log_placeholder):
    """Atualiza o painel de logs na lateral."""
    if os.path.exists("logs/automacao.log"):
        with open("logs/automacao.log", "r", encoding="utf-8") as f:
            lines = f.readlines()[-50:]
            log_placeholder.markdown(render_terminal(lines, "Log de Execução"), unsafe_allow_html=True)


def _render_post_execution():
    """Renderiza a seção pós-execução com download e botão de finalizar."""
    render_divider()
    st.markdown('<span class="status-chip done">● Concluído</span>', unsafe_allow_html=True)
    st.success("Automação em Lote concluída com sucesso!")
    
    base_dir = st.session_state.automator.output_manager.base_dir
    if base_dir and os.path.exists(base_dir):
        zip_path = str(base_dir) + ".zip"
        if not os.path.exists(zip_path):
            shutil.make_archive(str(base_dir), 'zip', str(base_dir))
        
        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦  Baixar Resultados (.zip)",
                data=f,
                file_name=os.path.basename(zip_path),
                mime="application/zip"
            )

    if st.button("🏁  Finalizar e Voltar", key="btn_finalizar", type="primary"):
        reset_state()
        safe_rerun()
