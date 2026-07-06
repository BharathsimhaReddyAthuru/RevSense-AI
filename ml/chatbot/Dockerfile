# Dockerfile for building an isolated, reproducible environment for the industry-grade chatbot
# Uses Python 3.11 (compatible with PyTorch wheels) and installs CPU PyTorch first to avoid resolution issues

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       git \
       cmake \
       libgomp1 \
       libsndfile1 \
       wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for efficient caching
COPY ml/chatbot/requirements-chatbot.txt /app/requirements-chatbot.txt

RUN python -m pip install --upgrade pip setuptools wheel

# Install CPU PyTorch wheels from official index to satisfy sentence-transformers dependency
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch

# Install the rest of the Python dependencies
RUN pip install -r /app/requirements-chatbot.txt

# Copy repository
COPY . /app

# Ensure ml package is importable
ENV PYTHONPATH=/app/ml

EXPOSE 8080

# Default entry: run industry app (change command to run lightweight app if desired)
CMD ["python", "ml/chatbot/app_industry.py"]
