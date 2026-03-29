# BestStore Production Deployment Configuration
# Domain: mamamaasaibakers.com

## Production Settings Applied:
- DEBUG = False
- ALLOWED_HOSTS = ['mamamaasaibakers.com', 'www.mamamaasaibakers.com']
- Security headers enabled
- Static files collected for production

## Apache Configuration:
- Virtual Host: mamamaasaibakers.com
- Port: 80 (HTTP)
- Reverse proxy to Django on port 8001
- Static files served directly by Apache

## DNS Configuration Required:
Point your domain mamamaasaibakers.com to this server's IP address:
- A Record: mamamaasaibakers.com -> [YOUR_SERVER_IP]
- CNAME Record: www.mamamaasaibakers.com -> mamamaasaibakers.com

## SSL/HTTPS Setup (Recommended for Production):
1. Obtain SSL certificate (Let's Encrypt or paid)
2. Configure Apache for HTTPS on port 443
3. Redirect HTTP to HTTPS
4. Update Django settings for HTTPS

## Services:
- Apache HTTP Server: Handles static files and proxy
- Waitress WSGI Server: Runs Django application
- Port 8001: Internal Django server
- Port 80: Public web access

## Monitoring:
- Check Apache logs: C:\Users\BRAMWEL\Downloads\httpd-2.4.66-260223-Win64-VS18\Apache24\logs\
- Django logs: Check waitress console output
- Access logs: mamamaasaibakers_access.log
- Error logs: mamamaasaibakers_error.log

## Security Notes:
- Change SECRET_KEY in production
- Use environment variables for sensitive data
- Consider using a reverse proxy like nginx for better performance
- Implement proper firewall rules
- Regular security updates