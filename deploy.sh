#!/bin/bash
#
# Deploy script for Flash-Bites
# Usage: bash deploy.sh [production|staging]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Get environment parameter
ENVIRONMENT=${1:-production}

if [[ "$ENVIRONMENT" != "production" && "$ENVIRONMENT" != "staging" ]]; then
    log_error "Environment must be 'production' or 'staging'"
    exit 1
fi

log_info "Starting deployment to environment: $ENVIRONMENT"

# Verify we're in the correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    log_error "Must be executed from the project root (where backend/ and frontend/ exist)"
    exit 1
fi

# =========================================
# BACKEND
# =========================================

log_info "Updating Backend (FastAPI)..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log_info "Creating virtual environment..."
    python3.11 -m venv venv
    if [ $? -ne 0 ]; then
        log_error "Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Instalar dependencias
log_info "Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    log_error "Failed to install Python dependencies"
    exit 1
fi

log_info "✓ Backend ready"

cd ..

# =========================================
# FRONTEND
# =========================================

log_info "Updating Frontend (React + Vite)..."
cd frontend

# Instalar dependencias
log_info "Installing Node dependencies..."
npm ci

if [ $? -ne 0 ]; then
    log_error "Failed to install Node dependencies"
    exit 1
fi

# Verificar archivo .env (opcional para dev local)
if [ ! -f ".env" ]; then
    log_warn "No .env file found in frontend/ - using defaults"
fi

# Build
log_info "Building React application with Vite..."
npm run build

if [ ! -d "dist" ]; then
    log_error "Frontend build directory not found! Build failed."
    exit 1
fi

log_info "✓ Frontend built successfully (dist/ created)"

cd ..

# =========================================
# FINAL STATUS
# =========================================

log_info "═════════════════════════════════════════════════════════"
log_info "✓ Deployment validated successfully for $ENVIRONMENT"
log_info "═════════════════════════════════════════════════════════"

log_info ""
log_info "Build artifacts ready:"
log_debug "  Frontend: ./frontend/dist"
log_debug "  Backend:  ./backend (venv: ./backend/venv)"

log_info ""
log_info "Next steps:"

if [[ "$ENVIRONMENT" == "production" ]]; then
    log_info "1. Review changes:"
    log_info "   git diff HEAD~1"
    log_info ""
    log_info "2. Commit and push:"
    log_info "   git add ."
    log_info "   git commit -m 'Deploy to production'"
    log_info "   git push origin main"
    log_info ""
    log_info "3. GitHub Actions will automatically deploy"
    log_info "   Check: https://github.com/Estefani-Cometa/Flash-Bites/actions"
    log_info ""
    log_info "4. Or deploy manually to VPS:"
    log_info "   bash deploy.sh production (from VPS)"
else
    log_info "1. Deploy to staging VPS:"
    log_info "   bash deploy.sh staging (from VPS)"
fi

log_info ""
log_info "To start backend locally:"
log_info "  cd backend"
log_info "  source venv/bin/activate"
log_info "  uvicorn app.main:app --reload"
log_info ""
log_info "To start frontend locally:"
log_info "  cd frontend"
log_info "  npm run dev"
