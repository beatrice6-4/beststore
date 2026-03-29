# BestStore Django - Apache Deployment Guide

## Overview
This guide walks you through deploying the BestStore Django application to Apache web server with mod_wsgi.

## System Requirements

- **OS**: Ubuntu 20.04 LTS or later (or any Linux distribution with Apache)
- **Python**: 3.8+
- **Database**: PostgreSQL 12+
- **Web Server**: Apache 2.4+
- **Memory**: Minimum 2GB RAM recommended
- **Storage**: 10GB+ for application and media files

## Pre-Deployment Checklist

- [ ] Domain name configured and pointing to server IP
- [ ] SSL certificate (Let's Encrypt recommended)
- [ ] PostgreSQL database created
- [ ] Environment variables documented
- [ ] Static files collected locally
- [ ] All dependencies in requirements.txt
- [ ] `.env` file templates prepared
- [ ] Backup of current database

## Deployment Steps

### 1. Prepare Your Server

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
  python3.11 python3.11-venv python3.11-dev \
  apache2 apache2-dev libapache2-mod-wsgi-py3 \
  postgresql postgresql-contrib postgresql-server-dev-all \
  git build-essential libssl-dev libffi-dev libpq-dev \
  certbot python3-certbot-apache
```

### 2. Create Project Directory

```bash
# Create and set permissions
sudo mkdir -p /var/www/mamamaasaibakers
sudo chown -R www-data:www-data /var/www/mamamaasaibakers
```

### 3. Clone/Copy Project

```bash
# Option A: Clone from Git
cd /var/www/mamamaasaibakers
sudo git clone <your-repository-url> .

# Option B: Copy from existing location
sudo cp -r /path/to/local/beststore/* /var/www/mamamaasaibakers/
```

### 4. Create Virtual Environment

```bash
cd /var/www/mamamaasaibakers
sudo python3.11 -m venv venv
sudo chown -R www-data:www-data venv
source venv/bin/activate
```

### 5. Install Python Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 6. Configure Environment Variables

```bash
# Create .env file
sudo nano /var/www/mamamaasaibakers/.env
```

Add the following (update with your values):

```
DEBUG=False
DJANGO_SECRET_KEY=your-very-long-secret-key-here
ALLOWED_HOSTS=mamamaasaibakers.com,www.mamamaasaibakers.com
DATABASE_URL=postgresql://beststore_user:password@localhost:5432/beststore_db
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Set proper permissions:
```bash
sudo chmod 600 /var/www/mamamaasaibakers/.env
```

### 7. Create PostgreSQL Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE beststore_db;
CREATE USER beststore_user WITH PASSWORD 'secure_password';
ALTER ROLE beststore_user SET client_encoding TO 'utf8';
ALTER ROLE beststore_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE beststore_user SET default_transaction_deferrable TO on;
ALTER ROLE beststore_user SET default_transaction_readonly TO off;
GRANT ALL PRIVILEGES ON DATABASE beststore_db TO beststore_user;
\q
```

### 8. Collect Static Files

```bash
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py collectstatic --noinput
```

### 9. Run Database Migrations

```bash
python manage.py migrate
```

### 10. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 11. Enable Required Apache Modules

```bash
sudo a2enmod wsgi
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod headers
sudo a2enmod deflate
sudo a2enmod expires
```

### 12. Install Apache Configuration

```bash
# Copy and enable your VirtualHost configuration
sudo cp /var/www/mamamaasaibakers/apache/beststore.conf \
  /etc/apache2/sites-available/

# Enable the site
sudo a2ensite beststore.conf

# Disable default site (optional)
sudo a2dissite 000-default.conf

# Verify configuration
sudo apache2ctl configtest
# Should output: Syntax OK
```

### 13. Configure SSL with Let's Encrypt

```bash
# Install and configure certificate
sudo certbot --apache -d mamamaasaibakers.com -d www.mamamaasaibakers.com

# Enable auto-renewal
sudo systemctl enable certbot.timer
```

### 14. Start Apache

```bash
# Restart Apache to apply changes
sudo systemctl restart apache2

# Enable Apache to start on boot
sudo systemctl enable apache2

# Check Apache status
sudo systemctl status apache2
```

### 15. Create Necessary Directories

```bash
# Create logs directory
mkdir -p /var/www/mamamaasaibakers/logs
sudo chown www-data:www-data /var/www/mamamaasaibakers/logs

# Ensure media files directory exists
mkdir -p /var/www/mamamaasaibakers/mediafiles
sudo chown www-data:www-data /var/www/mamamaasaibakers/mediafiles
```

## File Permissions

```bash
# Set correct ownership
sudo chown -R www-data:www-data /var/www/mamamaasaibakers

# Set directory permissions
sudo find /var/www/mamamaasaibakers -type d -exec chmod 755 {} \;

# Set file permissions
sudo find /var/www/mamamaasaibakers -type f -exec chmod 644 {} \;

# Keep private files more restrictive
sudo chmod 600 /var/www/mamamaasaibakers/.env
sudo chmod 700 /var/www/mamamaasaibakers/manage.py
```

## Post-Deployment Verification

### Test Apache Configuration
```bash
sudo apache2ctl configtest
# Output should be: Syntax OK
```

### Test the Website
```bash
curl -I https://mamamaasaibakers.com
```

### View Apache Logs
```bash
# Error log
sudo tail -f /var/log/apache2/beststore_error.log

# Access log
sudo tail -f /var/log/apache2/beststore_access.log
```

### Test Django
```bash
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py check
```

### Verify Static Files
```bash
curl https://mamamaasaibakers.com/static/admin/css/base.css
```

## Troubleshooting

### Permission Denied Errors
```bash
# Verify ownership
ls -la /var/www/mamamaasaibakers

# Fix permissions
sudo chown -R www-data:www-data /var/www/mamamaasaibakers
sudo chmod 755 /var/www/mamamaasaibakers
```

### 500 Internal Server Error
```bash
# Check Apache error log
sudo tail -100 /var/log/apache2/beststore_error.log

# Check Django logs
tail -100 /var/www/mamamaasaibakers/logs/django.log
```

### Static Files Not Loading
```bash
# Verify STATIC_ROOT exists and is readable
ls -la /var/www/mamamaasaibakers/staticfiles

# Re-collect static files
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py collectstatic --clear --noinput
```

### Database Connection Error
```bash
# Verify DATABASE_URL in .env
cat /var/www/mamamaasaibakers/.env | grep DATABASE_URL

# Test PostgreSQL connection
sudo -u www-data python /var/www/mamamaasaibakers/manage.py dbshell
```

### Module wsgi Error
```bash
# Verify mod_wsgi is installed
sudo apt list --installed | grep libapache2-mod-wsgi

# Reinstall if needed
sudo apt-get install --reinstall libapache2-mod-wsgi-py3
sudo a2enmod wsgi
```

## Maintenance

### Regular Updates
```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Python packages
cd /var/www/mamamaasaibakers
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### Database Backups
```bash
# Backup database
sudo -u postgres pg_dump beststore_db > beststore_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup media files
tar -czf mediafiles_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/www/mamamaasaibakers/mediafiles
```

### Monitor Performance
```bash
# Check Apache processes
ps aux | grep apache

# Check memory usage
free -h

# Check disk usage
df -h

# Check Apache status
sudo systemctl status apache2
```

### SSL Certificate Renewal
```bash
# Test renewal (dry-run)
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew
```

## Security Best Practices

### 1. Firewall Configuration
```bash
# Allow HTTP and HTTPS only
sudo ufw default deny incoming
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

### 2. Update Django Settings for Production

Ensure in `settings.py`:
```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 3. Hide Server Information
```bash
# Edit Apache configuration
sudo nano /etc/apache2/conf-available/security.conf

# Ensure these are set:
ServerTokens Prod
ServerSignature Off
```

### 4. Disable Directory Listing
Already configured in VirtualHost - DirectoryIndex and Options -Indexes

### 5. Regular Security Updates
```bash
# Check for updates
sudo apt list --upgradable

# Install updates
sudo apt-get update && sudo apt-get upgrade -y
```

## Performance Optimization

### 1. Enable Gzip Compression
Already configured in VirtualHost

### 2. Enable Browser Caching
Already configured in VirtualHost with Cache-Control headers

### 3. Optimize WSGI Settings
Adjust in VirtualHost:
```
WSGIDaemonProcess beststore python-home=/var/www/mamamaasaibakers/venv \
  processes=4 threads=15 maximum-requests=10000
```

### 4. Database Connection Pooling
Add to Django settings if needed:
```python
DATABASES['default']['CONN_MAX_AGE'] = 600
```

## Deployment Automation Script

Automated deployment script available at: [deploy.sh](deploy.sh)

Make it executable and run:
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

## Support and Troubleshooting

For common issues and solutions, see the troubleshooting section above.

## Next Steps

1. Monitor the application for 24-48 hours after deployment
2. Set up uptime monitoring and alerts
3. Configure automated backups
4. Schedule regular security scanning
5. Plan for load testing if expecting high traffic

---

**Last Updated**: 2026-03-21
**Version**: 1.0
