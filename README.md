# Business AI Agent

Business AI Agent es una aplicación modular para asistir pequeños negocios con un chatbot inteligente, gestión de clientes, productos, pedidos y facturación simulada.

## Arquitectura

- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI + Python
- IA/RAG: LangChain + ChromaDB + documentos PDF/CSV
- Base de datos: PostgreSQL listo para migrar desde SQLite
- Despliegue: OCI con Docker Compose

## Requisitos

- Python 3.11+
- Node.js 20+
- Docker (opcional)

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Pruebas

```bash
cd backend
pytest
```

## Despliegue en OCI

1. Crear una instancia de Ubuntu en OCI.
2. Instalar Docker y Docker Compose.
3. Subir este proyecto y ejecutar:

```bash
docker compose up --build -d
```

## Despliegue en VPS/Apache (Producción)

Para desplegar en un servidor VPS con Apache, consulta la **[Guía de Deployment](DEPLOYMENT.md)** que incluye:

- Configuración de GitHub Actions para CI/CD
- Workflows para deployment manual y automático
- Script de validación local (`deploy.sh`)
- Setup del servidor VPS
- Variables de entorno y configuración de Apache/FastAPI

**Quick start (5 minutos):**
```bash
# 1. En tu VPS, ejecutar:
sudo bash vps-setup.sh

# 2. En GitHub, agregar secrets (ver GITHUB_SECRETS.md)

# 3. Ir a GitHub Actions → Deploy to VPS (Manual) → Run workflow
```

Consulta **[QUICKSTART.md](QUICKSTART.md)** para una guía paso a paso.

## Endpoints principales

- GET /health
- POST /api/v1/auth/register
- GET /api/v1/products
- POST /api/v1/customers
- POST /api/v1/orders
- GET /api/v1/orders
- GET /api/v1/billing/invoice/{order_id}
- POST /api/v1/chat

## Notas

La facturación es simulada en esta primera versión y está preparada para crecer hacia facturación electrónica y WhatsApp.
