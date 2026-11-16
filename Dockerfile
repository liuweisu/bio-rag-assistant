FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY corpus ./corpus
COPY eval ./eval
RUN pip install --no-cache-dir . && useradd --create-home app
USER app

# Pass the key at run time, never bake it into the image:
#   docker run -p 8000:8000 -e ANTHROPIC_API_KEY bio-rag-assistant
ENV BIORAG_MODEL=claude-opus-5-5 \
    BIORAG_CORPUS=/app/corpus \
    BIORAG_EVAL_DIR=/app/eval
EXPOSE 8000
CMD ["uvicorn", "biorag.api:app", "--host", "0.0.0.0", "--port", "8000"]
