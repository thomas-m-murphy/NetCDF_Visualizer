# Hybrid Configuration Overview

This setup supports **two types of usage**:

- **(1) Server-Stored Files** with persistent access  
- **(2) Temporary Local Files** for one-time quick use

---

## 1. Server-Stored File Workflow

### Uploads Directory Structure

Uploaded files will be organized by date, just like you’ve been doing:

```
uploads/
├── 2025-03/
│   ├── field0001.nc
│   ├── simA_run4.nc
├── 2025-04/
│   ├── simB_test1.nc
```

This helps with:
- Logical organization  
- Quick file browsing  
- Preventing name collisions  

> You can still customize by project/user/etc later if needed.

---

### Metadata Management with SQLite

Each uploaded file will have metadata saved in a **SQLite database**  
(or PostgreSQL later, if needed):

```sql
CREATE TABLE nc_files (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    path TEXT,
    upload_date TEXT,
    variables TEXT,   -- JSON array of variables in the file
    size_mb REAL,
    project TEXT,
    user TEXT
);
```

This allows:
- Fast querying  
- Filtering by variable/project/date  
- File lookup without rescanning the filesystem  

---

## 2. Temporary (One-Time) Local File Workflow

Users can also **drag and drop** or browse for `.nc` files and:

- Visualize them directly in the app  
- Not store them in the database  
- Not save them in `uploads/` permanently  

### How it works:

- File is uploaded to a temporary directory (e.g., `temp/`)  
- Processed in memory or from disk  
- Deleted after use or session ends  

> This avoids cluttering the server and is great for quick exploration.

---

## Summary

| Feature                     | Server-Stored | Temporary |
|----------------------------|---------------|-----------|
| Persistent Access          | ✅            | ❌        |
| Stored in `uploads/YYYY-MM`| ✅            | ❌        |
| Saved in SQLite DB         | ✅            | ❌        |
| Good for large analysis    | ✅            | ✅        |
| Auto
