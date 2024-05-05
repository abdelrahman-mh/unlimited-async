FROM python:slim

# Install 'time' from apt repo
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        time && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME /app

CMD ["tail", "-f", "/dev/null"]
