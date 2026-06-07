# Deployment Guide - Maritime Compliance Suite

This guide provides instructions for deploying the Maritime Compliance Suite to production environments.

## ☁️ Option 1: Render (Recommended)

1. **Prepare the Repository**: Ensure `requirements.txt` is up-to-date and `app.py` is configured for production.
2. **Create Web Service**:
   - Connect your GitHub repository to Render.
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
3. **Database**:
   - The application uses SQLite by default, which is suitable for small deployments.
   - For persistent storage on Render, use **Render Disks** to mount the `/database` directory.

## 🐳 Option 2: Docker

1. **Build Image**:
   ```bash
   docker build -t maritime-suite .
   ```
2. **Run Container**:
   ```bash
   docker run -d -p 5000:5000 --name maritime-suite maritime-suite
   ```

## 🖥️ Option 3: Traditional Linux Server (Ubuntu/Nginx)

1. **Install System Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```
2. **Setup Application**:
   - Clone the repo and setup virtual environment.
   - Install dependencies.
3. **Setup Gunicorn**:
   - Create a systemd service file for Gunicorn.
4. **Configure Nginx**:
   - Create a reverse proxy configuration pointing to the Gunicorn socket.

## 🛡️ Security Best Practices
- **SECRET_KEY**: Set a strong `SECRET_KEY` in environment variables.
- **HTTPS**: Always use SSL/TLS in production.
- **Database Backups**: Regularly backup the `vessels.db` file.
- **Debug Mode**: Ensure `debug=False` in production.
