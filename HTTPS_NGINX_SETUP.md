# HTTPS/Nginx Reverse Proxy Setup for CogniData

## Overview

This guide helps you set up Nginx as a reverse proxy in front of Streamlit to:
- ✅ Enforce HTTPS/TLS encryption (GDPR Article 32)
- ✅ Add security headers (Content-Security-Policy, HSTS, X-Frame-Options)
- ✅ Handle SSL certificate management
- ✅ Hide Streamlit from direct internet exposure
- ✅ Enable rate limiting at reverse proxy layer

**Architecture:**
```
Client (HTTPS)
    ↓
Nginx (Reverse Proxy, TLS termination)
    ↓
Streamlit (HTTP localhost:8501)
```

---

## Part 1: Install Nginx

### macOS (Development)
```bash
brew install nginx
```

### Ubuntu/Debian (Linux Server)
```bash
sudo apt-get update
sudo apt-get install nginx
```

### RHEL/CentOS (Linux Server)
```bash
sudo yum install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

## Part 2: Obtain SSL Certificate

### Option A: Free Certificate with Let's Encrypt (Production Recommended)

**Prerequisites:**
- Domain name pointing to your server
- Port 80 and 443 open to the internet

**Install Certbot:**
```bash
# Ubuntu/Debian
sudo apt-get install certbot python3-certbot-nginx

# macOS
brew install certbot certbot-nginx

# RHEL/CentOS
sudo yum install certbot python3-certbot-nginx
```

**Generate Certificate:**
```bash
# Interactive (recommended for first time)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# With Nginx plugin (automatic setup)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Certificate Details:**
- Location: `/etc/letsencrypt/live/yourdomain.com/`
- Files:
  - `fullchain.pem` - Your certificate + chain
  - `privkey.pem` - Private key
- Auto-renewal: Certbot sets up automatic renewal via cron

### Option B: Self-Signed Certificate (Development Only)

⚠️ **WARNING:** For development/testing only. Browsers will show security warnings.

```bash
# Generate self-signed cert (valid 365 days)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/cognidata-self-signed.key \
  -out /etc/ssl/certs/cognidata-self-signed.crt \
  -subj "/CN=localhost"

# Verify certificate
sudo openssl x509 -in /etc/ssl/certs/cognidata-self-signed.crt -text -noout
```

---

## Part 3: Configure Nginx

### Main Configuration

Edit `/etc/nginx/sites-available/cognidata` (or `/etc/nginx/conf.d/cognidata.conf` on some systems):

```nginx
# Redirect HTTP to HTTPS (enforce encryption)
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all HTTP traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificate (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL certificate (Self-signed - development only)
    # ssl_certificate /etc/ssl/certs/cognidata-self-signed.crt;
    # ssl_certificate_key /etc/ssl/private/cognidata-self-signed.key;
    
    # TLS Configuration (GDPR Article 32)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers (GDPR Article 32 + OWASP)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self';" always;
    
    # Logging
    access_log /var/log/nginx/cognidata_access.log combined;
    error_log /var/log/nginx/cognidata_error.log warn;
    
    # Rate limiting (prevent abuse at reverse proxy layer)
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=100r/m;
    
    # Root location
    location / {
        limit_req zone=general_limit burst=20 nodelay;
        
        # Proxy to Streamlit
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        
        # Headers for Streamlit
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        
        # Buffering (important for Streamlit WebSocket)
        proxy_buffering off;
    }
    
    # Login endpoint (stricter rate limiting)
    location ~ ^/auth|^/_stcore/session {
        limit_req zone=auth_limit burst=2 nodelay;
        
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ ~$ {
        deny all;
    }
}
```

### Enable Site (Linux)

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/cognidata /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Enable Site (macOS)

Edit `/usr/local/etc/nginx/nginx.conf` and add:
```nginx
include /usr/local/etc/nginx/sites-enabled/*;
```

Then:
```bash
# Create sites directories if they don't exist
mkdir -p /usr/local/etc/nginx/sites-enabled
mkdir -p /usr/local/etc/nginx/sites-available

# Move config
cp /usr/local/etc/nginx/cognidata.conf /usr/local/etc/nginx/sites-available/
ln -s /usr/local/etc/nginx/sites-available/cognidata /usr/local/etc/nginx/sites-enabled/

# Test
nginx -t

# Reload
nginx -s reload
```

---

## Part 4: Run Streamlit

Streamlit should run on localhost only (Nginx proxies to it):

```bash
# Disable external access
streamlit run app.py --server.address=127.0.0.1 --server.port=8501

# Or configure in ~/.streamlit/config.toml
# [server]
# address = "127.0.0.1"
# port = 8501
```

---

## Part 5: Troubleshooting

### Nginx Status
```bash
# Check if running
sudo systemctl status nginx

# View logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/cognidata_access.log

# Test configuration
sudo nginx -t
```

### SSL Certificate Issues
```bash
# Check certificate expiration
sudo openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -noout -dates

# Manual renewal (Let's Encrypt)
sudo certbot renew --dry-run
sudo certbot renew

# View active certificates
sudo certbot certificates
```

### Connection Issues
```bash
# Test upstream connection
curl http://127.0.0.1:8501

# Check open ports
sudo netstat -tulpn | grep nginx

# Verify DNS
nslookup yourdomain.com
```

### Rate Limiting Too Strict
Adjust in Nginx config:
```nginx
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/m;  # Increase from 5
limit_req zone=auth_limit burst=5 nodelay;  # Increase from 2
```

---

## Part 6: Security Checklist

✅ **Configuration:**
- [ ] HTTPS enforced (HTTP→HTTPS redirect)
- [ ] TLS 1.2+ only (no SSLv3, TLS 1.0, 1.1)
- [ ] Strong ciphers configured
- [ ] Security headers set (HSTS, CSP, X-Frame-Options)
- [ ] SSL certificate valid and not self-signed (production)

✅ **Nginx Hardening:**
- [ ] Nginx runs as unprivileged user (`www-data` or `nginx`)
- [ ] Config files readable only by owner
- [ ] Access/error logs rotated (logrotate)
- [ ] Rate limiting enabled on auth endpoints
- [ ] Sensitive paths blocked (`/. , ~/~`)

✅ **Streamlit Hardening:**
- [ ] Listens on 127.0.0.1 only (not 0.0.0.0)
- [ ] Accessible only via Nginx proxy
- [ ] No direct internet exposure
- [ ] Admin password strong (12+ chars, mixed case, special)
- [ ] AUTH_SECRET_KEY configured (32+ chars)

✅ **Firewall Rules:**
- [ ] Port 80 (HTTP) open to world
- [ ] Port 443 (HTTPS) open to world
- [ ] Port 8501 (Streamlit) closed to world (localhost only)
- [ ] SSH (22) open only to trusted IPs

---

## Part 7: Certificate Renewal

### Automatic Renewal (Let's Encrypt)

Certbot creates cron job automatically:
```bash
# View cron job
sudo crontab -l

# Manual renewal
sudo certbot renew --force-renewal

# Reload Nginx after renewal
sudo systemctl reload nginx
```

### Certificate Pre-Expiration Notification

Add to crontab:
```bash
# Check 30 days before expiration
0 0 * * * certbot renew --quiet && systemctl reload nginx && mail -s "Cert renewal" admin@example.com
```

---

## Part 8: Performance Tuning

### Compression
Add to `http` block in nginx.conf:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1024;
gzip_comp_level 6;
```

### Caching
Add to server block:
```nginx
location ~* \.(css|js|gif|jpg|jpeg|png)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### Connection Pool (for Streamlit WebSocket)
```nginx
upstream streamlit {
    server 127.0.0.1:8501;
    keepalive 32;
}

location / {
    proxy_pass http://streamlit;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}
```

---

## Part 9: Monitoring

### Certificate Expiration
```bash
# Get 30-day warning email from Let's Encrypt (default)
# Manual check:
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Nginx Status
```bash
# Enable status module (add to Nginx config)
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}

# Monitor
curl http://127.0.0.1/nginx_status
```

### SSL Labs Test
Visit: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com

Goal: **A** rating or higher

---

## Part 10: Production Deployment Checklist

```bash
# 1. Install Nginx and Certbot
sudo apt-get install nginx certbot python3-certbot-nginx

# 2. Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# 3. Configure Nginx (use config above)
sudo nano /etc/nginx/sites-available/cognidata

# 4. Enable site
sudo ln -s /etc/nginx/sites-available/cognidata /etc/nginx/sites-enabled/

# 5. Test
sudo nginx -t

# 6. Reload
sudo systemctl reload nginx

# 7. Verify HTTPS works
curl https://yourdomain.com

# 8. Run Streamlit on localhost only
streamlit run app.py --server.address=127.0.0.1 --server.port=8501 &

# 9. Test end-to-end
curl https://yourdomain.com/
# Should see Streamlit app

# 10. Check SSL rating
# Visit https://www.ssllabs.com/ssltest/
```

---

## References

- **Nginx Documentation**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/
- **OWASP Security Headers**: https://owasp.org/www-project-secure-headers/
- **Mozilla SSL Configuration Generator**: https://ssl-config.mozilla.org/
- **GDPR Article 32**: https://gdpr-info.eu/art-32-gdpr/

---

## Support

For issues:
1. Check Nginx error log: `sudo tail -f /var/log/nginx/error.log`
2. Verify upstream (Streamlit): `curl http://127.0.0.1:8501`
3. Test configuration: `sudo nginx -t`
4. Check certificate: `openssl x509 -in /path/to/cert -noout -dates`
5. Run `certbot renew --dry-run` to test renewal

---

**Security Summary:**
- ✅ HTTPS enforced (GDPR Article 32)
- ✅ TLS 1.2+ only (no weak ciphers)
- ✅ Security headers configured
- ✅ Rate limiting at proxy layer
- ✅ Streamlit hidden from direct access
- ✅ SSL auto-renewal configured
