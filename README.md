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

## 8. Prompt 3 Product Inspection Pipeline

The authenticated scanner workflow is now available at `/scan`:

1. Create an inspection and optionally label the product.
2. Select multiple JPEG, PNG, or WEBP package images, or capture them with a supported camera.
3. Assign each image a package side, preview it, and remove unsuitable images.
4. Upload originals to Django media storage, preprocess a copy, and run the OCR service.
5. Review detected text and structured fields at `/scan/<inspection_id>/review`.
6. Correct or verify fields. Original OCR values remain stored for auditability.

Inspection APIs are authenticated and owner-scoped:

```text
POST   /api/scanner/inspections/
GET    /api/scanner/inspections/
GET    /api/scanner/inspections/<inspection_id>/
POST   /api/scanner/inspections/<inspection_id>/images/
DELETE /api/scanner/inspections/<inspection_id>/images/<image_id>/
POST   /api/scanner/inspections/<inspection_id>/process/
PATCH  /api/scanner/inspections/<inspection_id>/verify/
```

The processing layer stores original images, processed copies, OCR regions, confidence,
and structured extraction metadata. It does not evaluate legal compliance or produce
PASS/FAIL decisions; that belongs to Prompt 4. Extraction is assistive and requires
officer verification.

### OCR Runtime

Pillow is required for Django image validation. OpenCV is used when installed for
denoising and enhancement. PaddleOCR is loaded lazily by the processing service so the
API can report a clear processing failure when its platform-compatible PaddlePaddle
runtime is not installed. Python 3.13 support for PaddlePaddle must be verified before
installing it on Windows; use a supported Python environment and then install the
versions listed in `backend/requirements.txt`.

After changing models or dependencies:

```powershell
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py test scanner.tests users.tests
```

---

## 8. Development Roadmap (15 Prompts)

- [x] **Prompt 1/15:** Project Foundation, React + Vite, Django, MySQL, OfficerProfile & Dashboard Skeleton.
- [x] **Prompt 2/15:** React-Django API integration, officer authentication, protected routes, logout & authorization foundation.
- [x] **Prompt 3/15:** Multi-image inspection ingestion, preprocessing, OCR storage, structured extraction & officer verification.
- [x] **Prompt 4/15:** PDF-sourced Legal Metrology applicability, rule evaluation, schedules, evidence and manual-review results.
- [x] **Prompt 5/15:** Officer verification, correction history, compliance result views, inspection history, dashboard statistics and audit trail.

## 10. Prompt 5 Verification and Audit Workflow

Prompt 5 adds append-only field corrections and inspection audit events. Corrections preserve
the original extracted value, corrected value, officer, and timestamp. Changing verified data
invalidates the current compliance evaluation; running the check again creates a new version
and preserves the previous result.

New scanner endpoints include:

```text
GET /api/scanner/inspections/history/?search=<text>&status=<status>&product=<text>
GET /api/scanner/inspections/<inspection_id>/review/
GET /api/scanner/inspections/<inspection_id>/audit/
GET /api/scanner/dashboard/stats/
```

Compliance results are available through:

```text
GET /api/compliance/inspections/<inspection_id>/results/
GET /api/compliance/inspections/<inspection_id>/compliance/
```

The frontend routes are `/inspection/<id>`, `/inspection/<id>/review`, and
`/inspection/<id>/results`. History search is enforced by Django ownership-filtered
querysets. Audit logs and corrections are read-only in Django Admin.

## 9. Prompt 4 Legal Metrology Compliance Engine

The compliance engine is sourced from `9 The Legal Metrology (Package Commodities) Rules, 2011.pdf`.
The parsed source covers Rules 3–31 on PDF pages 4–26 and the First through Fourth Schedules
on pages 28–34. Rule records retain their source page and reference. The engine evaluates
applicability before declarations and distinguishes `PASS`, `FAIL`, `WARNING`,
`MANUAL_REVIEW`, `NOT_APPLICABLE`, and `NOT_DETECTED`.

Seed the PDF-derived rules and schedules:

```powershell
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py seed_rules
```

Compliance APIs are mounted under `/api/compliance/`:

```text
GET  /api/compliance/rules/
POST /api/compliance/inspections/<inspection_id>/evaluate/
GET  /api/compliance/inspections/<inspection_id>/compliance/
GET  /api/compliance/inspections/<inspection_id>/compliance/summary/
```

The verified inspection review page exposes **Run Compliance Check** and displays the overall
status, counts, rule reference, requirement, detected value, explanation, recommendation,
evidence metadata, and source PDF page. Physical quantity accuracy and visual measurements
remain `MANUAL_REVIEW` unless authorised inspection measurements or reliable calibrated image
evidence are supplied. The interface describes the result as an automated preliminary
assessment; an authorised Legal Metrology Officer must verify it.

The provided Legal Metrology (Packaged Commodities) Rules, 2011 PDF is used as the rule-source
for this implementation. Applicable amendments and current legal requirements must be verified
against the official current legal source before production/legal reliance.
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

## Prompt 6 Reports, Testing and Security

Completed inspections have a protected backend-generated PDF report:

```text
GET /api/scanner/inspections/<inspection_id>/report/pdf/
```

The report includes inspection and officer metadata, extracted and corrected fields,
persisted rule-by-rule results, evidence references, manual-review requirements, and the
audit timeline. The Results page provides **Download PDF Report**. Access uses the same
owner/admin queryset as inspection details, and report errors do not expose filesystem paths.

Run backend validation from `backend/`:

```powershell
python manage.py check
python manage.py test
```

Report generation requires `reportlab`. Uploads are limited to 10 MB and JPEG, PNG, or
WEBP files; extension, MIME type, and actual image contents are validated. Original images
remain separate from processed copies, generated storage names are used, and history is
paginated at 25 records per page. Set `SECRET_KEY`, `DEBUG`, database variables, and
`CORS_ALLOWED_ORIGINS` in `backend/.env`; never use the example secret outside development.

Automated results are preliminary decision-support output. Officers must perform physical
measurements and other manual checks identified in the report. Known limitations include
synchronous OCR/image processing, source-image references instead of full-resolution PDF
embeds, and no production backup or deployment pipeline in Prompt 6.
