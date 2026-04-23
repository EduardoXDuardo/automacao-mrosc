import os
import time
import base64
import shutil
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

from backend.automacao import MROSCAutomator
from frontend.state import NOMES_ESTADOS, reset_state, safe_rerun
from frontend.components import render_section_header, render_terminal, render_divider


def render_manual_mode(template_data: dict, variables: dict, limite: int):
    """Renderiza o modo de execução manual com logs laterais."""
    template_nome = template_data.get("nome", "Sem nome")

    _, col_stop = st.columns([4, 1])
    with col_stop:
        if st.button("🛑  Parar", use_container_width=True, type="secondary"):
            reset_state()
            safe_rerun()

    render_divider()

    # Inicializar automator e buscar links
    if not st.session_state.automator:
        st.session_state.automator = MROSCAutomator(template_data=template_data, variables=variables, limit=limite)
        with st.spinner("Realizando buscas na internet... (Aguarde)"):
            st.session_state.links = st.session_state.automator.searcher.collect_links()
        st.session_state.manual_step = "next"
        safe_rerun()

    automator = st.session_state.automator
    links = st.session_state.links
    idx = st.session_state.current_idx
    total = len(links)

    # Fim da lista
    if idx >= total:
        _render_completed(automator, total)
        return

    # Layout: conteúdo à esquerda, logs à direita
    col_main, col_logs = st.columns([2.5, 1])
    
    with col_main:
        render_section_header("🔬", "Modo Manual — Revisão de Documentos")
        
        st.progress((idx) / total if total > 0 else 0)
        st.markdown(f'<span class="status-chip running">● Link {idx + 1} de {total}</span>', unsafe_allow_html=True)
        st.markdown("")
        
        url = links[idx]
        
        if st.session_state.manual_step == "next":
            st.session_state.manual_step = "analyzing"
            safe_rerun()

        if st.session_state.manual_step == "analyzing":
            _process_document(automator, url)

        if st.session_state.manual_step == "waiting":
            _render_document_review(
                url,
                st.session_state.current_temp_path,
                st.session_state.current_analysis,
                automator, idx, total
            )

    with col_logs:
        render_section_header("📋", "Logs em Tempo Real")
        log_path = "logs/automacao.log"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-50:]
                if lines:
                    st.markdown(render_terminal(lines, "Log de Execução"), unsafe_allow_html=True)
                else:
                    st.info("Log vazio.")
        else:
            st.info("Nenhum log gerado ainda.")


def _process_document(automator, url):
    """Baixa e analisa o documento atual."""
    with st.spinner("Baixando documento e processando com IA..."):
        temp_path = automator.downloader.download(url)
        if not temp_path:
            st.error("Falha ao baixar o arquivo.")
            time.sleep(1)
            st.session_state.current_idx += 1
            st.session_state.manual_step = "next"
            safe_rerun()
        
        st.session_state.current_temp_path = str(temp_path)
        
        parts = automator.processor.get_document_content(temp_path)
        if not parts:
            st.warning("Falha na extração de texto (arquivo vazio ou inválido).")
            time.sleep(1)
            try: temp_path.unlink()
            except Exception: pass
            st.session_state.current_idx += 1
            st.session_state.manual_step = "next"
            safe_rerun()
        
        analysis = automator.processor.analyze(parts, url, automator.estado)
        st.session_state.current_analysis = analysis
        st.session_state.manual_step = "waiting"
        safe_rerun()


def _process_manual_action(action, url, path, analysis, automator):
    """Processa a ação do usuário (aprovar ou pular)."""
    if action == "approve":
        automator.output_manager.process_and_save_document(url, Path(path), analysis)
        st.toast("✅ Documento aprovado e salvo!")
    elif action == "skip":
        st.toast("⏭️ Documento descartado.")
        
    if path and os.path.exists(path):
        try: os.unlink(path)
        except Exception: pass
        
    st.session_state.current_idx += 1
    st.session_state.manual_step = "next"
    safe_rerun()


def _render_document_review(url, path, analysis, automator, idx, total):
    """Renderiza a interface de revisão de documento."""
    # Step indicator
    st.markdown(f'''
    <div class="step-indicator">
        <div class="step-number">{idx + 1}</div>
        <div>
            <div class="step-text">Analisando Documento {idx + 1} de {total}</div>
            <div class="step-subtext">Aguardando sua decisão</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(f"**Fonte:** [{url}]({url})")
    
    act1, act2 = st.columns(2)
    with act1:
        if st.button("✅  Aprovar & Salvar", use_container_width=True, type="primary", key=f"btn_approve_{idx}"):
            _process_manual_action("approve", url, path, analysis, automator)
    with act2:
        if st.button("⏭️  Pular / Descartar", use_container_width=True, type="secondary", key=f"btn_skip_{idx}"):
            _process_manual_action("skip", url, path, analysis, automator)

    render_divider()
    
    c_doc, c_ia = st.columns([1.4, 1])
    with c_doc:
        st.markdown('<div class="panel-header"><span>📄</span> Visualização do Documento</div>', unsafe_allow_html=True)
        try:
            if path.endswith(".html"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    components.html(
                        f"<div style='height:600px;padding:15px;overflow-y:auto;background:#fff;color:#1e293b;font-family:Inter,sans-serif;font-size:14px;'>{content}</div>",
                        height=600, scrolling=True
                    )
            elif path.endswith(".pdf"):
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600" style="border:none;border-radius:8px;"></iframe>',
                    unsafe_allow_html=True
                )
            else:
                st.info(f"Arquivo `{path}` baixado. Formato não renderizável.")
        except Exception as e:
            st.error(f"Erro ao carregar visualização: {e}")

    with c_ia:
        st.markdown('<div class="panel-header"><span>🤖</span> Análise da IA</div>', unsafe_allow_html=True)
        with st.container(height=600):
            if isinstance(analysis, dict):
                is_rel = analysis.get("relevante")
                if is_rel:
                    st.markdown('<div class="badge-relevante yes">✅ RELEVANTE</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-relevante no">❌ NÃO RELEVANTE</div>', unsafe_allow_html=True)
                st.markdown("")
                st.json(analysis, expanded=True)
            else:
                st.error("Falha na análise ou JSON inválido.")


def _render_completed(automator, total):
    """Renderiza a tela de conclusão do modo manual."""
    st.markdown('<span class="status-chip done">● Concluído</span>', unsafe_allow_html=True)
    st.success(f"Fim da lista! **{total}** documentos processados.")
    automator.output_manager.save_excel(incremental=False)
    
    base_dir = automator.output_manager.base_dir
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
    
    if st.button("🏁  Concluir Processo", type="primary"):
        reset_state()
        safe_rerun()
    st.stop()
