#!/bin/bash

# Apache Deployment Setup Script for BestStore Django Application
# Run this script on your Apache server as root or with sudo

set -e

echo "======================================"
echo "BestStore Django - Apache Deployment"
echo "======================================"

# Configuration
PROJECT_NAME="beststore"
PROJECT_DIR="/var/www/mamamaasaibakers"
DOMAIN="mamamaasaibakers.com"
USER="www-data"
GROUP="www-data"
PYTHON_VERSION="3.11"

# Step 1: Update system packages
echo "[1/11] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Step 2: Install required packages
echo "[2/11] Installing required packages..."
sudo apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev \
    apache2 \
    apache2-dev \
    libapache2-mod-wsgi-py3 \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-all \
    postgresql-client \
    git \
    curl \
    wget \
    certbot \
    python3-certbot-apache \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev

# Step 3: Create project directory
echo "[3/11] Creating project directory..."
if [ ! -d "$PROJECT_DIR" ]; then
    sudo mkdir -p "$PROJECT_DIR"
fi
sudo chown -R "$USER:$GROUP" "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"

# Step 4: Clone or configure project
echo "[4/11] Setting up project repository..."
# Replace with your actual git repository or local project copy
# git clone <your-repo-url> "$PROJECT_DIR"
# For now, assuming project is already in place

# Step 5: Create virtual environment
echo "[5/11] Creating Python virtual environment..."
cd "$PROJECT_DIR"
python${PYTHON_VERSION} -m venv venv
source venv/bin/activate

# Step 6: Install Python dependencies
echo "[6/11] Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Step 7: Create/Update environment variables
echo "[7/11] Setting up environment variables..."
cat > "${PROJECT_DIR}/.env" << EOF
DEBUG=False
DJANGO_SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=mamamaasaibakers.com,www.mamamaasaibakers.com
DATABASE_URL=postgresql://beststore_user:beststore_password@localhost:5432/beststore_db
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
EOF

sudo chown "$USER:$GROUP" "${PROJECT_DIR}/.env"
chmod 600 "${PROJECT_DIR}/.env"

# Step 8: Collect static files
echo "[8/11] Collecting static files..."
cd "$PROJECT_DIR"
source venv/bin/activate
python manage.py collectstatic --noinput

# Step 9: Create logs directory
echo "[9/11] Setting up logs directory..."
mkdir -p "$PROJECT_DIR/logs"
sudo chown -R "$USER:$GROUP" "$PROJECT_DIR/logs"
chmod 755 "$PROJECT_DIR/logs"

# Step 10: Enable Apache modules
echo "[10/11] Enabling Apache modules..."
sudo a2enmod wsgi
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod headers
sudo a2enmod deflate
sudo a2enmod expires

# Step 11: Install and configure Apache VirtualHost
echo "[11/11] Configuring Apache VirtualHost..."
sudo cp beststore.conf /etc/apache2/sites-available/
sudo a2ensite beststore.conf
sudo a2dissite 000-default.conf

# Verify Apache Configuration
echo ""
echo "Verifying Apache configuration..."
sudo apache2ctl configtest

# Restart Apache
echo "Restarting Apache..."
sudo systemctl restart apache2

# Setup SSL Certificate with Let's Encrypt
echo ""
echo "======================================"
echo "Setting up SSL Certificate..."
echo "======================================"
sudo certbot --apache -d "$DOMAIN" -d "www.$DOMAIN"

# Final verification
echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "✓ Project Directory: $PROJECT_DIR"
echo "✓ Domain: $DOMAIN"
echo "✓ Python Environment: $PROJECT_DIR/venv"
echo "✓ Static Files: $PROJECT_DIR/staticfiles"
echo "✓ Media Files: $PROJECT_DIR/mediafiles"
echo "✓ Logs: $PROJECT_DIR/logs"
echo ""
echo "Next steps:"
echo "1. Update .env file with your actual credentials"
echo "2. Configure database: sudo -u postgres createdb beststore_db"
echo "3. Run migrations: cd $PROJECT_DIR && source venv/bin/activate && python manage.py migrate"
echo "4. Create superuser: python manage.py createsuperuser"
echo "5. Test the site: curl https://$DOMAIN"
echo ""
