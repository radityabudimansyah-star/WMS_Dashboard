# 📦 WMS Portal — Setup Guide
**Warehouse Management System** | Django + PostgreSQL + Streamlit

---

## Project Structure

```
wms_project/
├── django_backend/
│   ├── manage.py
│   ├── settings.py
│   ├── urls.py
│   └── wms/
│       ├── models.py        ← Database models
│       ├── views.py         ← API views + role checks
│       ├── serializers.py   ← DRF serializers
│       ├── admin.py         ← Django admin
│       └── management/commands/seed_data.py
└── streamlit_frontend/
    ├── app.py               ← Main Streamlit UI
    └── api_client.py        ← HTTP calls to Django API
```

---

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 2. PostgreSQL Setup

Create the database:
```sql
CREATE DATABASE wms_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE wms_db TO postgres;
```

Or set environment variables to use your own credentials:
```bash
export DB_NAME=wms_db
export DB_USER=your_user
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
```

---

## 3. Run Django Backend

```bash
cd django_backend

# Apply migrations
python manage.py makemigrations wms
python manage.py migrate

# Seed demo users + SKU masterlist
python manage.py seed_data

# Start Django API server (port 8000)
python manage.py runserver
```

---

## 4. Run Streamlit Frontend

Open a **new terminal**:
```bash
cd streamlit_frontend
streamlit run app.py
```

Streamlit opens at **http://localhost:8501**

---

## 5. Demo Accounts

| Username   | Password   | Role           | Access                                    |
|------------|------------|----------------|-------------------------------------------|
| admin      | admin123   | Inbound Admin  | Inbound, SKU (full edit), Dashboard       |
| outadmin   | out123     | Outbound Admin | Outbound, SKU (view), Dashboard           |
| security   | sec123     | Security       | Register inbound & outbound trucks        |
| checker1   | check123   | Checker        | Inbound view, SKU view                    |
| picker1    | pick123    | Picker         | Outbound view, SKU view                   |
| supervisor | super123   | Supervisor     | Full access to everything                 |

---

## 6. Role Permissions Summary

| Feature                  | Security | Inbound Admin | Outbound Admin | Checker | Picker | Supervisor |
|--------------------------|:--------:|:-------------:|:--------------:|:-------:|:------:|:----------:|
| View Dashboard           | ✅        | ✅             | ✅              | ✅       | ✅      | ✅          |
| Register Inbound Truck   | ✅        | ✅             |                |         |        | ✅          |
| Update Inbound Status    |          | ✅             |                |         |        | ✅          |
| View Inbound Trucks      |          | ✅             |                | ✅       |        | ✅          |
| Register Outbound Truck  | ✅        |               | ✅              |         |        | ✅          |
| Update Outbound Status   |          |               | ✅              |         |        | ✅          |
| View Outbound Trucks     |          |               | ✅              |         | ✅      | ✅          |
| View SKU Masterlist      |          | ✅             | ✅              | ✅       | ✅      | ✅          |
| Add/Edit/Delete SKU      |          | ✅             |                |         |        | ✅          |

---

## 7. Django Admin Panel

Access at **http://localhost:8000/admin/**

Create a superuser first:
```bash
python manage.py createsuperuser
```
