#!/bin/bash
#
# VPS Setup Script for Flash-Bites
# Run this on your VPS before first deployment
# Usage: bash vps-setup.sh
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    log_error "This script must be run as root (use: sudo bash vps-setup.sh)"
    exit 1
fi

log_info "Starting Flash-Bites VPS setup..."
echo ""

# =========================================
# UPDATE SYSTEM
# =========================================

log_step "1. Updating system packages"
apt-get update
apt-get upgrade -y

# =========================================
# PYTHON 3.11
# =========================================

log_step "2. Installing Python 3.11"
apt-get install -y python3.11 python3.11-venv python3-pip python3-dev
python3.11 --version

# =========================================
# NODE.JS 20
# =========================================

log_step "3. Installing Node.js 20"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
node --version
npm --version

# =========================================
# APACHE2
# =========================================

log_step "4. Installing Apache2"
apt-get install -y apache2

# Enable required modules
a2enmod proxy_http
a2enmod rewrite
a2enmod headers
log_info "Apache modules enabled: proxy_http, rewrite, headers"

# =========================================
# CREATE DEPLOYMENT DIRECTORY
# =========================================

log_step "5. Creating deployment directory"
mkdir -p /var/www/flashbites
chown www-data:www-data /var/www/flashbites
chmod 755 /var/www/flashbites
log_info "Directory: /var/www/flashbites"

# =========================================
# CONFIGURE SUDO PERMISSIONS
# =========================================

log_step "6. Configuring sudo permissions for www-data"

# Create sudoers file
cat > /etc/sudoers.d/flashbites <<'SUDOERS_EOF'
# Allow www-data to restart services without password
www-data ALL=(ALL) NOPASSWD: /usr/sbin/systemctl restart flashbites-backend
www-data ALL=(ALL) NOPASSWD: /usr/sbin/systemctl restart apache2
www-data ALL=(ALL) NOPASSWD: /usr/sbin/systemctl status flashbites-backend
www-data ALL=(ALL) NOPASSWD: /usr/sbin/systemctl status apache2
www-data ALL=(ALL) NOPASSWD: /usr/sbin/a2enmod
www-data ALL=(ALL) NOPASSWD: /usr/sbin/a2ensite
www-data ALL=(ALL) NOPASSWD: /usr/sbin/a2dissite
www-data ALL=(ALL) NOPASSWD: /usr/sbin/systemctl daemon-reload
SUDOERS_EOF

chmod 0440 /etc/sudoers.d/flashbites
log_info "Sudoers file created: /etc/sudoers.d/flashbites"

# =========================================
# GIT SETUP
# =========================================

log_step "7. Verifying Git installation"
git --version

# =========================================
# SSL CERTIFICATE (Optional)
# =========================================

log_step "8. Certbot for SSL (Optional)"
apt-get install -y certbot python3-certbot-apache

log_info "To add SSL later, run:"
log_info "  sudo certbot --apache -d flashbites.com -d www.flashbites.com"

# =========================================
# FIREWALL SETUP (ufw)
# =========================================

log_step "9. Configuring firewall (UFW)"
ufw --force enable
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw status verbose

# =========================================
# VERIFICATION
# =========================================

log_step "10. Verification"
echo ""
log_info "Checking installations:"

echo -n "  Python 3.11: "
python3.11 --version

echo -n "  Node.js: "
node --version

echo -n "  npm: "
npm --version

echo -n "  Apache2: "
apache2 -v | head -1

echo -n "  Git: "
git --version

echo ""

# =========================================
# SUMMARY
# =========================================

log_info "═════════════════════════════════════════════════════════"
log_info "✓ VPS Setup Completed Successfully!"
log_info "═════════════════════════════════════════════════════════"

echo ""
log_info "Next Steps:"
echo ""
log_info "1. Add GitHub SSH Key:"
echo "   ssh-keygen -t rsa -b 4096"
echo "   cat ~/.ssh/id_rsa.pub"
echo "   # Add to GitHub settings or repository deploy keys"
echo ""
log_info "2. Configure GitHub Secrets (in GitHub UI):"
echo "   Settings → Secrets and variables → Actions → New repository secret"
echo "   Add: SERVER_HOST, SERVER_USER, SERVER_SSH_KEY, SERVER_SSH_PORT"
echo "   Add: VITE_API_URL, SECRET_KEY, OPENAI_API_KEY, DATABASE_URL"
echo ""
log_info "3. First Deployment:"
echo "   Go to GitHub Actions → Deploy to VPS (Manual) → Run workflow"
echo "   Select environment: production"
echo ""
log_info "4. Monitor deployment:"
echo "   sudo systemctl status flashbites-backend"
echo "   sudo systemctl status apache2"
echo ""
log_info "5. Check logs:"
echo "   sudo journalctl -u flashbites-backend -f"
echo "   sudo tail -f /var/log/apache2/flashbites-error.log"
echo ""
log_info "Documentation: DEPLOYMENT.md and GITHUB_SECRETS.md"
log_info "═════════════════════════════════════════════════════════"
