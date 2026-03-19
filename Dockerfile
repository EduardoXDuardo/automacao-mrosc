FROM python:3.11-slim

# Instalar dependências do sistema operacional necessárias (Poppler para pdf2image)
RUN apt-get update && apt-get install -y \
    poppler-utils \
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

# Comando default: Rodar a Interface de Usuário (Streamlit)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
