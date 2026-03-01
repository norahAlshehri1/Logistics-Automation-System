# Logistics Paperwork Automation System
This project aims to automate the processing of logistics documentation using **FastAPI** and **AI-driven data extraction**.
## Sprint 1 Achievements
In this initial sprint, we focused on building the core backend infrastructure and security:
- **Database Schema:** Designed and implemented relational tables for **Cases**, **Documents**, and **Users** using **SQLAlchemy**.
- **Authentication System:** Developed a secure **JWT-based** login and registration flow.
- **Shipment Management:** Implemented core **CRUD** operations for managing shipment cases.
- **Document Upload:** Created a dedicated service for handling **multipart document uploads** and **server-side storage**.
## Technology Stack
- **Language:** Python 3.9+
- **Framework:** FastAPI
- **Database:** SQLite (SQLAlchemy ORM)
- **Security:** JWT (JSON Web Tokens) & Bcrypt hashing
## Installation & Setup
To run this project locally, follow these steps:
1. Clone the repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ````
3. Run the server:
   ```
   uvicorn main:app --reload
   ```
4. Access the API documentation at:

   * [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Team Members

* Norah Alshehri — 2230004682
* Bayader Alghamdi — 2230003715
* Shaykhah Mohsen — 2230005764
* Maha Alnafea — 2230003005
