# Distribution stage
FROM python:3.10-slim as backend

# Container source code
COPY ./backend /backend
WORKDIR /backend
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
# CMD ["gunicorn", "main:app", "--workers=2", "--worker-class=uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:80"]


# Local stage
FROM backend as local-backend
# System dependecies
RUN apt update \
    && apt install -y --no-install-recommends mariadb-client \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Container source code
COPY docker/backend/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Add entry point
ENTRYPOINT ["docker-entrypoint.sh"]
