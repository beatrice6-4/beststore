# Apache Deployment Quick Reference

## One-Command Deploy (After Server Setup)

```bash
cd /var/www/mamamaasaibakers && sudo bash -c 'source venv/bin/activate && python manage.py migrate && python manage.py collectstatic --noinput && systemctl restart apache2'
```

## Essential Commands

### Check Status
```bash
# Apache status
sudo systemctl status apache2

# Django health check
cd /var/www/mamamaasaibakers && source venv/bin/activate && python manage.py check

# Website accessibility
curl -I https://mamamaasaibakers.com
```

### Restart Services
```bash
# Reload Apache (no downtime)
sudo systemctl reload apache2

# Restart Apache (brief downtime)
sudo systemctl restart apache2

# Full restart with Django
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py migrate
sudo systemctl restart apache2
```

### View Logs
```bash
# Real-time error log
sudo tail -f /var/log/apache2/beststore_error.log

# Real-time access log
sudo tail -f /var/log/apache2/beststore_access.log

# Django logs
tail -f /var/www/mamamaasaibakers/logs/*.log

# System journal
sudo journalctl -u apache2 -f
```

### Common Fixes

#### Fix Permissions
```bash
sudo chown -R www-data:www-data /var/www/mamamaasaibakers
sudo find /var/www/mamamaasaibakers -type d -exec chmod 755 {} \;
```

#### Collect Static Files
```bash
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py collectstatic --clear --noinput
```

#### Reset Database
```bash
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

#### Clear Cache
```bash
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py clear_cache
```

## File Locations

```
/var/www/mamamaasaibakers/          # Project root
├── venv/                             # Python virtual environment
├── beststore/                        # Django project settings
│   ├── settings.py                   # Django configuration
│   ├── wsgi.py                       # WSGI application
│   └── urls.py                       # URL routing
├── static/                           # Static files source
├── staticfiles/                      # Collected static files (served by Apache)
├── mediafiles/                       # User uploaded files
├── logs/                             # Application logs
├── manage.py                         # Django management
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables (secrets)
└── apache/
    ├── beststore.conf                # Apache VirtualHost config
    ├── wsgi_apache.py                # Apache WSGI file
    └── APACHE_DEPLOYMENT_GUIDE.md    # This guide
```

```
/etc/apache2/
├── sites-available/beststore.conf    # Apache config (symlinked from above)
├── sites-enabled/beststore.conf      # Active Apache config
└── apache2.conf                      # Main Apache configuration
```

```
/var/log/apache2/
├── beststore_access.log              # HTTP request logs
├── beststore_error.log               # Apache error logs
└── error.log                         # System error logs
```

```
/etc/letsencrypt/live/mamamaasaibakers.com/
├── fullchain.pem                     # SSL certificate
├── privkey.pem                       # SSL private key
└── chain.pem                         # Certificate chain
```

## Performance Tuning

### Increase Apache Processes
Edit `/etc/apache2/sites-available/beststore.conf`:
```apache
WSGIDaemonProcess beststore \
  processes=6 \
  threads=20 \
  maximum-requests=15000
```

### Enable Caching Headers
Already configured in VirtualHost for:
- Static files: 1 year
- Media files: 7 days

### Database Connection Pooling
Ensure in Django settings:
```python
DATABASES['default']['CONN_MAX_AGE'] = 600
```

## Monitoring & Uptime

### Basic Health Check Script
```bash
#!/bin/bash
# Save as /usr/local/bin/check_beststore.sh

curl -s -o /dev/null -w "%{http_code}" https://mamamaasaibakers.com
if [ $? -ne 200 ]; then
  sudo systemctl restart apache2
  echo "Apache restarted at $(date)" >> /var/log/beststore_restarts.log
fi
```

### Schedule Hourly Check
```bash
crontab -e

# Add line:
0 * * * * /usr/local/bin/check_beststore.sh
```

## Backup & Restore

### Full Backup
```bash
# Create backup date directory
BACKUP_DIR="/backups/beststore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database
sudo -u postgres pg_dump beststore_db | gzip > "$BACKUP_DIR/database.sql.gz"

# Backup media files
tar -czf "$BACKUP_DIR/mediafiles.tar.gz" /var/www/mamamaasaibakers/mediafiles

# Backup configuration
tar -czf "$BACKUP_DIR/config.tar.gz" \
  /var/www/mamamaasaibakers/.env \
  /etc/apache2/sites-available/beststore.conf

echo "Backup completed: $BACKUP_DIR"
```

### Restore from Backup
```bash
# Restore database
gunzip < "$BACKUP_DIR/database.sql.gz" | sudo -u postgres psql beststore_db

# Restore media files
tar -xzf "$BACKUP_DIR/mediafiles.tar.gz" -C /

# Restore configuration
tar -xzf "$BACKUP_DIR/config.tar.gz" -C /
```

## SSL Certificate Management

### Check Certificate Expiry
```bash
sudo openssl x509 -in /etc/letsencrypt/live/mamamaasaibakers.com/fullchain.pem -text -noout | grep -A 2 Validity
```

### Renew Certificate
```bash
sudo certbot renew
sudo systemctl reload apache2
```

### View Certificate Details
```bash
sudo certbot certificates
```

## Security

### Disable Server Information
```bash
# Edit security configuration
sudo nano /etc/apache2/conf-available/security.conf

# Ensure:
ServerTokens Prod
ServerSignature Off
```

### Check for Vulnerabilities
```bash
# Update all packages
sudo apt-get update && sudo apt-get upgrade -y

# Check Apache modules
sudo apache2ctl -M

# Review active modules (should have only necessary ones)
```

### Firewall Rules
```bash
# View current rules
sudo ufw status

# Essential rules
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
```

## Database Management

### Connect to Database
```bash
sudo -u postgres psql beststore_db
```

### Database Vacuum & Analyze
```bash
sudo -u postgres vacuumdb beststore_db
sudo -u postgres analyzedb beststore_db
```

### Reset Password
```bash
sudo -u postgres psql
ALTER USER beststore_user WITH PASSWORD 'new_secure_password';
\q
```

## Troubleshooting Checklist

- [ ] `sudo apache2ctl configtest` returns "Syntax OK"
- [ ] `curl https://mamamaasaibakers.com` returns 200
- [ ] Static files loading at `/static/`
- [ ] Media files accessible at `/media/`
- [ ] Admin panel accessible at `/admin/`
- [ ] Error logs show no WSGI errors
- [ ] Database connection working
- [ ] SSL certificate valid and not expired
- [ ] File permissions correct (www-data owner)
- [ ] .env file present and readable only by www-data

## Emergency Procedures

### Disable Site (Maintenance)
```bash
sudo a2dissite beststore.conf
sudo a2ensite maintenance.html  # Create maintenance page first
sudo systemctl reload apache2
```

### Re-enable Site
```bash
sudo a2dissite maintenance.html
sudo a2ensite beststore.conf
sudo systemctl reload apache2
```

### Rollback to Previous Version
```bash
cd /var/www/mamamaasaibakers
git checkout <previous-commit-hash>
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
sudo systemctl reload apache2
```

---

**Quick Deploy Checklist**
- [ ] Server prepared with all dependencies
- [ ] Project directory created
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Database created and migrated
- [ ] Static files collected
- [ ] Apache configuration installed
- [ ] SSL certificate configured
- [ ] Services started and enabled
- [ ] Website tested and verified
