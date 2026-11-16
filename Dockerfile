FROM python:3.13.17-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1


COPY requirements.txt .
RUN pip install -r requirements.txt


COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]



# docker run --rm -p 8501:8501 --env-file .env pdf-rag