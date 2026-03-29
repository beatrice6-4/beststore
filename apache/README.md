# BestStore Apache Deployment - Complete Setup Guide

## 📋 Overview

This folder contains all necessary files and documentation to deploy the BestStore Django application to Apache web server with mod_wsgi.

## 📁 Files in This Directory

### Configuration Files
- **`beststore.conf`** - Apache VirtualHost configuration for production deployment
- **`wsgi_apache.py`** - Optimized WSGI application file for Apache mod_wsgi

### Documentation
- **`APACHE_DEPLOYMENT_GUIDE.md`** - Detailed step-by-step deployment guide (15 steps)
- **`DJANGO_SETTINGS_CONFIG.md`** - Django settings configuration reference
- **`QUICK_REFERENCE.md`** - Quick commands and common operations cheat sheet

### Scripts
- **`deploy.sh`** - Fully automated deployment bash script (Linux/Ubuntu)

## 🚀 Quick Start (Choose One)

### Option A: Automated Deployment (Recommended)
```bash
# On your Apache server (Ubuntu/Debian Linux):
chmod +x deploy.sh
sudo ./deploy.sh

# Follows all best practices and best practices automatically
# Approximately 10-15 minutes for complete setup
```

### Option B: Manual Deployment
Follow the step-by-step guide in `APACHE_DEPLOYMENT_GUIDE.md`
- Each step clearly explained
- Understand what each command does
- Better for learning and custom configurations

### Option C: Quick Deployment
Use `QUICK_REFERENCE.md` for fast deployment if you know Apache

## 🎯 What Gets Deployed

After deployment, you'll have:

```
✓ Django application running on Apache with mod_wsgi
✓ HTTPS with Let's Encrypt SSL certificate
✓ Static files served directly by Apache (fast)
✓ Media files with proper permissions
✓ PostgreSQL database (production-ready)
✓ Comprehensive logging and error tracking
✓ Security headers and configurations
✓ Automated SSL renewal
✓ Performance optimizations (caching, compression, etc.)
```

## 📊 Deployment Architecture

```
Internet
   ↓
HTTPS (Port 443)
   ↓
Apache Web Server
   ├─ mod_wsgi
   │  └─ Django Application
   ├─ Static Files Handler (/static/)
   └─ Reverse Proxy (if needed)
   ↓
PostgreSQL Database
```

## ✅ Pre-Deployment Checklist

### 1. Development Environment Ready
- [ ] Django settings.py ready for production
- [ ] All dependencies in requirements.txt
- [ ] Database migrations created
- [ ] Static files collected locally
- [ ] No DEBUG mode dependencies in code

### 2. Server Preparation
- [ ] Server IP assigned and accessible
- [ ] Domain name registered (mamamaasaibakers.com)
- [ ] Domain DNS pointing to server IP
- [ ] SSH access available
- [ ] Ubuntu/Debian Linux 20.04+

### 3. Credentials & Configuration
- [ ] First set of administrator account info
- [ ] Email service credentials (for admin notifications)
- [ ] Database backup prepared
- [ ] .env file template created
- [ ] SSL certificate plan (Let's Encrypt recommended)

### 4. Security
- [ ] No hardcoded secrets in code
- [ ] All credentials in environment variables
- [ ] Firewall rules documented
- [ ] Backup strategy in place
- [ ] Monitoring plan defined

## 🔧 Setup Instructions

### Step 1: Prepare Your Server
Ensure your server has:
- Ubuntu 20.04 LTS or later
- root/sudo access
- At least 2GB RAM
- 10GB+ disk space
- Internet connectivity
- SSH access

### Step 2: Copy Files
```bash
# From your local machine:
scp -r apache/ your-server:/tmp/apache

# SSH into server:
ssh your-server

# Move files to project directory:
sudo cp /tmp/apache/* /var/www/mamamaasaibakers/apache/
```

### Step 3: Run Deployment
```bash
cd /var/www/mamamaasaibakers
chmod +x apache/deploy.sh
sudo bash apache/deploy.sh
```

### Step 4: Post-Deployment Configuration
After deployment completes:

1. **Update .env file with your credentials:**
   ```bash
   sudo nano /var/www/mamamaasaibakers/.env
   ```

2. **Create superuser:**
   ```bash
   cd /var/www/mamamaasaibakers
   source venv/bin/activate
   python manage.py createsuperuser
   ```

3. **Test the application:**
   ```bash
   curl https://mamamaasaibakers.com
   ```

## 🐛 Troubleshooting

### Most Common Issues & Fixes

#### Issue: "500 Internal Server Error"
```bash
# Check Apache error log
sudo tail -100 /var/log/apache2/beststore_error.log

# Check Django errors
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py check
```

#### Issue: "Static files not loading"
```bash
# Re-collect static files
cd /var/www/mamamaasaibakers
source venv/bin/activate
python manage.py collectstatic --clear --noinput

# Verify Alias in Apache config
sudo apache2ctl configtest
```

#### Issue: "Database connection error"
```bash
# Verify DATABASE_URL
cat /var/www/mamamaasaibakers/.env | grep DATABASE_URL

# Test PostgreSQL connection
sudo -u postgres psql beststore_db

# Check permissions
ps aux | grep postgres
```

#### Issue: "Permission denied" errors
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/mamamaasaibakers

# Fix permissions
sudo find /var/www/mamamaasaibakers -type d -exec chmod 755 {} \;
sudo find /var/www/mamamaasaibakers -type f -exec chmod 644 {} \;

# .env should be more restrictive
sudo chmod 600 /var/www/mamamaasaibakers/.env
```

For more troubleshooting, see `APACHE_DEPLOYMENT_GUIDE.md` - Troubleshooting section.

## 📈 Monitoring & Maintenance

### Daily Tasks
```bash
# Check Apache status
sudo systemctl status apache2

# Monitor error logs
sudo tail -f /var/log/apache2/beststore_error.log

# Check disk space
df -h
```

### Weekly Tasks
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Check backups
ls -la /backups/beststore_*/

# Review access logs for issues
sudo tail /var/log/apache2/beststore_access.log
```

### Monthly Tasks
```bash
# Database maintenance
sudo -u postgres vacuumdb beststore_db
sudo -u postgres analyzedb beststore_db

# Review and rotate logs
sudo logrotate -f /etc/logrotate.d/apache2

# Test SSL certificate renewal
sudo certbot renew --dry-run
```

## 🔒 Security Best Practices

### 1. Keep Everything Updated
```bash
# Auto-update security patches
sudo apt-get install unattended-upgrades
sudo systemctl enable unattended-upgrades
```

### 2. Monitor Access
```bash
# Real-time access monitoring
sudo tail -f /var/log/apache2/beststore_access.log | grep -v "200"
```

### 3. Regular Backups
```bash
# Daily automated backup
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-beststore.sh
```

### 4. SSL Certificate Renewal
```bash
# Automatic renewal (already set up)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 5. Firewall Configuration
```bash
# Only allow necessary ports
sudo ufw default deny incoming
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

## 📞 Support Resources

### Documentation
- See individual `.md` files in this directory for detailed information
- `QUICK_REFERENCE.md` - Quick lookup for common commands
- `DJANGO_SETTINGS_CONFIG.md` - Settings configuration details

### Official Resources
- [Django Deployment with mod_wsgi](https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/apache/)
- [Apache mod_wsgi Documentation](https://modwsgi.readthedocs.io/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Common Commands
See `QUICK_REFERENCE.md` for:
- Service management
- Log monitoring
- Database operations
- Backup procedures
- Emergency operations

## 🎉 Success Indicators

Your deployment is successful when:

✓ `curl https://mamamaasaibakers.com` returns HTTP 200 with HTML content
✓ `https://mamamaasaibakers.com/admin/` is accessible and styled
✓ Static files are loading (CSS, images, JavaScript)
✓ No errors in `/var/log/apache2/beststore_error.log`
✓ Django health check passes: `python manage.py check`
✓ SSL certificate is valid and not expired
✓ Database migrations are applied
✓ Superuser account created and functional

## 📝 Next Steps After Deployment

1. **Configure Email System**
   - Test email sending
   - Set up admin notifications
   - Configure backup alerts

2. **Set Up Monitoring**
   - Enable Application Performance Monitoring (APM)
   - Set up uptime monitoring
   - Configure alerts for errors

3. **Plan Scaling**
   - Monitor server performance
   - Plan for increased traffic
   - Consider load balancing

4. **Security Hardening**
   - Run security scan
   - Review firewall rules
   - Enable intrusion detection

5. **Backup & Recovery**
   - Automate daily backups
   - Test backup recovery
   - Document recovery procedures

## 📞 Getting Help

If you encounter issues not covered in documentation:

1. Check the troubleshooting section in `APACHE_DEPLOYMENT_GUIDE.md`
2. Review Apache error logs: `sudo tail /var/log/apache2/beststore_error.log`
3. Check Django logs: `tail /var/www/mamamaasaibakers/logs/django.log`
4. Verify Apache configuration: `sudo apache2ctl configtest`
5. Test Django: `cd /var/www/mamamaasaibakers && source venv/bin/activate && python manage.py check`

## 📄 License & Credits

BestStore Django Application
Apache Configuration - 2026
Deployment Guide Version 1.0

---

**For detailed step-by-step instructions, see:** [APACHE_DEPLOYMENT_GUIDE.md](APACHE_DEPLOYMENT_GUIDE.md)

**For quick command reference, see:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**For Django configuration details, see:** [DJANGO_SETTINGS_CONFIG.md](DJANGO_SETTINGS_CONFIG.md)

**Last Updated**: 2026-03-21
