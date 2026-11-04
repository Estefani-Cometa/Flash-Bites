# Contribuir a Flash-Bites

Esta guía describe cómo preparar el entorno, proponer cambios y registrar validaciones para el estado actual del repositorio. Si cambian las dependencias, los comandos o el flujo de CI, actualiza esta guía en el mismo cambio.

## Antes de empezar

- Revisa los Issues y Pull Requests abiertos para evitar duplicar trabajo.
- Delimita el cambio y sus criterios de aceptación antes de editar.
- No incluyas credenciales, archivos `.env`, datos privados, bases de datos locales ni artefactos generados.
- La carpeta `Flash-Bites/` anidada que pueda aparecer en el árbol local no forma parte de este checkout. No la agregues al PR sin confirmar su procedencia.

## Preparar el entorno

Requisitos: Python 3.11 o superior, Node.js 20 o superior y npm.

### Backend

En PowerShell, desde la raíz:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

La API local queda en `http://localhost:8000`; su documentación interactiva, en `http://localhost:8000/docs`.

### Frontend

En otra terminal, desde la raíz:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

Vite inicia normalmente en `http://localhost:5173`. Configura `VITE_API_URL` en `frontend/.env` para que apunte al backend, por ejemplo `http://localhost:8000/api/v1`.

### Docker Compose

Desde la raíz, con Docker instalado:

```powershell
docker compose up --build
```

Compose publica el backend en el puerto 8000 y el frontend en el 80. No uses las credenciales de ejemplo para un despliegue público; configura secretos únicos mediante el entorno del servicio.

## Flujo de trabajo

1. Sincroniza `develop` y crea una rama corta para el cambio:

   ```powershell
   git switch develop
   git pull origin develop
   git switch -c feat/nombre-corto
   ```

2. Mantén el alcance acotado. Si existe un Issue, enlázalo en el Pull Request. No asumas que existe un tablero, rama de integración o proceso de aprobación que no esté configurado en el repositorio.
3. Usa commits descriptivos con prefijos como `feat:`, `fix:`, `docs:`, `test:` o `chore:`. Ejemplos: `fix: validar cantidad de productos` y `docs: corregir guía de inicio`.
4. Revisa los cambios antes de preparar el commit. Añade archivos explícitamente cuando el árbol tenga cambios locales ajenos:

   ```powershell
   git status --short
   git diff --check
   git add backend/app/models/schemas.py
   ```

5. Abre un Pull Request hacia `develop`, explica el problema y la solución, y registra las comprobaciones ejecutadas. La promoción de `develop` a `main` debe hacerse mediante un Pull Request separado cuando el equipo considere lista la versión.

## Validación local

Ejecuta las comprobaciones pertinentes al cambio y reporta sus resultados reales.

### Backend

Desde la raíz:

```powershell
cd backend
$env:PYTHONPATH = "."
python -c "from app.main import app; print('FastAPI import OK')"
pytest tests/ -v --tb=short
```

La CI también ejecuta una comprobación limitada de errores graves con Flake8; no equivale a una revisión completa de estilo o tipos.

### Frontend

Desde la raíz:

```powershell
cd frontend
npm ci
npm run build
```

El `package.json` actual no define scripts de lint ni de pruebas frontend. No reportes esos comandos como ejecutados hasta que se incorporen.

### Cambios de documentación o configuración

```powershell
git diff --check
```

Para cambios de despliegue, comprueba que los nombres de variables, puertos, rutas y comandos coincidan con los Dockerfiles, `docker-compose.yml` y la configuración del proveedor realmente utilizada.

## Pull Request

Incluye:

- El problema que resuelve y el alcance del cambio.
- Decisiones relevantes y efectos sobre API, datos, configuración o experiencia de usuario.
- Comandos de validación ejecutados y sus resultados; indica con claridad lo que no se pudo ejecutar.
- Capturas para cambios visuales y ejemplos sanitizados para cambios de API cuando ayuden a revisar.
- Issues relacionados, si existen.

Antes de solicitar revisión, comprueba que el PR no contiene secretos, archivos `.env`, dependencias instaladas, compilaciones ni cambios locales ajenos. Atiende los comentarios y corrige los checks fallidos antes de integrar.

## Límites funcionales actuales

Flash-Bites contiene flujos de demostración. El backend mantiene clientes y pedidos en memoria; el registro no persiste usuarios ni comprueba contraseñas; el catálogo de la API y el que usa el agente proceden de fuentes distintas. No describas estas capacidades como persistentes, aisladas por negocio o listas para operar pedidos reales sin implementar y validar esos requisitos.

La factura actual es simulada y el chat/RAG tiene dependencias y comportamiento que deben verificarse en el entorno antes de presentarlos como funciones de producción. Al ampliar estas áreas, actualiza la documentación y añade validaciones que cubran los nuevos contratos.
