import streamlit as st
import json
from frontend.components import render_section_header, render_divider
from frontend.state import reset_state, safe_rerun

def render_template_editor():
    _, col_stop = st.columns([4, 1])
    with col_stop:
        if st.button("⬅️  Voltar", use_container_width=True, type="secondary"):
            reset_state()
            safe_rerun()

    render_section_header("📝", "Criar/Editar Template JSON")
    st.markdown("Preencha os campos abaixo para gerar um arquivo de configuração personalizado. Quando terminar, clique em **Baixar** e use o arquivo no painel lateral.")
    
    uploaded_edit = st.file_uploader("📂 Importar Template Existente para Edição (Opcional)", type=["json"], key="template_edit_uploader")
    
    default_vals = {
        "nome": "Meu Template",
        "descricao": "Template de busca personalizado.",
        "sites": "{uf}.gov.br\nportal.{uf}.gov.br",
        "blacklist": "jusbrasil.com.br\nwikipedia.org\njus.com.br\ngoverno.xyz",
        "vars": "estado|Nome do Estado (Ex: Bahia)\nuf|Sigla do Estado (Ex: BA)",
        "queries": "\"Lei 13.019\" {estado}\nmarco regulatório organizações sociedade civil {estado}\nmanual parcerias OSC {estado}",
        "prompt": "Você analisará documentos do estado de {estado}. Extraia informações em JSON com base nos campos definidos.",
        "schema": "titulo|str|O título do documento\nresumo|str|Resumo objetivo do conteúdo\ndata|str_opt|A data se presente\nrelevante|bool|Se é importante para o tema principal"
    }
    
    if uploaded_edit is not None:
        try:
            content = uploaded_edit.getvalue().decode("utf-8-sig")
            data = json.loads(content)
            default_vals["nome"] = data.get("nome", default_vals["nome"])
            default_vals["descricao"] = data.get("descricao", default_vals["descricao"])
            default_vals["sites"] = "\n".join(data.get("sites_especificos", [])) or default_vals["sites"]
            default_vals["blacklist"] = "\n".join(data.get("blacklist", [])) or default_vals["blacklist"]
            
            vars_list = [f"{v['nome']}|{v.get('descricao', v['nome'])}" for v in data.get("variaveis_esperadas", [])]
            if vars_list: default_vals["vars"] = "\n".join(vars_list)
            
            if data.get("queries"): default_vals["queries"] = "\n".join(data.get("queries"))
            default_vals["prompt"] = data.get("instrucoes_prompt", default_vals["prompt"])
            
            schema_list = [f"{s['nome']}|{s.get('tipo', 'str')}|{s.get('descricao', '')}" for s in data.get("schema_de_saida", [])]
            if schema_list: default_vals["schema"] = "\n".join(schema_list)
        except Exception:
            st.error("Erro ao ler JSON inválido.")
    
    with st.form("template_form"):
        st.subheader("1. Informações Básicas")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Template", value=default_vals["nome"])
        with col2:
            descricao = st.text_input("Descrição", value=default_vals["descricao"])
        
        st.subheader("2. Configuração de Buscas")
        st.markdown("Adicione os sites específicos para busca (um por linha). Use `{variavel}` se desejar injetar uma variável depois.")
        sites_especificos = st.text_area("Sites Específicos (Opcional)", value=default_vals["sites"], height=100)
        
        st.markdown("Lista de domínios ou caminhos a serem ignorados (um por linha):")
        blacklist = st.text_area("Blacklist", value=default_vals["blacklist"], height=100)
        
        st.subheader("3. Parâmetros e Variáveis")
        st.markdown("Quais variáveis o usuário deve preencher na tela? (Formato: `nome_variavel|Descrição bonita`, uma por linha). **Exemplo:** `uf|Sigla do Estado` ou `municipio|Nome da Cidade`")
        variaveis = st.text_area("Variáveis Esperadas", value=default_vals["vars"], height=100)
        
        st.subheader("4. Queries (Consultas)")
        st.markdown("Digite uma query por linha. Use `{nome_variavel}` para injetar o valor dinamicamente, como `{estado}`.")
        queries = st.text_area("Consultas de Busca", value=default_vals["queries"], height=200)
        
        st.subheader("5. IA e Extração (Prompts e Output Schema)")
        st.markdown("Instruções que serão passadas para o LLM. Seja claro e objetivo. Use variáveis se necessário.")
        prompt = st.text_area("Instruções Base (Prompt)", value=default_vals["prompt"], height=200)
        
        st.markdown("Quais colunas/informações você quer extrair de cada link? (Formato: `chave_json|tipo|Descrição`, uma por linha). Tipos suportados: `str`, `str_opt`, `bool`, `bool_opt`")
        schema_out = st.text_area("Campos de Saída (Output Schema)", value=default_vals["schema"], height=150)
        
        submitted = st.form_submit_button("💾 Gerar Arquivo JSON", type="primary")
        
    if submitted:
        try:
            # Process values
            def parse_lines(text):
                return [t.strip() for t in text.split("\n") if t.strip()]
            
            var_list = []
            for v in parse_lines(variaveis):
                parts = v.split("|")
                var_list.append({"nome": parts[0].strip(), "descricao": parts[1].strip() if len(parts) > 1 else parts[0]})
                
            schema_list = []
            for s in parse_lines(schema_out):
                parts = s.split("|")
                schema_list.append({
                    "nome": parts[0].strip(),
                    "tipo": parts[1].strip() if len(parts) > 1 else "str",
                    "descricao": parts[2].strip() if len(parts) > 2 else ""
                })
                
            template_dict = {
                "nome": nome,
                "descricao": descricao,
                "variaveis_esperadas": var_list,
                "blacklist": parse_lines(blacklist),
                "sites_especificos": parse_lines(sites_especificos),
                "queries": parse_lines(queries),
                "instrucoes_prompt": prompt,
                "schema_de_saida": schema_list
            }
            
            json_blob = json.dumps(template_dict, ensure_ascii=False, indent=2)
            
            st.success("✅ JSON gerado com sucesso!")
            st.download_button(
                label="⬇️ Baixar template_custom.json",
                data=json_blob,
                file_name="template_custom.json",
                mime="application/json"
            )
        except Exception as e:
            st.error(f"Erro ao processar formatação: {e}")
