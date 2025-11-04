# Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)
- MongoDB instance (local or remote)

### Initial Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/yourusername/simple-email-client.git
   cd simple-email-client
   ```

2. Create `.env` file from example:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and configure:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=email_client
   SECRET_KEY=your-random-secret-key-here
   ```

   **Generate a secure secret key:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. Build and start the container:
   ```bash
   docker-compose up -d
   ```

5. Access the application at `http://localhost:8000`

6. Complete the initial setup wizard:
   - Create your admin account
   - Go to Settings
   - Add your Resend API key
   - (Optional) Configure Cloudflare R2 credentials

### Deploy with Docker (without compose)

```bash
# Build the Docker image
docker build -t email-client:latest .

# Run the container
docker run -d \
  --name email-client \
  -p 8000:8000 \
  -e MONGODB_URI="mongodb://localhost:27017" \
  -e DATABASE_NAME="email_client" \
  -e SECRET_KEY="your-secret-key" \
  email-client:latest
```

## Production Deployment

### Using a Reverse Proxy (Recommended)

It's recommended to use a reverse proxy like Nginx or Caddy in production:

**Nginx example:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Caddy example (with automatic HTTPS):**
```
your-domain.com {
    reverse_proxy localhost:8000
}
```

### Environment Variables

**Required Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `email_client` |
| `SECRET_KEY` | Session secret key | Generate with `secrets.token_hex(32)` |

**API Configuration (via Web Interface):**
- Resend API Key
- Cloudflare R2 Account ID
- Cloudflare R2 Access Key ID
- Cloudflare R2 Secret Access Key
- Cloudflare R2 Bucket Name
- Cloudflare R2 Public URL

### Configuring Resend Webhook

After deploying your application:

1. Go to https://resend.com/webhooks
2. Click "Add Webhook"
3. Enter your webhook URL: `https://your-domain.com/webhook/email`
4. Select the "email.received" event
5. Save the webhook

### Security Best Practices

1. **Use a strong secret key:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Secure MongoDB:**
   - Use authentication
   - Don't expose MongoDB port publicly
   - Use strong passwords

3. **Use HTTPS:**
   - Always use HTTPS in production
   - Caddy provides automatic HTTPS
   - For Nginx, use Let's Encrypt with Certbot

4. **Regular backups:**
   - Backup your MongoDB database regularly
   - Store backups securely

5. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

## Monitoring and Maintenance

### View Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f email-client
```

### Check Container Status

```bash
# Docker Compose
docker-compose ps

# Docker
docker ps
```

### Restart Application

```bash
# Docker Compose
docker-compose restart

# Docker
docker restart email-client
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs
```

Common issues:
- Missing or invalid environment variables
- Port 8000 already in use
- MongoDB connection issues

### Can't connect to MongoDB

Test MongoDB connection:
```bash
docker exec -it email-client python -c "from database import client; print(client.server_info())"
```

### Webhook not receiving emails

1. Verify webhook URL is accessible from the internet
2. Check Resend webhook configuration
3. Check application logs for errors
4. Ensure Resend API key is configured in Settings

### Can't log in after setup

1. Check if users exist in database:
   ```bash
   docker exec -it email-client python -c "from database import users_collection; print(list(users_collection.find()))"
   ```

2. Reset admin password (if needed):
   ```bash
   docker exec -it email-client python -c "
   from database import users_collection
   from auth import hash_password
   users_collection.update_one(
       {'username': 'admin'},
       {'\$set': {'password': hash_password('newpassword')}}
   )
   print('Password updated')
   "
   ```

## Scaling

For production deployments with high traffic:

1. **Use a production WSGI server:**
   - Already using uvicorn (production-ready)
   - Can add Gunicorn for better process management

2. **MongoDB replica set:**
   - Set up MongoDB replica set for high availability
   - Update MONGODB_URI to include all replica set members

3. **Load balancing:**
   - Use multiple application instances
   - Add a load balancer (nginx, HAProxy)

4. **Caching:**
   - Add Redis for session storage
   - Cache frequently accessed data

## Backup and Restore

### Backup MongoDB

```bash
mongodump --uri="mongodb://localhost:27017" --db=email_client --out=/backup/$(date +%Y%m%d)
```

### Restore MongoDB

```bash
mongorestore --uri="mongodb://localhost:27017" --db=email_client /backup/20240101/email_client
```

## Health Checks

Add health check endpoint monitoring:

```bash
# Check if application is running
curl http://localhost:8000/

# Should return HTML (status 200)
```

## Support

For issues and questions:
- Check the logs first
- Review this deployment guide
- Open an issue on GitHub
