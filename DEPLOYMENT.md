# Deployment Guide - Flash-Bites Railway

## Overview

Flash-Bites utiliza una arquitectura moderna desplegada en Railway con servicios separados:

* **Frontend:** React + Vite + Tailwind CSS
* **Backend:** FastAPI + Python
* **IA/RAG:** LangChain + ChromaDB
* **Base de datos:** SQLite actualmente, preparada para PostgreSQL
* **Contenedores:** Docker
* **CI/CD:** GitHub Actions + Railway Auto Deploy

La aplicación está dividida en dos servicios independientes:

| Servicio | Tecnología   | Plataforma |
| -------- | ------------ | ---------- |
| Frontend | React + Vite | Railway    |
| Backend  | FastAPI      | Railway    |

---

## Production URLs

## Frontend

Aplicación web:

```bash
https://frontend-production-bb6a.up.railway.app
```

---

## Backend API

API principal:

```bash
https://flash-bites-production.up.railway.app
```

Swagger:

```bash
https://flash-bites-production.up.railway.app/docs
```

OpenAPI:

```bash
https://flash-bites-production.up.railway.app/openapi.json
```

---

## Repository Structure

```bash
Flash-Bites/

├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
│
└── .github/
    └── workflows/
```

---

## Railway Configuration

## Backend Service

### Root Directory

```bash
backend
```

### Dockerfile

```bash
backend/Dockerfile
```

### Port

Railway asigna automáticamente la variable:

```bash
PORT
```

La aplicación debe escuchar:

```bash
0.0.0.0:$PORT
```

---

### Start Command

Ejemplo:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Backend Environment Variables

Configurar en Railway:

```bash
SECRET_KEY=clave_segura
OPENAI_API_KEY=tu_api_key
DATABASE_URL=sqlite:///./app.db
```

Opcionales:

```bash
CHROMA_PERSIST_DIRECTORY=./data/chroma
DOCUMENTS_DIRECTORY=./documents
```

---

## Frontend Service

```bash
 Railway Configuration
```

## "Root Directory"

```bash
frontend
```

---

## "Dockerfile"

```bash
frontend/Dockerfile
```

---

## Build Command

```bash
npm run build
```

---

## "Start Command"

```bash
npm run start
```

---

## Frontend Environment Variables

Configurar en Railway:

```bash
VITE_API_URL=https://flash-bites-production.up.railway.app/api/v1
```

Esta variable permite que React se comunique con FastAPI.

---

## "Deployment Process"

## Automatic Deployment

Cada cambio enviado a la rama principal activa el despliegue:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway ejecutará automáticamente:

1. Detectar cambios en GitHub
2. Construir la imagen Docker
3. Instalar dependencias
4. Ejecutar build
5. Crear nuevo contenedor
6. Reiniciar servicio
7. Publicar nueva versión

---

## GitHub Actions

El repositorio cuenta con validaciones automáticas.

## CI Workflow

Ejecuta:

### Backend

* Instalación de dependencias
* Validación FastAPI
* Ejecución de pruebas

### "Frontend"

* Instalación npm
* Build Vite
* Validación React

Ejemplo:

```bash
Flash-Bites CI - Pruebas y validación
```

---

## Docker Deployment

## Backend Docker

El backend utiliza Docker para crear un entorno reproducible.

Proceso:

```bash
Dockerfile
      |
      ↓
Python Environment
      |
      ↓
FastAPI Application
      |
      ↓
Railway Container
```

---

## Frontend Docker

Proceso:

```bash
Node.js
   |
   ↓
npm install
   |
   ↓
npm run build
   |
   ↓
serve dist
   |
   ↓
Railway Container
```

---

## "API Endpoints"

## Health Check

```bash
GET /health
```

Respuesta:

```json
{
  "status":"ok"
}
```

---

## Authentication

Registrar usuario:

```bash
POST /api/v1/auth/register
```

---

## Products

Obtener productos:

```bash
GET /api/v1/products
```

Ejemplo:

```json
{
  "items":[
    {
      "id":"prod-1",
      "name":"Café Premium",
      "price":4.5
    }
  ]
}
```

---

## Customers

Crear cliente:

```env
POST /api/v1/customers
```

---

## Orders

Crear pedido:

```bash
POST /api/v1/orders
```

Consultar pedidos:

```bash
GET /api/v1/orders
```

---

## Billing

Factura simulada:

```bash
GET /api/v1/billing/invoice/{order_id}
```

---

## AI Chat

Enviar mensaje:

```bash
POST /api/v1/chat
```

---

## Troubleshooting

## Frontend muestra error 404 en API

Verificar:

```bash
VITE_API_URL
```

Debe ser:

```env
https://flash-bites-production.up.railway.app/api/v1
```

No:

```bash
https://frontend-production-bb6a.up.railway.app
```

---

## Backend no responde

Revisar logs Railway:

```bash
Backend Service
→ Deployments
→ Logs
```

Debe aparecer:

```bash
Application startup complete
```

---

## Error de puerto

FastAPI debe escuchar:

Correcto:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Incorrecto:

```bash
--port 8000
```

---

## Error Docker Build

Verificar:

* Dockerfile correcto
* requirements.txt actualizado
* versión Python compatible

---

## Local Development

## "Backend"

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Disponible:

```bash
http://localhost:8000/docs
```

### ""Frontend"

```bash
cd frontend

npm install

npm run dev
```

Disponible:

```bash
http://localhost:5173
```

---

## Migration to PostgreSQL

Actualmente:

```bash
SQLite
```

Preparado para:

```bash
PostgreSQL
```

Cambiar:

```bash
DATABASE_URL
```

Ejemplo:

```bash
postgresql://user:password@host/database
```

---

## Future Improvements

Planeado:

* Facturación electrónica
* Integración WhatsApp Business
* PostgreSQL producción
* Sistema de usuarios avanzado
* Dashboard administrativo
* Mejoras del agente IA
* Integración de pagos

---

## Last Updated

2026-07-23
