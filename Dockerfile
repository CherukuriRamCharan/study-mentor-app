FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    zstd \
    && curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ollama serve & sleep 10 && ollama pull phi3 && python app.py