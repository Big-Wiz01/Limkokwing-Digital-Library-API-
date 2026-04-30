# Limkokwing Digital Library API

Breaking barriers to education at Limkokwing University Sierra Leone —
a digital library API built to make knowledge accessible to every student,
anytime, anywhere.

## Setup
pip install -r requirements.txt
uvicorn limkokwing_library_api:app --port 9000

## Endpoints
GET  /books                - Search books by title, author, or category
GET  /books/available      - List all books available right now
POST /books                - Add a new book to the catalogue (staff only)
POST /borrow               - Borrow an available book (14-day loan)
POST /return               - Return a book; calculates overdue fines in Leones
GET  /fines/{user_id}      - Check outstanding fines for a user
GET  /overdue              - All overdue borrowings campus-wide (staff)
GET  /stats                - Library statistics and fine summary

## Tech Stack
Python 3.10+ | FastAPI 0.115.0 | Uvicorn 0.30.6 | Pydantic 2.9.2

## Module: PROG315 | Semester 04 | 2025-2026
## Institution: Limkokwing University Sierra Leone
