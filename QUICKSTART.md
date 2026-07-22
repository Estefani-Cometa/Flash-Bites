# Quick Start Guide - Flash-Bites Deployment

## Checklist de Configuración (5 minutos)

### ✅ Paso 1: Preparar el VPS (Una sola vez)

```bash
# Conectarse al VPS
ssh ubuntu@tu-vps-ip

# Ejecutar el setup script
curl -O https://raw.githubusercontent.com/Estefani-Cometa/Flash-Bites/main/vps-setup.sh
sudo bash vps-setup.sh

# Responder sí a todas las preguntas
```

Tiempo estimado: **3-5 minutos**

---

### ✅ Paso 2: Configurar GitHub Secrets (5 minutos)

Ir a: **GitHub Repo → Settings → Secrets and variables → Actions**

Crear estos secrets:

| Secret | Valor | Ejemplo |
|--------|-------|---------|
| `SERVER_HOST` | IP o dominio del VPS | `192.168.1.100` |
| `SERVER_USER` | Usuario SSH | `ubuntu` |
| `SERVER_SSH_KEY` | Tu clave privada SSH (~/.ssh/id_rsa) | `-----BEGIN RSA PRIVATE KEY-----...` |
| `SERVER_SSH_PORT` | Puerto SSH | `22` |
| `VITE_API_URL` | URL del backend | `https://api.flashbites.com` |
| `SECRET_KEY` | Clave segura (generar: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`) | `dGVzdC1zZWNyZXQ...` |
| `OPENAI_API_KEY` | API key de OpenAI (opcional) | `sk-proj-xxx...` |
| `DATABASE_URL` | URL de BD (opcional) | `postgresql://user:pass@localhost/db` |

Tiempo estimado: **3-5 minutos**

---

### ✅ Paso 3: Primer Deployment

**Opción A: Desde GitHub UI (Más fácil)**

1. Ir a **Actions** en tu repositorio
2. Seleccionar **"Deploy to VPS (Manual)"**
3. Hacer clic en **"Run workflow"**
4. Seleccionar environment: **production**
5. Hacer clic en **"Run workflow"**
6. Ver los logs en tiempo real

**Opción B: Push a main (Automático)**

```bash
git add .
git commit -m "Deploy: initial setup"
git push origin main
# Irá automáticamente a producción si todo valida correctamente
```

Tiempo estimado: **2-3 minutos**

---

## Verificar que todo funciona

Después de que el deployment termine:

```bash
# Conectarse al VPS
ssh ubuntu@tu-vps-ip

# Revisar estado del backend
sudo systemctl status flashbites-backend

# Ver logs del backend
sudo journalctl -u flashbites-backend -f

# Revisar estado de Apache
sudo systemctl status apache2

# Ver logs de Apache
sudo tail -f /var/log/apache2/flashbites-error.log
```

Si ves `active (running)`, ¡todo está funcionando! ✅

---

## URLs Después de Deployment

- **Frontend:** https://flashbites.com (desde Apache)
- **Backend API:** https://flashbites.com/api/docs (FastAPI Swagger docs)
- **Healthcheck:** curl https://flashbites.com/api/health

---

## Troubleshooting Rápido

### Backend no inicia
```bash
sudo systemctl restart flashbites-backend
sudo journalctl -u flashbites-backend -n 50  # Últimas 50 líneas
```

### Frontend no se ve
```bash
ls /var/www/flashbites/frontend/dist/  # Debe tener index.html
sudo systemctl restart apache2
```

### Cambiar variables de entorno
```bash
# SSH al VPS
# Editar: /etc/systemd/system/flashbites-backend.service
sudo systemctl edit flashbites-backend
# Hacer cambios y guardar
sudo systemctl daemon-reload
sudo systemctl restart flashbites-backend
```

---

## Despliegues posteriores

Simplemente hacer push a `main`:

```bash
git add .
git commit -m "Feature: agregar nueva funcionalidad"
git push origin main
```

El deployment automático se ejecutará y la app se actualizará en unos minutos.

---

## Documentación Completa

- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía detallada de deployment
- [GITHUB_SECRETS.md](GITHUB_SECRETS.md) - Detalles sobre configuración de secrets
- [deploy.sh](deploy.sh) - Script de validación local

---

## Soporte

Si algo no funciona:

1. Revisar [Troubleshooting en DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting--verification)
2. Revisar logs en GitHub Actions
3. Revisar logs en el VPS con `journalctl`

¡Listo! 🚀
