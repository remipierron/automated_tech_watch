# TechWatch — single image, used by both the scheduler and dashboard services
# (see docker-compose.yml). Keep it slim: no lxml/bs4 system deps required,
# feedparser and BeautifulSoup both work with the stdlib parser.
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p storage

# Default: run the daily scheduler. The dashboard service overrides this
# command in docker-compose.yml.
CMD ["python", "scheduler.py"]
