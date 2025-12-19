FROM tiangolo/uvicorn-gunicorn:python3.11-slim

ENV HOME=/home/fast \
    APP_HOME=/home/fast/app \
    PYTHONPATH="$PYTHONPATH:/home/fast" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p $APP_HOME \
 && groupadd -r fast \
 && useradd -r -g fast fast

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install -r requirements.txt --no-cache-dir \
 && rm requirements.txt \
 && rm -rf /root/.cache/pip

COPY . .

RUN chown -R fast:fast $APP_HOME

USER fast

EXPOSE 8000
