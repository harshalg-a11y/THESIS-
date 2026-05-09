# Thesis Portal (Flask Edition)

A visually stunning, ultra-modern Thesis Management System built with Flask and MySQL.

## Features
- **Apple-Standard UI:** Minimalist luxury with Glassmorphism and Mesh Gradients.
- **Role-Based Portals:** Dedicated environments for Admin, Students, and Experts.
- **Nexus Chat Hub:** 3-pane real-time communication interface with file sharing.
- **Supreme Randomizer Engine v2:** Intelligent load-balancing using Weighted Load Scores.
- **Security First:** SHA-256 password hashing, IDOR protection, and XSS prevention.

## Setup

```bash
pip install Flask pymysql
```

### MySQL Setup
1. Create a database `thesis_portal`.
2. Apply `mysql_schema.sql`.
3. Set environment variables:
   - `DB_TYPE=mysql`
   - `DB_HOST=localhost`
   - `DB_USER=root`
   - `DB_PASS=your_password`
   - `DB_NAME=thesis_portal`

### Local Development (SQLite)
Just run:
```bash
python app.py
```

## Credentials (Seeded)
- Admin: `admin` / `admin123`
- Student: `user1` / `user123`
- Experts: `sender1`, `sender2` / `sender123`
