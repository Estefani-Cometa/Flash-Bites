# Deployment Guide - Flash-Bites

## Overview

Flash-Bites tiene tres workflows de GitHub Actions configurados:

1. **CI (Continuous Integration)** - Tests y validación en PRs y push a `develop`
2. **Deploy Manual** - Deploy manual a production o staging desde GitHub UI
3. **Deploy Automático** - Deploy automático en push a `main`

## Setup Required

### 1. GitHub Secrets Configuration

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

#### Server Configuration

```bash

SERVER_HOST           - Your VPS/Apache hostname or IP
SERVER_USER           - SSH user (usually 'ubuntu', 'root', or 'www-data')
SERVER_SSH_KEY        - Private SSH key for authentication
SERVER_SSH_PORT       - SSH port (default: 22)
```

#### Application Configuration

```bash
SECRET_KEY            - FastAPI secret key (for token generation)
OPENAI_API_KEY        - OpenAI API key (if using LLM features)
DATABASE_URL          - Database connection URL (if applicable)
VITE_API_URL          - Backend API URL for frontend
```

**Example values:**

```bash
SERVER_HOST=vps.example.com
SERVER_USER=ubuntu
SERVER_SSH_PORT=22
VITE_API_URL=https://api.flashbites.com
```

### 2. VPS Prerequisites

Before deploying, ensure your VPS has:

**Automated Setup (Recommended):**

Run the provided setup script on your VPS:

```bash
# SSH into your VPS
ssh ubuntu@your-vps-ip

# Download and run the setup script
curl -O https://raw.githubusercontent.com/Estefani-Cometa/Flash-Bites/main/vps-setup.sh
sudo bash vps-setup.sh
```

This script automatically installs and configures:

- Python 3.11 + venv
- Node.js 20 + npm
- Apache2 with required modules (proxy, rewrite, headers)
- UFW firewall (ports 22, 80, 443)
- Deployment directory with correct permissions
- Sudo permissions for www-data user

**Manual Setup (If preferred):**

If you prefer manual setup, install these packages:

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y nodejs npm
sudo apt install -y apache2
sudo a2enmod proxy_http rewrite headers
```

**User & Permissions:**

```bash
# Create deployment user (if not using root)
sudo useradd -m -s /bin/bash www-data

# Configure sudoers for service restart
sudo visudo  # Add www-data permissions for systemctl restart
```

**Directory Setup:**

```bash
mkdir -p /var/www/flashbites
sudo chown www-data:www-data /var/www/flashbites
```

## Deployment Methods

### Method 1: Manual Deployment via GitHub UI (Recommended)

1. Go to: <https://github.com/Estefani-Cometa/Flash-Bites/actions>
2. Select **"Deploy to VPS (Manual)"**
3. Click **"Run workflow"**
4. Choose environment: `production` or `staging`
5. Click **"Run workflow"**
6. Monitor logs in the Actions tab

### Method 2: Automatic Deployment on Push

Push to `main` branch → workflow runs automatically:

```bash
git add .
git commit -m "Deploy: feature X"
git push origin main
```

The `deploy-auto.yml` workflow will:

- Validate frontend and backend
- Deploy to production if validation passes
- Send notification on completion

### Method 3: Local Deployment Script

For manual VPS deployment from your local machine:

```bash
# Make script executable
chmod +x deploy.sh

# Validate build (local machine)
bash deploy.sh production

# Then SSH to VPS and run the same script
ssh -p 22 ubuntu@vps.example.com
cd /var/www/flashbites
bash deploy.sh production
```

## Workflow Details

### CI Workflow (`.github/workflows/ci.yml`)

**Triggers:** Pull requests to `main`/`develop`, push to `develop`

**What it does:**

- Installs backend dependencies
- Runs Python tests (`pytest`)
- Checks Python code quality (`flake8`)
- Installs frontend dependencies
- Builds frontend with Vite
- Reports build artifacts

**Configuration:** No secrets needed

### Deploy Manual Workflow (`.github/workflows/deploy-manual.yml`)

**Triggers:** Manual trigger from GitHub UI

**What it does:**

1. Validates frontend build locally
2. Validates backend tests locally
3. Connects to VPS via SSH
4. Clones/updates repository
5. Installs frontend dependencies & builds Vite
6. Installs backend dependencies
7. Configures Apache with reverse proxy
8. Creates/updates systemd service for FastAPI
9. Restarts services (Apache + Uvicorn)

**Secrets used:**

- `SERVER_HOST`, `SERVER_USER`, `SERVER_SSH_KEY`, `SERVER_SSH_PORT`
- `SECRET_KEY`, `OPENAI_API_KEY`, `DATABASE_URL`, `VITE_API_URL`

### Deploy Auto Workflow (`.github/workflows/deploy-auto.yml`)

**Triggers:** Push to `main` branch

**What it does:**

- Same as Deploy Manual but runs automatically
- Skips if validation fails

## VPS Configuration Files

The workflows automatically create these files on your VPS:

### Apache Config

**Location:** `/etc/apache2/sites-available/flashbites.conf`

```apache
<VirtualHost *:80>
    ServerName flashbites.com
    ServerAlias www.flashbites.com
    
    # Proxy backend requests to FastAPI
    ProxyPreserveHost On
    ProxyPass /api/ http://127.0.0.1:8000/api/
    ProxyPassReverse /api/ http://127.0.0.1:8000/api/
    
    # Serve frontend from dist/
    DocumentRoot /var/www/flashbites/frontend/dist
    
    # SPA rewrite rule
    <Directory /var/www/flashbites/frontend/dist>
        RewriteEngine On
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/flashbites-error.log
    CustomLog ${APACHE_LOG_DIR}/flashbites-access.log combined
</VirtualHost>
```

### Systemd Service

**Location:** `/etc/systemd/system/flashbites-backend.service`

```ini
[Unit]
Description=Flash-Bites FastAPI Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/flashbites/backend
Environment="PATH=/var/www/flashbites/backend/venv/bin"
Environment="SECRET_KEY=your-secret-key"
Environment="OPENAI_API_KEY=sk-xxx..."
Environment="DATABASE_URL=postgresql://user:pass@localhost/flashbites"
ExecStart=/var/www/flashbites/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Monitoring & Troubleshooting

### Check Deployment Status

```bash
# On your VPS:
ssh ubuntu@vps.example.com

# Backend service
sudo systemctl status flashbites-backend
sudo journalctl -u flashbites-backend -f

# Apache
sudo systemctl status apache2
sudo tail -f /var/log/apache2/flashbites-error.log
```

### Common Issues

***Issue: "Permission denied" on SSH***

```bash
# On your local machine, ensure SSH key permissions
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh
```

**Issue: "Connection refused" to backend***

```bash
# On VPS, ensure backend is running
sudo systemctl restart flashbites-backend
sudo systemctl status flashbites-backend
```

**Issue: "Frontend build failed"***

```bash
# On VPS
cd /var/www/flashbites/frontend
npm ci --force
npm run build
```

**Issue: Environment variables not found***

```bash
# Check systemd service is using correct environment
sudo systemctl cat flashbites-backend
# Update service: sudo systemctl edit flashbites-backend
```

## Environment Variables

### Frontend (`.env` or via workflow secret `VITE_API_URL`)

```bash
VITE_API_URL=https://api.flashbites.com
```

### Backend (FastAPI - via systemd environment)

```bash
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-xxx...
DATABASE_URL=postgresql://user:pass@localhost/flashbites
```

## Development & Testing

### Local Testing Before Deploy

```bash
# Test frontend build
cd frontend
npm ci
npm run build
ls dist/  # Should exist with index.html

# Test backend
cd ../backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v

# Test backend startup
uvicorn app.main:app --reload
# Visit: http://localhost:8000/docs
```

### Testing Workflows Locally (Optional)

Install `act` to test GitHub Actions locally:

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | bash

# Test CI workflow
act pull_request -j test

# Test deployment (requires secrets file)
act workflow_dispatch -s SERVER_HOST=... -s SERVER_USER=... etc.
```

## Rollback Procedure

If deployment breaks production:

```bash
# On VPS
ssh ubuntu@vps.example.com
cd /var/www/flashbites

# Show git history
git log --oneline -10

# Rollback to previous commit
git reset --hard HEAD~1

# Rebuild & restart
npm run build  # frontend
pip install -r backend/requirements.txt  # backend
sudo systemctl restart flashbites-backend flashbites-apache2
```

Or trigger a new deployment from GitHub UI pointing to a stable branch.

## Support & Documentation

- FastAPI Docs: <http://your-vps.com/docs>
- GitHub Actions: <https://github.com/Estefani-Cometa/Flash-Bites/actions>
- Vite Docs: <https://vitejs.dev/>
- FastAPI Docs: <https://fastapi.tiangolo.com/>

---

**Last Updated:** 2026-07-07
