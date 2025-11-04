# Simple Email Client

<div align="center">

A minimalist, self-hosted email client built with FastAPI, MongoDB, and Resend webhooks.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## Overview

Simple Email Client is a lightweight, self-hosted email management solution designed for individuals and small teams who want complete control over their email infrastructure. Built with modern technologies and a focus on simplicity, it provides a clean interface for receiving, viewing, and replying to emails through the Resend API.

### Why Simple Email Client?

- **Complete Control**: Self-hosted solution with no vendor lock-in
- **Privacy First**: Your emails stay on your infrastructure
- **Easy Setup**: 5-minute setup with an intuitive first-time wizard
- **Clean Interface**: Minimalist design focused on productivity
- **Multi-User**: Support for multiple users with role-based access
- **API Driven**: All settings configurable through web interface

---

## Features

### Core Functionality
- **Email Management**: Receive, view, reply, and delete emails
- **Attachment Support**: Store email attachments in Cloudflare R2
- **Search & Filter**: Find emails quickly (coming soon)
- **Real-time Updates**: Webhook-based email reception from Resend

### Authentication & Security
- **Simple Authentication**: Username and password-based login
- **Multi-User Support**: Create and manage multiple user accounts
- **Role-Based Access**: Admin and regular user roles
- **Secure Sessions**: Session-based authentication with secure cookies
- **Password Hashing**: SHA256 password hashing

### Administration
- **First-Time Setup Wizard**: Easy initial configuration
- **Settings Panel**: Configure all API keys through web interface
- **User Management**: Create, view, and delete users
- **API Configuration**: Manage Resend and Cloudflare R2 settings

### Technical Highlights
- **Modern Stack**: FastAPI, MongoDB, Jinja2 templates
- **Docker Ready**: Complete Docker and Docker Compose support
- **Minimalist UI**: Clean design with no unnecessary elements
- **REST API**: Well-structured API endpoints
- **Database Driven**: All settings stored in MongoDB

---

## Quick Start

### Prerequisites

Before you begin, ensure you have:
- **Docker & Docker Compose** (recommended) OR **Python 3.9+**
- **MongoDB** instance (local or remote)
- **Resend Account** ([Sign up free](https://resend.com))
- **Cloudflare R2** (optional, for attachments)

### Installation (Docker - Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/simple-email-client.git
   cd simple-email-client
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables**

   Edit `.env` file:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=email_client
   SECRET_KEY=your-random-secret-key-here
   ```

   Generate a secure secret key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Start the application**
   ```bash
   docker-compose up -d
   ```

5. **Access the application**

   Open your browser and navigate to: `http://localhost:8000`

6. **Complete the setup wizard**
   - Create your admin account (username, email, password)
   - Navigate to Settings
   - Add your Resend API key
   - (Optional) Configure Cloudflare R2 credentials for attachments

**That's it!** Your email client is now ready to use.

### Installation (Manual)

If you prefer running without Docker:

1. **Clone and navigate**
   ```bash
   git clone https://github.com/yourusername/simple-email-client.git
   cd simple-email-client
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access and setup**

   Navigate to `http://localhost:8000` and complete the setup wizard.

---

## Configuration

### Setting Up Resend Webhook

After deploying your application, configure Resend to forward emails:

1. Go to [Resend Webhooks](https://resend.com/webhooks)
2. Click **"Add Webhook"**
3. Enter your webhook URL: `https://your-domain.com/webhook/email`
4. Select the **"email.received"** event
5. Click **"Save"**

Now all emails sent to your Resend domain will be forwarded to your email client.

### Configuring API Keys

All API keys are configured through the web interface:

1. Log in as an admin user
2. Click **"Settings"** in the top navigation
3. Fill in your API credentials:
   - **Resend API Key** (required for sending replies)
   - **Cloudflare R2** credentials (optional, for attachments)
4. Click **"Save API Settings"**

### Environment Variables

Only three environment variables are required:

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `MONGODB_URI` | MongoDB connection string | Yes | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | Yes | `email_client` |
| `SECRET_KEY` | Session secret key | Yes | Generate with Python `secrets` |

All other settings (Resend API, Cloudflare R2) are configured via the web interface.

---

## Usage

### Creating Your First User

When you first access the application, you'll see the setup wizard:

1. Enter a username (will be used for login)
2. Enter an email address
3. Choose a strong password
4. Confirm your password
5. Click **"Create Admin Account"**

You'll be automatically logged in and redirected to Settings.

### Managing Users

Admin users can create and manage other users:

1. Go to **Settings**
2. Scroll to **"User Management"** section
3. Fill in the new user details:
   - Username
   - Email
   - Password
   - Admin privileges (checkbox)
4. Click **"Create User"**

To delete a user, click the **"Delete"** button next to their name in the user table.

### Viewing Emails

- **Inbox**: All received emails are displayed on the main page
- **Unread**: Unread emails are shown in bold
- **Attachments**: Emails with attachments show a badge with count
- **Replied**: Emails you've replied to show a "Replied" badge

### Replying to Emails

1. Click on an email to view it
2. Scroll to the **"Reply"** section
3. Type your reply message
4. Click **"Send Reply"**

The email will be sent via your configured Resend API key.

---

## Project Structure

```
simple-email-client/
├── main.py                 # FastAPI application entry point
├── database.py             # MongoDB connection and collections
├── auth.py                 # Authentication and user management
├── email_service.py        # Resend API integration
├── r2_service.py           # Cloudflare R2 integration
├── templates/              # Jinja2 HTML templates
│   ├── setup.html          # Initial setup wizard
│   ├── login.html          # Login page
│   ├── inbox.html          # Email inbox
│   ├── email_view.html     # Single email view
│   └── settings.html       # Admin settings panel
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose orchestration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .dockerignore          # Docker ignore rules
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── DEPLOYMENT.md          # Detailed deployment guide
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/setup` | Initial setup page | No |
| `POST` | `/setup` | Create first admin user | No |
| `GET` | `/login` | Login page | No |
| `POST` | `/login` | Authenticate user | No |
| `GET` | `/logout` | Logout current user | Yes |

### Email Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | View inbox | Yes |
| `GET` | `/email/{id}` | View specific email | Yes |
| `POST` | `/email/{id}/reply` | Reply to email | Yes |
| `DELETE` | `/email/{id}` | Delete email | Yes |

### Admin Settings

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/settings` | Settings panel | Admin |
| `POST` | `/settings/api` | Update API config | Admin |
| `POST` | `/settings/users` | Create new user | Admin |
| `DELETE` | `/settings/users/{username}` | Delete user | Admin |

### Webhook

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/webhook/email` | Receive emails from Resend | No (webhook) |

---

## Deployment

### Production Deployment

For production environments, we recommend:

1. **Use HTTPS**: Always use SSL/TLS in production
2. **Reverse Proxy**: Use Nginx or Caddy as a reverse proxy
3. **Secure MongoDB**: Enable authentication and use strong passwords
4. **Regular Backups**: Schedule regular MongoDB backups
5. **Update Dependencies**: Keep all dependencies up to date

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

### Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Reverse Proxy Examples

**Nginx:**
```nginx
server {
    listen 80;
    server_name mail.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Caddy (with auto HTTPS):**
```
mail.yourdomain.com {
    reverse_proxy localhost:8000
}
```

---

## Security

### Best Practices

- **Strong Passwords**: Enforce strong passwords for all users
- **Secure Secret Key**: Use a cryptographically secure random key
- **HTTPS Only**: Never run in production without HTTPS
- **Regular Updates**: Keep dependencies and Docker images updated
- **MongoDB Security**: Use authentication and restrict network access
- **Backup Strategy**: Implement regular automated backups

### Password Reset

If you need to reset an admin password:

```bash
docker exec -it email-client python -c "
from database import users_collection
from auth import hash_password
users_collection.update_one(
    {'username': 'admin'},
    {'\$set': {'password': hash_password('newpassword')}}
)
print('Password reset successfully')
"
```

---

## Troubleshooting

### Common Issues

**Container won't start**
```bash
# Check logs
docker-compose logs

# Common fixes:
# - Verify .env file exists and is configured
# - Check if port 8000 is available
# - Verify MongoDB connection
```

**Can't connect to MongoDB**
```bash
# Test connection
docker exec -it email-client python -c "from database import client; print(client.server_info())"
```

**Webhook not receiving emails**
- Verify webhook URL is publicly accessible
- Check Resend webhook configuration
- Ensure webhook event is set to "email.received"
- Check application logs for errors

**Emails not sending**
- Verify Resend API key is configured in Settings
- Check Resend dashboard for quota limits
- Review application logs for error messages

For more troubleshooting tips, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Development

### Setting Up Development Environment

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure `.env` file
6. Run: `python main.py`

### Running Tests

```bash
# Coming soon
pytest
```

### Code Style

This project follows PEP 8 guidelines. Format your code with:

```bash
black .
flake8 .
```

---

## Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- **Report Bugs**: Open an issue with details about the bug
- **Suggest Features**: Share your ideas for new features
- **Improve Documentation**: Help make the docs better
- **Submit Pull Requests**: Fix bugs or add features

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

Please ensure your PR:
- Follows existing code style
- Includes appropriate tests (when applicable)
- Updates documentation if needed
- Has a clear description of changes

---

## Support

### Getting Help

- **Documentation**: Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides
- **Issues**: Open a [GitHub issue](https://github.com/yourusername/simple-email-client/issues)
- **Bug Reports**: Use the issue tracker with the bug label

### Community

- Star this repository if you find it useful
- Share with others who might benefit
- Contribute to make it better

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Simple Email Client Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## Acknowledgments

- **FastAPI**: Modern, fast web framework for Python
- **MongoDB**: Flexible document database
- **Resend**: Email API for developers
- **Cloudflare R2**: Object storage for attachments

---

## Screenshots

*Coming soon - screenshots of the application interface*

---

<div align="center">

### Part of [Projexa AI](https://projexa.ai) Open Source Initiative

Built with ❤️ by the open-source community

**[Back to Top](#simple-email-client)**

</div>
