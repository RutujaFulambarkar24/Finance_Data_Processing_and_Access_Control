from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import date
from fastapi import HTTPException
from typing import Optional
from datetime import datetime
from collections import defaultdict
from calendar import month_name


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API is running"}


# --- In-memory database ---
users_db = []

# --- User Model ---
class User(BaseModel):
    id: int
    name: str
    role: str  # viewer / analyst / admin
    active: bool = True


@app.post("/users")
def create_user(user: User):
    users_db.append(user)
    return {"message": "User created", "user": user}


@app.get("/users")
def get_users():
    return users_db


# --- In-memory DB ---
records_db = []

# --- Record Model ---
class Record(BaseModel):
    id: int
    amount: float
    type: str  # income / expense
    category: str
    date: date
    notes: str
    user_id: int


@app.post("/records")
def create_record(record: Record, user_id: int):
    
    # find user
    user = next((u for u in users_db if u.id == user_id), None)
    
    # check user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # check active
    if not user.active:
        raise HTTPException(status_code=403, detail="User inactive")
    
    # check role
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create records")
    
    # validation
    if record.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    if record.type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Invalid type")
    
    records_db.append(record)
    
    return {"message": "Record created", "record": record}


@app.get("/records")
def get_records(user_id: int):
    
    user = next((u for u in users_db if u.id == user_id), None)
    
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return records_db


@app.get("/records/filter")
def filter_records(
    user_id: int,
    type: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    # check user
    user = next((u for u in users_db if u.id == user_id), None)
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    filtered = records_db.copy()
    
    # filter by type
    if type:
        filtered = [r for r in filtered if r.type == type]
    
    # filter by category
    if category:
        filtered = [r for r in filtered if r.category == category]
    
    # filter by date range
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        filtered = [r for r in filtered if r.date >= start]
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        filtered = [r for r in filtered if r.date <= end]
    
    return filtered


@app.put("/records/{record_id}")
def update_record(record_id: int, updated_record: Record, user_id: int):
    
    # check user
    user = next((u for u in users_db if u.id == user_id), None)
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update records")
    
    # find record
    record = next((r for r in records_db if r.id == record_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # validate
    if updated_record.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    if updated_record.type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Invalid type")
    
    # update fields
    record.amount = updated_record.amount
    record.type = updated_record.type
    record.category = updated_record.category
    record.date = updated_record.date
    record.notes = updated_record.notes
    record.user_id = updated_record.user_id
    
    return {"message": "Record updated", "record": record}


@app.delete("/records/{record_id}")
def delete_record(record_id: int, user_id: int):
    
    user = next((u for u in users_db if u.id == user_id), None)
    
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete")
    
    global records_db
    records_db = [r for r in records_db if r.id != record_id]
    
    return {"message": "Record deleted"}


@app.get("/dashboard/total-income")
def total_income(user_id: int):
    
    user = next((u for u in users_db if u.id == user_id), None)
    
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    total = sum(r.amount for r in records_db if r.type == "income")
    
    return {"total_income": total}


@app.get("/dashboard/total-expense")
def total_expense(user_id: int):
    
    user = next((u for u in users_db if u.id == user_id), None)
    
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    total = sum(r.amount for r in records_db if r.type == "expense")
    
    return {"total_expense": total}


@app.get("/dashboard/net-balance")
def net_balance(user_id: int):
    
    user = next((u for u in users_db if u.id == user_id), None)
    
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    income = sum(r.amount for r in records_db if r.type == "income")
    expense = sum(r.amount for r in records_db if r.type == "expense")
    
    return {"net_balance": income - expense}


@app.get("/dashboard/category-totals")
def category_totals(user_id: int, type: Optional[str] = None):
    # check user
    user = next((u for u in users_db if u.id == user_id), None)
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    totals = defaultdict(float)
    
    for r in records_db:
        if type and r.type != type:
            continue
        totals[r.category] += r.amount
    
    # convert to regular dict for output
    return dict(totals)


@app.get("/dashboard/recent-activity")
def recent_activity(user_id: int, limit: int = 5):
    # check user
    user = next((u for u in users_db if u.id == user_id), None)
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # sort records by date descending
    sorted_records = sorted(records_db, key=lambda r: r.date, reverse=True)
    
    # take the most recent 'limit' records
    recent = sorted_records[:limit]
    
    return recent


@app.get("/dashboard/monthly-trends")
def monthly_trends(user_id: int):
    # check user
    user = next((u for u in users_db if u.id == user_id), None)
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="Access denied")
    
    trends = defaultdict(lambda: {"income": 0, "expense": 0})
    
    for r in records_db:
        month = r.date.strftime("%B %Y")  # e.g., "April 2026"
        if r.type == "income":
            trends[month]["income"] += r.amount
        elif r.type == "expense":
            trends[month]["expense"] += r.amount
    
    return dict(trends)