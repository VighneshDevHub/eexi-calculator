# How to Run the Application

This guide walks you through running the Maritime Compliance Suite on your local machine!

---

## 🚀 Option 1: Quick Start with Docker Compose (Easiest)

### Prerequisites:
- Docker and Docker Compose installed on your machine

### Step 1: Clone the Repository
```bash
cd "c:\Users\vighn\Desktop\STAY-HARD\Goltens-Internship\Project 1\eexi-calculator"
```

### Step 2: Start All Services
Run this command in your terminal:
```bash
docker-compose up -d --build
```

This will automatically:
- Build the backend and frontend Docker images
- Start a PostgreSQL database
- Launch the Flask backend on port 5000
- Launch the Next.js frontend on port 3000

### Step 3: Verify the Application is Running
- Open your browser and go to: **http://localhost:3000** (frontend)
- Verify the backend is working: **http://localhost:5000/health**

### Step 4: Stop the Application (when you're done)
```bash
docker-compose down
```

---

## 💻 Option 2: Run Locally Without Docker (Development Mode)

### Prerequisites:
- Python 3.11+
- Node.js 18+ and npm
- A code editor (like VS Code)

### Part 1: Set Up the Backend

1. **Open a new terminal and navigate to the backend directory**:
   ```bash
   cd "c:\Users\vighn\Desktop\STAY-HARD\Goltens-Internship\Project 1\eexi-calculator\backend"
   ```

2. **Create a virtual environment (recommended)**:
   - Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - Linux/macOS (Bash):
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env` (we'll use the default settings for development):
     ```bash
     # Windows PowerShell
     Copy-Item .env.example -Destination .env
     
     # Linux/macOS
     cp .env.example .env
     ```

5. **Start the backend server**:
   ```bash
   python main.py
   ```
   The backend will be running on **http://localhost:5000**

### Part 2: Set Up the Frontend

1. **Open another terminal and navigate to the frontend directory**:
   ```bash
   cd "c:\Users\vighn\Desktop\STAY-HARD\Goltens-Internship\Project 1\eexi-calculator\frontend"
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   - Create a `.env.local` file in the frontend directory with:
     ```
     NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
     ```

4. **Start the frontend development server**:
   ```bash
   npm run dev
   ```
   The frontend will be available on **http://localhost:3000**

---

## 📖 How to Use the Application

Now that the app is running, you can:

1. **EEXI Calculator** - Calculate the Energy Efficiency Existing Ship Index for vessels
2. **CII Calculator** - Calculate the Carbon Intensity Indicator
3. **EGBP Calculator** - Calculate Exhaust Gas Back Pressure
4. **Pipe Wall Thickness Calculator** - Calculate pipe wall thickness requirements
5. **Linear Interpolator** - Perform linear interpolation calculations
6. **History** - View past calculations
7. **Admin Dashboard** - View stats and all history (for admin use)

---

## 🔍 Troubleshooting Common Issues

### Backend Won't Start:
- Check if port 5000 is already in use by another app
- Make sure your virtual environment is activated
- Verify all dependencies installed correctly with `pip list`

### Frontend Won't Connect to Backend:
- Verify the backend is running on http://localhost:5000
- Check that your `NEXT_PUBLIC_API_BASE_URL` in `.env.local` is correct
- Look for CORS errors in your browser's developer console

### Docker Issues:
- Make sure Docker Desktop is running (on Windows/macOS)
- Try restarting Docker
- Run `docker-compose down` then `docker-compose up -d` again

### Database Issues (Docker):
- The database data is stored in a Docker volume - it will persist even after `docker-compose down`
- To completely reset everything (including the database), run:
  ```bash
  docker-compose down -v
  ```

---

## 📂 Project Structure Recap

```
eexi-calculator/
├── backend/           # Flask backend application
│   ├── app/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── frontend/          # Next.js frontend application
│   └── src/app/
├── docker/            # Dockerfiles
├── docs/              # Documentation
├── .env.example       # Example environment variables
└── docker-compose.yml # Docker Compose configuration
```
