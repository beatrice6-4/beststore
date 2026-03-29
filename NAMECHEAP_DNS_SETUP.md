# Namecheap DNS Configuration for mamamaasaibakers.com

## Your Server Information:
- **Public IP Address**: 105.164.7.132
- **Apache Port**: 80 (HTTP)
- **Local Testing**: http://localhost (already working)

## Step-by-Step Namecheap DNS Setup:

### 1. Log into Namecheap
1. Go to https://www.namecheap.com/
2. Click "Sign In" and log into your account
3. Go to "Domain List" from the left menu
4. Click on "mamamaasaibakers.com"

### 2. Access DNS Management
1. In the domain details, click on "Manage" button
2. Scroll down and click on "Advanced DNS" tab
3. You should see current DNS records

### 3. Configure DNS Records

#### Delete Existing Records (if any):
- Remove any existing A records for @ or mamamaasaibakers.com
- Remove any existing CNAME records for www

#### Add New Records:

**Record 1: A Record (Main Domain)**
```
Type: A Record
Host: @
Value: 105.164.7.132
TTL: 5 min
```

**Record 2: CNAME Record (www Subdomain)**
```
Type: CNAME Record
Host: www
Value: mamamaasaibakers.com.
TTL: 5 min
```
*Note: Don't forget the trailing dot (.) after mamamaasaibakers.com*

### 4. Save Changes
- Click the green checkmark (✓) to save each record
- Wait for "Record updated successfully" message

### 5. Verify Configuration
After saving, your DNS records should look like:
```
Type    Host    Value                   TTL
A       @       105.164.7.132          5 min
CNAME   www     mamamaasaibakers.com.  5 min
```

## Testing Your Configuration:

### Immediate Test (Local):
```batch
# Test local access (should work now)
start http://localhost
```

### DNS Propagation Test (After 5-10 minutes):
```batch
# Run the DNS test script
test_dns.bat
```

### Online DNS Checkers:
- https://dnschecker.org/ (enter: mamamaasaibakers.com)
- https://www.whatsmydns.net/ (enter: mamamaasaibakers.com)

### Full Website Test (After DNS propagation):
```batch
# Test public access
start http://mamamaasaibakers.com
```

## Troubleshooting:

### If DNS Doesn't Work:
1. **Check IP Address**: Verify 105.164.7.132 is still your public IP
2. **TTL Settings**: Use 5 minutes for faster propagation
3. **Clear DNS Cache**:
   ```batch
   ipconfig /flushdns
   ```
4. **Wait Time**: DNS changes can take 5-60 minutes to propagate

### If Website Doesn't Load:
1. **Check Apache**: Ensure Apache service is running
   ```batch
   sc query Apache2.4
   ```
2. **Check Firewall**: Port 80 must be open
3. **Check Router**: If behind NAT, port forward port 80

### Namecheap Specific Issues:
1. **Custom DNS**: Make sure you're not using custom nameservers
2. **Domain Lock**: Ensure domain is not locked
3. **WHOIS Privacy**: Shouldn't affect DNS resolution

## Expected Timeline:
- **5-10 minutes**: DNS changes visible in most locations
- **1-2 hours**: Global DNS propagation complete
- **Immediate**: Local testing works

## Current Status:
- ✅ Apache configured for mamamaasaibakers.com
- ✅ Django application running
- ✅ Public IP identified: 105.164.7.132
- ⏳ DNS records need to be added in Namecheap

Once you add the DNS records in Namecheap, your domain will start working!