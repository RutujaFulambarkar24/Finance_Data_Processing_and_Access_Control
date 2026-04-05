# Finance Data Processing and Access Control Backend

## Overview
Backend API for a finance dashboard system that manages **users, roles, and financial records**, with **role-based access control** and **dashboard summary APIs**.  

Built with **FastAPI (Python)** using in-memory storage.

---

## Features

### User & Role Management
- Create/manage users
- Roles: Viewer, Analyst, Admin
- Active/inactive status
- Role-based access control

### Financial Records
- Create, read, update, delete records
- Record fields: amount, type, category, date, notes, user_id
- Filtering by type, category, or date

### Dashboard APIs
- Total Income, Total Expense, Net Balance
- Category-wise totals
- Recent activity (latest transactions)
- Monthly trends (income & expense)

### Access Control & Validation
- Admin: full access
- Analyst/Viewer: read-only
- Input validation & proper error responses

---

## Technical Details
- **Framework:** FastAPI (Python)  
- **Storage:** In-memory lists (data resets on server restart)  
- **Role-based access:** Enforced per endpoint  
- **Enhancements:** Record filtering, dashboard summaries, optional trends  

---

## Notes
- In-memory storage used for simplicity  
- Ready for future enhancements like database persistence or authentication  
