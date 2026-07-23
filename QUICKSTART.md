# Quick Start Guide - Flash-Bites Deployment

## Checklist de Configuración

### ✅ Paso 1: Preparar el repositorio

Clonar el proyecto:

```bash
git clone https://github.com/Estefani-Cometa/Flash-Bites.git

cd Flash-Bites
```

La estructura esperada:

```env
Flash-Bites/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── Dockerfile
└── railway.json
```

---

## Deployment en Railway

## ✅ Paso 2: Crear servicios en Railway

Crear dos servicios:

```env
Flash-Bites Backend
Flash-Bites Frontend
```

---

### Backend Configuration

## Source

Repositorio:

```env
Estefani-Cometa/Flash-Bites
```

Root Directory:

```bash
/
```

Dockerfile:

```bash
/Dockerfile
```

Puerto:

```bash
8000
```

Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Variables:

```env
SECRET_KEY=tu_clave_segura

OPENAI_API_KEY=tu_api_key

DATABASE_URL=sqlite:///./app.db
```

URL generada:

```bash
https://flash-bites-production.up.railway.app
```

---

## Frontend Configuration

---

 Source

Repositorio:

```bash
Estefani-Cometa/Flash-Bites
```

Root Directory:

```bash
/frontend
```

Dockerfile:

```bash
/frontend/Dockerfile
```

Variable necesaria:

```env
VITE_API_URL=https://flash-bites-production.up.railway.app/api/v1
```

Puerto:

```bash
8080
```

URL generada:

```bash
https://frontend-production-bb6a.up.railway.app
```

---

## Deployment automático

Railway realizará deploy automáticamente al hacer:

```bash
git add .
git commit -m "Update application"
git push origin main
```

Proceso:

```bash
GitHub
   ↓
Railway
   ↓
Docker Build
   ↓
Deploy Container
   ↓
Production
```

Tiempo aproximado:

```bash
1-3 minutos
```

---

## Verificar que funciona

## Backend Health

Abrir:

```bash
https://flash-bites-production.up.railway.app/docs
```

Debe mostrar:

```bash
FastAPI Swagger UI
```

---

## Probar productos

Abrir:

```bash
https://flash-bites-production.up.railway.app/api/v1/products
```

Respuesta esperada:

```json
{
  "items": []
}
```

---

## Frontend

Abrir:

```bash
https://frontend-production-bb6a.up.railway.app
```

Debe permitir:

✅ Ver interfaz  
✅ Cargar productos  
✅ Crear cuenta demo  
✅ Enviar mensajes al agente IA  
✅ Crear pedidos  

---

## Troubleshooting

## Error 404 en API desde frontend

Síntoma:

```bash
GET frontend-url/products 404
```

Solución:

Verificar:

```env
VITE_API_URL=https://flash-bites-production.up.railway.app/api/v1
```

Después hacer nuevo deploy porque Vite incorpora variables durante el build.

---

## Backend no inicia

Revisar logs Railway:

```bash
Backend
→ Deployments
→ View Logs
```

Debe aparecer:

```bash
Uvicorn running on http://0.0.0.0:8000
```

---

## Frontend no conecta con backend

Verificar en navegador:

```env
F12
→ Network
```

La petición correcta debe ser:

```env
https://flash-bites-production.up.railway.app/api/v1/...
```

No:

```env
https://frontend-production-bb6a.up.railway.app/...
```

---

## Variables importantes

## Backend

```env
SECRET_KEY=
OPENAI_API_KEY=
DATABASE_URL=
```

---

### ""Frontend"

```env
VITE_API_URL=
```

---

## Próximas mejoras

- Migrar SQLite a PostgreSQL Railway
- Configurar dominios personalizados
- Añadir almacenamiento persistente
- Mejorar monitoreo
- Integrar WhatsApp Business API

---

## Documentación adicional

- `README.md` → Información general del proyecto
- `DEPLOYMENT.md` → Detalles técnicos de despliegue
- `QUICKSTART.md` → Inicio rápido

---

¡Flash-Bites está desplegado correctamente en Railway! 🚀
