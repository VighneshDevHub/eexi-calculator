# Deployment Guide - EEXI Calculator

This guide provides instructions for deploying the EEXI Calculator to production environments. As a Flask-based application, it can be hosted on various platforms.

## 1. Prerequisites
- Python 3.12+
- A production-ready WSGI server (like **Gunicorn** or **Waitress**)
- Access to a hosting provider (e.g., **Render**, **Railway**, **PythonAnywhere**, or a **VPS**)

---

## 2. Deployment to Render (Recommended Free Tier)
Render is an excellent choice for hosting this project due to its ease of use and native support for Python.

### Step-by-Step:
1. **Push Code to GitHub**:
   Ensure your project is in a GitHub repository.
2. **Create a New Web Service**:
   Log in to Render, click "New" -> "Web Service", and connect your repository.
3. **Configure Settings**:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. **Environment Variables**:
   Add any necessary environment variables in the Render dashboard (e.g., `FLASK_ENV=production`).
5. **Database**:
   Since the app uses SQLite, the database file (`vessels.db`) will be created in the `instance/` folder. Note that on Render's free tier, disk storage is ephemeral. For persistent data across redeployments, consider using Render's "Blueprints" with a Disk mount or a managed PostgreSQL database.

---

## 3. Deployment to PythonAnywhere
Ideal for hosting simple Flask apps with persistent storage.

### Step-by-Step:
1. **Upload Files**: Use the "Files" tab or `git clone` via the Bash console.
2. **Setup Virtualenv**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 my-venv
   pip install -r requirements.txt
   ```
3. **Configure Web Tab**:
   - Create a new web app using the "Manual Configuration" option.
   - Point the **WSGI configuration file** to your `app.py`.
   - Set the path to your virtual environment.
4. **Reload**: Click the "Reload" button on the Web tab.

---

## 4. Production Server Considerations

### WSGI Server
Do **NOT** use the built-in Flask development server (`app.run()`) in production. Instead, use:
- **Linux**: `gunicorn -w 4 -b 0.0.0.0:8000 app:app`
- **Windows**: `waitress-serve --port=8000 app:app`

### Security Checklist
- [ ] Set `debug=False` in `app.py`.
- [ ] Use a strong `SECRET_KEY` if using sessions.
- [ ] Ensure `instance/` and `reports/generated/` folders have proper write permissions.
- [ ] Configure a firewall to only allow traffic on necessary ports (80/443).

### Static Files
For optimal performance, use a reverse proxy like **Nginx** or **Apache** to serve the `static/` folder and proxy other requests to the WSGI server.

---

## 5. Maintenance
- **Backups**: Regularly backup the `instance/vessels.db` file.
- **Cleanup**: Periodically clear the `reports/generated/` folder to save disk space, or implement an automated cleanup script.

---
*Goltens EEXI Calculator - Production Deployment Standards.*
