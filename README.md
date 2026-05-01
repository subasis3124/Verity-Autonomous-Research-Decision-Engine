# Verity: Autonomous AI Research Engine

<p align="center">
  <em>A full-stack, cross-platform autonomous workflow agent that breaks down complex user queries, independently conducts LLM-based research, and synthesizes the findings into highly structured markdown reports.</em>
</p>

## 🚀 Overview

**Verity** is an autonomous agentic research pipeline. Unlike standard chatbots that provide immediate shallow responses, Verity acts as a "thinker". It ingests complex questions, deconstructs them into actionable sub-questions, autonomously executes multiple targeted inferences against deep reasoning LLMs, and synthesizes the data into a comprehensive report.

The system is fully cross-platform with distinct premium user interfaces built for Web and Mobile, all communicating with a real-time async backend.

## 🛠 Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy (Async), PostgreSQL (Neon Serverless)
- **AI Engine:** Groq API (`llama-3.1-8b-instant` / `llama-3.3-70b-versatile` multi-step pipeline)
- **Frontend (Web):** React.js, Vite, Axios
- **Frontend (Mobile):** Flutter, Dart, Provider State Management
- **Security:** Standard JWT (JSON Web Tokens) with hashed password local-auth validation

## ✨ Features

- **Agentic Decomposer:** Autonomously splits heavy queries into a targeted search tree.
- **Asynchronous Background Processing:** Employs FastAPI `BackgroundTasks` to ensure non-blocking HTTP threading while LLMs conduct multi-minute inferences.
- **Resilient AI Pipeline:** Implements intelligent exponential back-off and 429 Rate Limit recovery.
- **Real-Time Web Dashboard:** Web client autonomously polls pipeline progressions, transitioning badges dynamically from *Processing* -> *Completed*.
- **Cross-Platform State Synchronization:** Web and Android Mobile apps securely maintain JWT session states against the same universal Neon PostgreSQL database.

---

## 💻 Local Installation & Setup

You will need three terminal windows to run this application fully locally. Ensure you have Python 3.10+, Node.js, and the Flutter SDK installed.

### 1. Database & Environment Setup
Ensure you configure a `.env` file in your root folder or inside `/backend`:
```env
DATABASE_URL=postgresql+asyncpg://<YOUR_NEON_DB_URL>
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
SECRET_KEY=<YOUR_JWT_SECRET>
```

### 2. Running the Backend (FastAPI)
Open Terminal 1:
```bash
# Navigate to backend
cd backend

# Create & activate a virtual environment
python -m venv veritynv
.\veritynv\Scripts\activate   # Windows
# source veritynv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Boot the uvicorn server
uvicorn main:app --port 8000
```
*The API will be available at `http://127.0.0.1:8000` and Swagger docs at `http://127.0.0.1:8000/docs`.*

### 3. Running the Web App (React)
Open Terminal 2:
```bash
# Navigate to frontend
cd frontend

# Install node modules
npm install

# Start the Vite development server
npm run dev
```
*The web app will be available at `http://localhost:5173`.*

### 4. Running the Mobile App (Flutter)
Open Terminal 3:
```bash
# Navigate to mobile app
cd verity_mobile

# Fetch packages
flutter pub get

# Run on a connected Android device or Web emulator
flutter run
```
*(Note for Mobile Physical testing: Update `api_client.dart` to target your computer's local Wi-Fi IP address instead of 10.0.2.2)*

---

### Author
Designed and developed from scratch as a demonstration of production-grade Full-Stack Architecture, cross-platform UI integration, and Applied LLM Agentic workflows.
