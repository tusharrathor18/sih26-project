# Legal Metrology Compliance Inspection System

> **Problem Statement:** "Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels."

---

## 1. Project Objective & Vision
An automated, intelligent compliance inspection platform for **Legal Metrology Officers and Inspectors** to verify statutory label declarations on packaged commodities (MRP, net quantity, date of manufacture/import, consumer care details, country of origin, and manufacturer address) as mandated under the **Legal Metrology (Packaged Commodities) Rules, 2011**.

---

## 2. Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, React Router v6, Axios, Lucide Icons | High-performance officer interface |
| **Backend** | Python 3.13, Django 5.x, Django REST Framework (DRF) | Secure REST APIs & Authentication |
| **Database** | MySQL 8.0 (PyMySQL connector) | Relational persistence & officer profiles |
| **Future AI/CV** | OpenCV, PaddleOCR (Prompts 2+) | Image processing & OCR extraction pipeline |

---

## 3. Project Architecture & Monorepo Structure

```text
legal-metrology-compliance/
│
├── frontend/                     # React + Vite Client Application
│   ├── public/                   # Static browser assets
│   ├── src/
│   │   ├── components/           # ProtectedRoute & shared UI components
│   │   ├── context/              # AuthContext (token & profile management)
│   │   ├── pages/                # Login, Dashboard, Scan, History, Results
│   │   ├── services/             # Axios API client & endpoints
│   │   ├── styles/               # Component & global styling
│   │   ├── App.jsx               # Client-side router & route protection
│   │   └── main.jsx              # React DOM entry point
│   ├── package.json
│   └── vite.config.js
│
├── backend/                      # Django REST API Server
│   ├── venv/                     # Python Virtual Environment
│   ├── config/                   # Settings, WSGI/ASGI, URLs & PyMySQL setup
│   ├── users/                    # Officer authentication, OfficerProfile & roles
│   ├── scanner/                  # Commodity image upload & scan sessions (scaffold)
│   ├── compliance/               # Rules engine & compliance verification (scaffold)
│   ├── media/                    # Uploaded commodity images directory
│   ├── manage.py
│   └── requirements.txt
│
├── ml/                           # Computer Vision & OCR models (Future Prompts)
│   ├── models/
│   ├── datasets/
│   └── README.md
│
├── docs/                         # Specifications & Regulatory References
│   └── README.md
│
├── .gitignore                    # Git exclusions
├── .env.example                  # Environment variable reference template
└── README.md                     # System documentation
```

---

## 4. Officer Authentication & Security Architecture

### Strict Officer Login Flow (No Public Registration)
1. **Zero Public Signup:** Officer accounts can only be provisioned by Department Administrators or administrative seed commands.
2. **Profile Architecture:** Django `User` (credentials & password hashing) is linked one-to-one with `OfficerProfile` (Officer ID, designation, department, jurisdiction, active status).
3. **Multi-tier Validation:**
   - Officer ID existence check
   - Active status check (`is_active=True`)
   - Secure PBKDF2/Argon2 password hash verification
   - Token-based API authorization (`Token <key>`)
4. **Client-side Protected Routes:** `/dashboard`, `/scan`, `/history`, and `/results` strictly require valid officer tokens.

---

## 5. Setup & Installation Guide (Windows + VS Code)

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ & npm
- MySQL Server 8.0 running locally on port 3306

### Step 1: Database Setup
Open MySQL Workbench or MySQL Command Line and create the database:
```sql
CREATE DATABASE legal_metrology CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env` inside `backend/`:
```powershell
cd backend
copy .env.example .env
```
Update your MySQL password in `backend/.env`:
```env
DB_NAME=legal_metrology
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Step 3: Backend Setup with Virtual Environment
```powershell
cd backend

# Create virtual environment (if not already present)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed initial pre-authorized officer accounts
python manage.py seed_officers

# Start Django Development Server
python manage.py runserver
```

### Step 4: Frontend Setup (React + Vite)
Open a new terminal:
```powershell
cd frontend

# Install node dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## 6. Pre-Authorized Officer Accounts

| Officer ID | Role | Designation / Jurisdiction |
| :--- | :--- | :--- |
| `OFF-DEL-2024-001` | INSPECTOR | Senior Inspector, Delhi (Zone-1) |
| `OFF-MUM-2024-042` | INSPECTOR | Inspector, Mumbai (Zone-4) |
| `OFF-ADMIN-001` | ADMIN | Legal Metrology Controller (HQ) |
| `OFF-INACT-2024-099` | INSPECTOR | *Inactive Account (Access Denied Test)* |

Officer accounts are provisioned by department administrators or the development-only
`seed_officers` management command. There is no public registration or signup flow.

---

## 7. API Verification Endpoints

- **Health Check:** `GET http://127.0.0.1:8000/api/health/`
  ```json
  {
    "status": "ok",
    "message": "Legal Metrology API is running"
  }
  ```
- **Officer Login:** `POST http://127.0.0.1:8000/api/auth/login/`
  - Body: `{"officer_id": "OFF-DEL-2024-001", "password": "<provisioned-password>"}`
- **Current Officer:** `GET http://127.0.0.1:8000/api/auth/me/` (Requires `Authorization: Token <token>`)
- **Logout:** `POST http://127.0.0.1:8000/api/auth/logout/` (Requires `Authorization: Token <token>`)

The login response returns a server-side DRF token and safe officer profile fields only.
The frontend stores the token for the session and sends it as `Authorization: Token <token>`.
API errors are mapped to user-friendly messages, and invalid or inactive accounts cannot log in.

### Frontend API Configuration

Copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL` to the Django API
base URL. Backend configuration remains in `backend/.env`; both `.env` files are ignored by Git.

### Prompt 2 Verification

Run the backend checks from `backend/`:

```powershell
python manage.py check
python manage.py test users
python manage.py seed_officers
python manage.py runserver
```

In a separate terminal, run the frontend from `frontend/`:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173/`, sign in with an officer account provisioned in the database,
verify the dashboard officer details, refresh the page, visit the protected routes, and test
logout. After logout, `/dashboard`, `/scan`, `/history`, and `/results` redirect to `/login`.

---

## 8. Development Roadmap (15 Prompts)

- [x] **Prompt 1/15:** Project Foundation, React + Vite, Django, MySQL, OfficerProfile & Dashboard Skeleton.
- [x] **Prompt 2/15:** React-Django API integration, officer authentication, protected routes, logout & authorization foundation.
- [ ] **Prompt 3/15:** Image Ingestion Pipeline & Camera Capture Module.
- [ ] **Prompt 3/15:** Image Preprocessing (Deskewing, Contrast Adjustment, Bounding Box ROI).
- [ ] **Prompt 4/15:** OCR Engine Integration (PaddleOCR / Tesseract).
- [ ] **Prompt 5/15:** Text Parsing & Entity Extraction (MRP, Net Quantity, Dates, Manufacturer).
- [ ] **Prompt 6/15:** Legal Metrology Rules Engine (Rules 2011 Compliance Verification).
- [ ] **Prompt 7/15:** Violation Classifier & Scoring Matrix.
- [ ] **Prompt 8/15:** Officer Verification & Interactive Correction Interface.
- [ ] **Prompt 9/15:** Inspection Report Generation & Digital Notice Export (PDF).
- [ ] **Prompt 10/15:** Evidence Gallery & Label Annotation Viewer.
- [ ] **Prompt 11/15:** Search, Filter & Audit Trail Dashboard.
- [ ] **Prompt 12/15:** Role-Based Access Control & Admin Officer Management.
- [ ] **Prompt 13/15:** Performance Optimization, Caching & Batch Inspections.
- [ ] **Prompt 14/15:** Offline-first PWA Sync & Edge Support.
- [ ] **Prompt 15/15:** Production Hardening, Dockerization & Final Deployment.
