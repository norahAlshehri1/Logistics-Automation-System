# Logistics Paperwork Automation System

This project aims to automate the processing of logistics documentation using a FastAPI backend, a Regex/AI-driven extraction engine, and a modern React frontend. The system significantly reduces manual data entry time by automatically extracting key fields from commercial invoices and allowing users to verify them through an interactive interface.

## 🚀 Latest Updates (Sprint 2 Achievements)

In Sprint 2, we successfully built the core extraction engine and the user interface, completing the End-to-End (E2E) workflow:

- **Automated Extraction Engine:** Developed a Python-based extraction module using `pdfplumber` and Regex to accurately pull critical data such as Vendor Name, Invoice Number, Shipment Date, and Total Amount from uploaded invoices.
- **Interactive Review UI:** Built a modern, responsive React application featuring a side-by-side dual-pane layout with an embedded PDF viewer alongside a dynamic review form.
- **End-to-End Integration:** Enabled seamless communication between the frontend and backend using `axios`, handling `multipart/form-data` uploads, resolving CORS restrictions, and persisting approved data into the database.
- **Project Restructuring:** Organized the repository into dedicated `Gproject` (Backend) and `frontend` (Frontend) directories for a professional full-stack architecture.

## 🏁 Previous Milestones (Sprint 1)

- **Database Schema:** Designed relational tables for Cases, Documents, and Users using SQLAlchemy.
- **Authentication:** Implemented secure JWT-based login and registration flow with Bcrypt hashing.
- **Document Management:** Built RESTful APIs for CRUD operations and secure server-side file storage.

## 💻 Technology Stack

### Backend

- Python 3.9+
- FastAPI (REST API Framework)
- SQLite & SQLAlchemy ORM
- `pdfplumber` & `re` (Data Extraction)
- JWT & Bcrypt (Security)

### Frontend

- React.js (via Vite)
- Axios (API Client)
- Modern CSS (Soft UI, Glassmorphism)

## 📂 Project Structure

- `/Gproject` — Contains the FastAPI backend, database models, and extraction logic.
- `/frontend` — Contains the React user interface and UI components.

## ⚙️ Installation & Setup

To run this project locally, you need to start both the backend and frontend servers.

### 1. Backend Setup

Open a terminal, navigate to the backend folder, and run the server:

```bash
cd "Gproject"
pip install -r requirements.txt
uvicorn main:app --reload
````

The backend API will be available at `http://127.0.0.1:8000` and the documentation at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

Open a new terminal, navigate to the frontend folder, and start the React app:

```bash
cd "frontend"
npm install
npm run dev
```

The frontend interface will be available at `http://localhost:5173`.

## 👥 Team Members

* **Norah Alshehri** — 2230004682 (Backend & Extraction)
* **Bayader Alghamdi** — 2230003715 (Backend & Extraction)
* **Shaykhah Mohsen** — 2230005764 (Frontend & UI/UX)
* **Maha Alnafea** — 2230003005 (Frontend & UI/UX)

```
```
