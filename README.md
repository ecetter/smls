# SMLS - Social Media Login Service

A secure OAuth 2.0 authentication service supporting Google and LinkedIn login.

## 🚀 Quick Start

**Just 2 commands:**

```bash
# 1. Set your URL
export BASE_URL='http://yourdomain.com/your/path'

# 2. Run setup
./setup-and-launch.sh
```

**That's it!** The script automatically:
- ✅ Creates Python environment and installs dependencies
- ✅ Sets up nginx configuration (clean URLs when possible)
- ✅ Launches SMLS with reverse proxy

## 📋 Examples

### Any URL Works (No Root Required)
```bash
export BASE_URL='http://emeryetter.com/sweng861/smls'
./setup-and-launch.sh
```
**Result**: `http://emeryetter.com:8080/sweng861/smls` (script adds port automatically)

### Simple Domain
```bash
export BASE_URL='http://mydomain.com'
./setup-and-launch.sh
```
**Result**: `http://mydomain.com:8080` (script adds port automatically)

### With Port Already Specified
```bash
export BASE_URL='http://localhost:8080/myapp'
./setup-and-launch.sh
```
**Result**: `http://localhost:8080/myapp` (uses specified port)

## 🔧 Management

```bash
# Check status
./persist/manage.sh status

# View logs
./persist/manage.sh logs

# Stop SMLS
./persist/manage.sh stop

# Restart SMLS
./persist/manage.sh restart
```

## 🔐 OAuth Setup

After setup, update your OAuth apps with these URLs:

- **Google**: `{BASE_URL}/auth/google/callback`
- **LinkedIn**: `{BASE_URL}/auth/linkedin/callback`

**Example**: If BASE_URL is `http://emeryetter.com/sweng861/smls`:
- Google: `http://emeryetter.com/sweng861/smls/auth/google/callback`
- LinkedIn: `http://emeryetter.com/sweng861/smls/auth/linkedin/callback`

## 🆘 Troubleshooting

### SMLS Won't Start
```bash
./persist/manage.sh logs
```

### Port Conflicts
```bash
lsof -i :8080  # Check port 8080
lsof -i :5000  # Check port 5000
```

### Want Clean URLs?
The script automatically adds port 8080 for user-level deployment. For clean URLs without ports, you'll need to set up a reverse proxy or port forwarding at the system level.

## 📁 What Gets Created

```
smls/
├── smls_env/                    # Python environment
├── nginx/                       # Nginx configuration
├── persist/                     # Background management
├── logs/                        # Application logs
└── setup-and-launch.sh         # Main setup script
```

## 💡 Tips

- **No Root Required**: All URLs work without elevated privileges
- **Automatic Ports**: Script adds port 8080 automatically
- **Development**: Use `localhost` or `localhost:8080`
- **Production**: Use your actual domain

## 🔄 Re-running Setup

The script is safe to run multiple times - it will update existing installations.

---

**That's it!** Simple, clean, and everything you need in one place.