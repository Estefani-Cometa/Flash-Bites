# GitHub Secrets Configuration

Este archivo documenta todos los secrets que necesitas configurar en tu repositorio de GitHub para que los workflows de deployment funcionen correctamente.

## Cómo agregar secrets en GitHub

1. Ve a: **Settings → Secrets and variables → Actions**
2. Haz clic en **"New repository secret"**
3. Ingresa el nombre exacto del secret y su valor
4. Haz clic en **"Add secret"**

## Secrets Requeridos

### Configuración del Servidor VPS

```bash
SERVER_HOST
  Descripción: IP o dominio de tu VPS/Apache
  Ejemplo: vps.ejemplo.com o 192.168.1.100
  Requerido: ✅

SERVER_USER
  Descripción: Usuario SSH para conectarse al VPS
  Ejemplo: ubuntu, deploy, www-data
  Requerido: ✅

SERVER_SSH_KEY
  Descripción: Clave privada SSH para autenticación
  Cómo obtener:
    1. En tu máquina local: cat ~/.ssh/id_rsa
    2. Cópia el contenido COMPLETO (incluyendo BEGIN y END)
    3. Pégalo directamente en GitHub
  Requerido: ✅

SERVER_SSH_PORT
  Descripción: Puerto SSH del servidor
  Ejemplo: 22 (por defecto)
  Requerido: ✅
```

### Configuración de la Aplicación

```bash
SECRET_KEY
  Descripción: Clave secreta para FastAPI (generación de tokens JWT)
  Cómo generar:
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  Ejemplo: dGVzdC1zZWNyZXQta2V5LWZvci1mYXN0YXBpLWp3dA==
  Requerido: ✅

OPENAI_API_KEY
  Descripción: API key de OpenAI (si usas LLM)
  Ejemplo: sk-proj-xxx...
  Requerido: ❌ (opcional si usas IA)

DATABASE_URL
  Descripción: Connection string de la base de datos
  Ejemplo: postgresql://user:password@localhost:5432/flashbites
  Requerido: ❌ (opcional si no usas BD)

VITE_API_URL
  Descripción: URL del backend que usará el frontend
  Ejemplo: https://api.flashbites.com
  En desarrollo: http://localhost:8000
  Requerido: ✅
```

## Checklist de Setup

- [ ] Generar SSH key pair si no tienes (ssh-keygen -t rsa -b 4096)
- [ ] Configurar acceso SSH al VPS
- [ ] Generar SECRET_KEY seguro
- [ ] Determinar dominio/IP del VPS
- [ ] Agregar todos los secrets a GitHub
- [ ] Verificar permisos SSH en el VPS (sudo systemctl)
- [ ] Probar deployment manual desde GitHub Actions UI

## Prueba de Secrets

Puedes verificar que los secrets están correctamente configurados ejecutando un workflow y revisando los logs en GitHub Actions. **Los valores de los secrets NUNCA se mostrarán en los logs por seguridad.**

## Cambiar o Actualizar Secrets

1. Ve a **Settings → Secrets and variables → Actions**
2. Haz clic en el secret que quieres actualizar
3. Haz clic en **"Update"**
4. Cambia el valor
5. Haz clic en **"Update secret"**

Los cambios se aplican inmediatamente a los próximos workflow runs.

## Referencia de Workflows

### Qué secrets usa cada workflow

| Workflow | Secrets Usados |
|----------|----------------|

| `ci.yml` | Ninguno |
| `deploy-manual.yml` | SERVER_HOST, SERVER_USER, SERVER_SSH_KEY, SERVER_SSH_PORT, VITE_API_URL, SECRET_KEY, OPENAI_API_KEY, DATABASE_URL |
| `deploy-auto.yml` | SERVER_HOST, SERVER_USER, SERVER_SSH_KEY, SERVER_SSH_PORT, VITE_API_URL, SECRET_KEY, OPENAI_API_KEY, DATABASE_URL |

---

**Última actualización:** 2026-07-07
