FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN ollama serve & sleep 5 && ollama pull phi3

EXPOSE 5000

CMD ollama serve & sleep 5 && python app.py