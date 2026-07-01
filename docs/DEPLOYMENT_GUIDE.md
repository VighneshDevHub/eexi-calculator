# Deployment Guide - Maritime Compliance Suite

This guide provides instructions for deploying the Maritime Compliance Suite to production environments.

---

## 📋 Prerequisites

### Local Development:
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### Production:
- A server with Docker and Docker Compose installed
- A domain name (optional but recommended)
- SSL certificate (for HTTPS)

---

## 🐳 Quick Start with Docker Compose (Recommended)

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd eexi-calculator
```

### Step 2: Configure Environment Variables
Copy the example environment file and customize it:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
FLASK_ENV=production
SECRET_KEY=your-strong-secret-key-here
DATABASE_URI=postgresql://user:password@postgres:5432/eexi_db
CORS_ALLOWED_ORIGINS=https://your-domain.com,http://localhost:3000
RATE_LIMIT_DEFAULT=200 per minute
```

### Step 3: Start All Services
```bash
docker-compose up -d --build
```

This will start:
- PostgreSQL database
- Flask backend API (port 5000)
- Next.js frontend (port 3000)

### Step 4: Verify Deployment
Check that all containers are running:
```bash
docker-compose ps
```

Verify the health endpoints:
- Backend health: `http://localhost:5000/health`
- Frontend: `http://localhost:3000`

---

## 🏗️ Manual Deployment (Without Docker)

### Backend Setup (Flask)

1. **Navigate to the backend directory**:
```bash
cd backend
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize the database**:
```bash
python3 -c "from app.database.db import db, init_db; from main import app; init_db(app); with app.app_context(): db.create_all()"
```

6. **Start the backend server**:
- Development:
  ```bash
  python main.py
  ```
- Production (with Gunicorn):
  ```bash
  gunicorn --config app/gunicorn_config.py main:app
  ```

### Frontend Setup (Next.js)

1. **Navigate to the frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment variables**:
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

4. **Build and start the frontend**:
- Development:
  ```bash
  npm run dev
  ```
- Production:
  ```bash
  npm run build
  npm start
  ```

---

## 🔒 Production Security Best Practices

### 1. Environment Variables
Always use environment variables for sensitive information:
- `SECRET_KEY`: Use a strong, randomly generated secret key
- `DATABASE_URI`: Never hardcode database credentials
- `FLASK_ENV`: Set to `production` in production

### 2. HTTPS
Always use HTTPS in production:
- Use Let's Encrypt for free SSL certificates
- Configure Nginx or a reverse proxy to handle SSL termination

### 3. Database Security
- Use PostgreSQL instead of SQLite for production
- Enable database backups
- Restrict database access to trusted networks only

### 4. Rate Limiting
The application has built-in rate limiting, ensure it's enabled in production:
- Default: 200 requests per minute
- Configure via `RATE_LIMIT_DEFAULT` environment variable

### 5. CORS Configuration
Restrict CORS origins to only trusted domains:
```env
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 6. Container Security
- Use non-root users in Docker containers (already configured)
- Keep base images up to date
- Scan images for vulnerabilities

---

## 📊 Monitoring & Maintenance

### Logs
View logs with Docker Compose:
```bash
docker-compose logs -f
```

### Backups
- **Database**: Regularly backup the PostgreSQL database
- **Reports**: Backup the `backend/app/reports/generated` directory

### Upgrades
To update to the latest version:
```bash
git pull
docker-compose down
docker-compose up -d --build
```

---

## 🚀 Deployment Platforms

### Option 1: Docker Swarm / Kubernetes
For high availability and scalability, use orchestration:
- Docker Swarm (simple)
- Kubernetes (advanced)

### Option 2: Cloud Providers
- **AWS**: ECS, EKS, or Lightsail
- **GCP**: Cloud Run or GKE
- **Azure**: App Service or ACI
- **Render**: Managed Docker deployments (simple)

### Option 3: VPS (DigitalOcean, Linode, etc.)
Follow the Docker Compose guide on any VPS provider!

---

## 🚨 Troubleshooting

### Common Issues:
1. **Backend not starting**: Check logs with `docker-compose logs backend`
2. **Database connection issues**: Verify DATABASE_URI is correct
3. **Frontend API errors**: Check NEXT_PUBLIC_API_BASE_URL is pointing to the correct backend
4. **Permission errors**: Ensure Docker has proper permissions

### Getting Help:
Check the logs first! Most issues can be diagnosed by looking at the container logs!
