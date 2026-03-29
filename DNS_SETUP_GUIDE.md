# DNS Configuration Guide for mamamaasaibakers.com

## Current Status: DNS_PROBE_FINISHED_NXDOMAIN
This error means the domain `mamamaasaibakers.com` is not configured in DNS to point to your server.

## Step 1: Find Your Public IP Address

### Method 1: Check with your hosting provider
- If using cloud hosting (AWS, DigitalOcean, etc.), check your dashboard
- If using shared hosting, contact your provider

### Method 2: Use online tools
Visit any of these websites from your server:
- https://whatismyipaddress.com/
- https://www.whatismyip.com/
- https://icanhazip.com/
- https://ipinfo.io/ip

### Method 3: Command line (if internet accessible)
```bash
curl -s https://api.ipify.org
# or
curl -s https://ipinfo.io/ip
```

## Step 2: Configure DNS Records

### Where to Configure DNS:
1. **Domain Registrar** (GoDaddy, Namecheap, etc.) - where you bought the domain
2. **DNS Hosting Service** (Cloudflare, Route 53, etc.) - if using third-party DNS
3. **Hosting Provider** - if they provide DNS management

### Required DNS Records:

#### A Record (Required):
```
Type: A
Name: mamamaasaibakers.com
Value: [YOUR_PUBLIC_IP_ADDRESS]
TTL: 300 (5 minutes) or 3600 (1 hour)
```

#### CNAME Record (Optional - for www subdomain):
```
Type: CNAME
Name: www.mamamaasaibakers.com
Value: mamamaasaibakers.com
TTL: 300 (5 minutes) or 3600 (1 hour)
```

## Step 3: DNS Propagation

After configuring DNS:
- **Wait 24-48 hours** for DNS propagation worldwide
- Use tools like `nslookup mamamaasaibakers.com` to check if DNS is working
- Clear your local DNS cache: `ipconfig /flushdns` (Windows)

## Step 4: Test Your Domain

Once DNS is configured, test:
```bash
# Test DNS resolution
nslookup mamamaasaibakers.com

# Test website access
curl -I http://mamamaasaibakers.com
```

## Common Issues:

### 1. Wrong IP Address
- Double-check you're using your PUBLIC IP, not private IP (192.168.x.x, 10.x.x.x, 172.16-31.x.x)

### 2. DNS Not Updated
- DNS changes can take 24-48 hours to propagate
- Use online DNS checkers: https://dnschecker.org/

### 3. Firewall Blocking Port 80
- Ensure port 80 is open in your firewall/router
- Configure port forwarding if behind a router

### 4. Apache Not Running
- Verify Apache service is running: `Get-Service Apache2.4`

## Quick Test Commands:

```powershell
# Check if domain resolves
Resolve-DnsName mamamaasaibakers.com

# Test website
Invoke-WebRequest -Uri "http://mamamaasaibakers.com" -UseBasicParsing
```

## Alternative: Local Testing

While waiting for DNS, you can test locally:
- http://localhost (works now)
- http://127.0.0.1 (works now)

## Professional DNS Services:

Consider using:
- **Cloudflare** (free, with CDN and security)
- **Route 53** (AWS, reliable)
- **DigitalOcean DNS** (if hosting there)

---
**Note**: Your server IP appears to be in a private range (10.190.143.223), so you'll need your public IP address for DNS configuration.