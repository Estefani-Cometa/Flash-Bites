FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /app app

WORKDIR /app

RUN chown -R app:app /app && chmod 755 /app

COPY requirements.txt ./

# Install build deps, install python deps, then remove build deps to keep image small and reduce attack surface
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential=12.9 gcc=4:12.2.0-3 libpq-dev=15.* ca-certificates=20240110 \
	&& pip install --no-cache-dir --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r requirements.txt \
	&& apt-get purge -y --auto-remove build-essential gcc \
	&& rm -rf /var/lib/apt/lists/* /root/.cache/pip /tmp/*

COPY --chown=app:app . .

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

