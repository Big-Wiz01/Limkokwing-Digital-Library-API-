# 📚 Limkokwing Library API

> **Module:** PROG315 -- Object-Oriented Programming 2\
> **Assignment:** Basic API Structure with Open-Source Software\
> **Institution:** Limkokwing University of Creative Technology, Sierra
> Leone

A production-ready RESTful API for the Limkokwing University digital
library system, built with **Python FastAPI** and **async/await** for
concurrent multi-user support.

------------------------------------------------------------------------

## 🚀 Quick Start (VS Code)

### 1. Clone or download the project

``` bash
git clone https://github.com/YOUR_USERNAME/limkokwing-library-api.git
cd limkokwing-library-api
```

### 2. Create a virtual environment

``` bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Run the API server

``` bash
uvicorn limkokwing_library_api:app --port 9000
```

### 5. Open interactive documentation

-   Swagger UI: http://127.0.0.1:9000/docs\
-   ReDoc: http://127.0.0.1:9000/redoc

------------------------------------------------------------------------

## 🔗 API Endpoints

GET /books - Search books by title, author, or category\
GET /books/available - List all books available right now\
POST /books - Add a new book to the catalogue (staff only)\
POST /borrow - Borrow an available book (14-day loan)\
POST /return - Return a book; calculates overdue fines in Leones\
GET /fines/{user_id} - Check outstanding fines for a user\
GET /overdue - All overdue borrowings campus-wide (staff)\
GET /stats - Library statistics and fine summary

------------------------------------------------------------------------

## ⚙️ Tech Stack

Python 3.10+ \| FastAPI \| Uvicorn \| Pydantic

------------------------------------------------------------------------

## 🌍 SDG Alignment

Supports SDG 4: Quality Education by improving access to digital library
services.

------------------------------------------------------------------------

## 📁 Project Structure

limkokwing-library-api/ ├── limkokwing_library_api.py ├──
requirements.txt ├── .gitignore └── README.md

------------------------------------------------------------------------

## 👤 Collaborator
Alusine Jalloh
