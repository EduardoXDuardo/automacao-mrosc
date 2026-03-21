FROM python:3.11-slim

# Evita buffering do Python - logs aparecem imediatamente
ENV PYTHONUNBUFFERED=1

# Instalar dependências do sistema operacional necessárias
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos de dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código fonte
COPY . .

# Expor a porta do Streamlit (UI)
EXPOSE 8501

# Healthcheck para monitoramento do container
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando default: Rodar a Interface de Usuário (Streamlit)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
