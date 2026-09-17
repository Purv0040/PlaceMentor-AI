# PlaceMentor AI — Backend Service

The backend API server for PlaceMentor AI, built with **Node.js, Express, MongoDB Atlas, Mongoose, JWT, and Multer**.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd Backend
npm install
```

### 2. Configure MongoDB Atlas
Open `Backend/.env` and update `MONGODB_URI` with your MongoDB Atlas cluster connection string:
```env
PORT=8000
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/placementor_db?retryWrites=true&w=majority
JWT_SECRET=placementor_jwt_super_secret_key_2026
```

### 3. Run the Backend
- Development mode (with live reload):
  ```bash
  npm run dev
  ```
- Production mode:
  ```bash
  npm start
  ```

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` — Register a new student account (`{ name, email, password }`)
- `POST /api/auth/login` — Login (`{ email, password }`)
- `GET /api/auth/me` — Get authenticated user profile (`Bearer <token>`)

### Domains
- `GET /api/domains` — Retrieve available placement domains

### Reports & Analysis
- `POST /api/reports` — Orchestrate AI analysis & generate placement readiness report
- `GET /api/reports/:id` — Get report by ID
- `POST /api/reports/:id/roadmap` — Generate 4-week missing skill learning roadmap
- `GET /api/reports/:id/download` — Download report data
