from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import asyncio

app = FastAPI(
    title="Limkokwing Digital Library API",
    description="Breaking barriers to education at Limkokwing University Sierra Leone — a digital library API built to make knowledge accessible to every student, anytime, anywhere.",
    version="3.0.3",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ==================== DATA MODELS ====================

class BorrowRequest(BaseModel):
    user_id: str = Field(..., example="DIT905005001")
    book_id: str = Field(..., example="BK001")

class ReturnRequest(BaseModel):
    user_id: str = Field(..., example="DIT905005001")
    borrow_id: str = Field(..., example="BR101")

class NewBookRequest(BaseModel):
    book_id: str = Field(..., example="BK006")
    title: str = Field(..., example="The New Africa Rising")
    author: str = Field(..., example="Femi Otedola")
    category: str = Field(..., example="Business")

# ==================== SIMULATED DATABASE ====================

books_db: dict = {
    "BK001": {"title": "Otedola: The Billionaire Mindset", "author": "Femi Otedola", "category": "Business & Finance", "available": True},
    "BK002": {"title": "The Lean Startup", "author": "Eric Ries", "category": "Business & Entrepreneurship", "available": True},
    "BK003": {"title": "Atomic Habits", "author": "James Clear", "category": "Self Development", "available": False},
    "BK004": {"title": "Clean Code", "author": "Robert C. Martin", "category": "Software Engineering", "available": True},
    "BK005": {"title": "Artificial Intelligence: A Modern Approach", "author": "Stuart Russell", "category": "Technology", "available": True},
    "BK006": {"title": "Africa's Business Revolution", "author": "Acha Leke", "category": "Business & Finance", "available": True},
}

borrow_records: dict = {}
fines_db: dict = {}
borrow_counter: int = 100
FINE_RATE: int = 5000  # Le 5,000 per overdue day (Sierra Leone Leones)
LOAN_DAYS: int = 14

# ==================== HELPERS ====================

async def simulate_db_delay() -> None:
    await asyncio.sleep(0.05)

async def calculate_fine(return_by: str) -> int:
    await simulate_db_delay()
    due = datetime.strptime(return_by, "%Y-%m-%d")
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if today > due:
        return (today - due).days * FINE_RATE
    return 0

# ==================== ENDPOINT 1: GET /books ====================

@app.get("/books", tags=["Books"], summary="Search for Books")
async def search_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """Search the library catalogue by title, author, or category."""
    await simulate_db_delay()
    results: List[dict] = []
    for book_id, book in books_db.items():
        match = True
        if title and title.lower() not in book["title"].lower(): match = False
        if author and author.lower() not in book["author"].lower(): match = False
        if category and category.lower() not in book["category"].lower(): match = False
        if match:
            results.append({"id": book_id, **book})
    if not results:
        raise HTTPException(status_code=404, detail="No books found.")
    return {"books": results, "total": len(results)}

# ==================== ENDPOINT 2: GET /books/available ====================

@app.get("/books/available", tags=["Books"], summary="Get All Available Books")
async def get_available_books() -> dict:
    """Returns all books that are currently available to borrow right now."""
    await simulate_db_delay()
    available: List[dict] = []
    for book_id, book in books_db.items():
        if book["available"]:
            available.append({"id": book_id, **book})
    return {
        "available_books": available,
        "total_available": len(available),
        "total_books": len(books_db),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ==================== ENDPOINT 3: POST /books ====================

@app.post("/books", status_code=201, tags=["Books"], summary="Add a New Book")
async def add_book(request: NewBookRequest) -> dict:
    """Add a new book to the library catalogue. For library staff only."""
    await simulate_db_delay()
    if request.book_id in books_db:
        raise HTTPException(status_code=400, detail=f"Book ID '{request.book_id}' already exists.")
    books_db[request.book_id] = {
        "title": request.title,
        "author": request.author,
        "category": request.category,
        "available": True,
    }
    return {
        "message": "Book added successfully",
        "book_id": request.book_id,
        "title": request.title,
        "author": request.author,
        "category": request.category,
        "available": True,
    }

# ==================== ENDPOINT 4: POST /borrow ====================

@app.post("/borrow", status_code=201, tags=["Borrowing"], summary="Borrow a Book")
async def borrow_book(request: BorrowRequest) -> dict:
    """Borrow an available book. Records a 14-day loan period."""
    global borrow_counter
    await simulate_db_delay()
    if request.book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found.")
    book = books_db[request.book_id]
    if not book["available"]:
        raise HTTPException(status_code=400, detail="Book not available.")
    borrow_counter += 1
    borrow_id = f"BR{borrow_counter}"
    return_by = (datetime.now() + timedelta(days=LOAN_DAYS)).strftime("%Y-%m-%d")
    borrow_records[borrow_id] = {
        "user_id": request.user_id,
        "book_id": request.book_id,
        "borrow_date": datetime.now().strftime("%Y-%m-%d"),
        "return_by": return_by,
    }
    books_db[request.book_id]["available"] = False
    return {
        "message": "Book borrowed successfully",
        "borrow_id": borrow_id,
        "book_title": book["title"],
        "borrowed_by": request.user_id,
        "return_by": return_by,
        "loan_period_days": LOAN_DAYS,
    }

# ==================== ENDPOINT 5: POST /return ====================

@app.post("/return", tags=["Borrowing"], summary="Return a Borrowed Book")
async def return_book(request: ReturnRequest) -> dict:
    """Return a borrowed book. Fine of Le 5,000/day applies if overdue."""
    await simulate_db_delay()
    if request.borrow_id not in borrow_records:
        raise HTTPException(status_code=404, detail="Borrow record not found.")
    record = borrow_records[request.borrow_id]
    if record["user_id"] != request.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    fine_amount: int = await calculate_fine(record["return_by"])
    due_date = datetime.strptime(record["return_by"], "%Y-%m-%d")
    days_overdue = max(0, (datetime.now() - due_date).days)
    books_db[record["book_id"]]["available"] = True
    del borrow_records[request.borrow_id]
    if fine_amount > 0:
        fines_db[request.user_id] = fines_db.get(request.user_id, 0) + fine_amount
    return {
        "message": "Book returned successfully",
        "days_overdue": days_overdue,
        "fine": f"Le {fine_amount:,}",
        "fine_note": "No fine – returned on time." if fine_amount == 0 else f"Le {fine_amount:,} added to your account.",
    }

# ==================== ENDPOINT 6: GET /fines/{user_id} ====================

@app.get("/fines/{user_id}", tags=["Fines"], summary="Check User Fines")
async def get_fines(user_id: str) -> dict:
    """Get outstanding fines and overdue books for a specific user."""
    await simulate_db_delay()
    fine_total = fines_db.get(user_id, 0)
    overdue: List[dict] = []
    for bid, rec in borrow_records.items():
        if rec["user_id"] == user_id:
            fine = await calculate_fine(rec["return_by"])
            if fine > 0:
                book = books_db.get(rec["book_id"], {})
                due = datetime.strptime(rec["return_by"], "%Y-%m-%d")
                overdue.append({
                    "book": book.get("title", "Unknown"),
                    "days_overdue": (datetime.now() - due).days,
                    "accrued_fine": f"Le {fine:,}",
                })
    return {
        "user_id": user_id,
        "outstanding_fines": f"Le {fine_total:,}",
        "overdue_books": overdue,
        "overdue_count": len(overdue),
    }

# ==================== ENDPOINT 7: GET /overdue ====================

@app.get("/overdue", tags=["Fines"], summary="Get All Overdue Books")
async def get_all_overdue() -> dict:
    """Returns all overdue borrowings across all users. For library staff."""
    await simulate_db_delay()
    overdue_list: List[dict] = []
    for borrow_id, rec in borrow_records.items():
        fine = await calculate_fine(rec["return_by"])
        if fine > 0:
            book = books_db.get(rec["book_id"], {})
            due = datetime.strptime(rec["return_by"], "%Y-%m-%d")
            overdue_list.append({
                "borrow_id": borrow_id,
                "user_id": rec["user_id"],
                "book_title": book.get("title", "Unknown"),
                "return_by": rec["return_by"],
                "days_overdue": (datetime.now() - due).days,
                "fine_accrued": f"Le {fine:,}",
            })
    return {
        "overdue_records": overdue_list,
        "total_overdue": len(overdue_list),
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ==================== ENDPOINT 8: GET /stats ====================

@app.get("/stats", tags=["Reports"], summary="Library Statistics")
async def get_stats() -> dict:
    """Overall library statistics — total books, borrowed count, fines collected."""
    await simulate_db_delay()
    total_books = len(books_db)
    available_count = sum(1 for b in books_db.values() if b["available"])
    borrowed_count = total_books - available_count
    total_fines_collected = sum(fines_db.values())
    return {
        "total_books": total_books,
        "available_books": available_count,
        "currently_borrowed": borrowed_count,
        "active_borrow_records": len(borrow_records),
        "total_fines_collected": f"Le {total_fines_collected:,}",
        "fine_rate_per_day": f"Le {FINE_RATE:,}",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ==================== ASYNC SIMULATION ====================

async def simulate_multiple_users() -> None:
    """Demonstrates async concurrency with multiple users borrowing simultaneously."""
    print("\n" + "=" * 50)
    print("  Simulating Multiple Concurrent Users")
    print("=" * 50)

    async def user_borrow(user_id: str, book_id: str) -> None:
        print(f"  > {user_id} requesting book {book_id}...")
        await simulate_db_delay()
        print(f"  + {user_id} request processed.")

    await asyncio.gather(
        user_borrow("DIT905005001", "BK001"),
        user_borrow("BIT905005002", "BK002"),
        user_borrow("DIT905005001", "BK005"),
    )
    print("  All concurrent requests completed.")
    print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    asyncio.run(simulate_multiple_users())
    uvicorn.run(app, host="0.0.0.0", port=9000)