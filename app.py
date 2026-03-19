import streamlit as st
import os
from config import logger 

st.set_page_config(page_title="Automação MROSC", layout="centered")

st.title("Automação MROSC - Busca e Análise")
st.markdown("Interface para executar a busca e extração de documentos do Marco Regulatório.")

st.sidebar.header("Configurações da Busca")
estado = st.sidebar.selectbox("Estado alvo (UF)", [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
])
limite = st.sidebar.slider("Limite de resultados por query", 1, 50, 10)

if st.button("Iniciar Automação"):
    st.info(f"Iniciando busca para {estado}...")
    
    log_output = st.empty()
    
    
    try:
        from automacao_mrosc import MROSCAutomator
        logger.info(f"Iniciada a run pela UI para o estado: {estado}")
        
        nomes_estados = {
            "AC": "Acre",
            "AL": "Alagoas",
            "AP": "Amapá",
            "AM": "Amazonas",
            "BA": "Bahia",
            "CE": "Ceará",
            "DF": "Distrito Federal",
            "ES": "Espírito Santo",
            "GO": "Goiás",
            "MA": "Maranhão",
            "MT": "Mato Grosso",
            "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais",
            "PA": "Pará",
            "PB": "Paraíba",
            "PR": "Paraná",
            "PE": "Pernambuco",
            "PI": "Piauí",
            "RJ": "Rio de Janeiro",
            "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul",
            "RO": "Rondônia",
            "RR": "Roraima",
            "SC": "Santa Catarina",
            "SP": "São Paulo",
            "SE": "Sergipe",
            "TO": "Tocantins"
        }
        nome_estado = nomes_estados.get(estado, estado)
        
        automator = MROSCAutomator(uf=estado, estado=nome_estado)
        automator.run() 
        
        st.success(f"Automação concluída com sucesso para {estado}! Os arquivos estão na pasta output.")
    except Exception as e:
        logger.error(f"Erro na execução da UI: {e}")
        st.error(f"Ocorreu um erro: {e}")

# Visualizador de Logs
st.markdown("---")
st.subheader("📝 Últimos Logs")
if os.path.exists("logs/automacao.log"):
    with open("logs/automacao.log", "r", encoding="utf-8") as f:
        lines = f.readlines()[-15:]
        st.code("".join(lines), language="text")
else:
    st.write("Nenhum log gerado ainda.")
