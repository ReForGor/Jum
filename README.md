# ⚡ TechPrice - Thailand IT Equipment Price Aggregator & Comparator

A full-stack IT hardware price collection and real-time comparison engine for Thailand's top IT retailers: **JIB**, **iHaveCPU**, **BaNANA IT**, and **Advice IT Infinite**.

Features a **FastAPI backend**, **JWT Authentication system**, **Admin Management Portal**, **Price Drop Notification engine & Watchlist**, and a modern **dark-theme dashboard** with time-series historical price charts in **Thai Baht (฿ THB)**.

---

## 🌟 Key Features

1. **Thai IT Retailer Price Comparison**:
   - Compares real-time prices across **JIB (`jib.co.th`)**, **iHaveCPU (`ihavecpu.com`)**, **BaNANA IT (`bnn.in.th`)**, and **Advice (`advice.co.th`)**.
   - Highlights the **"🔥 Cheapest Store in Thailand"**, calculates savings in ฿ THB, and provides direct "Buy on Store" links.

2. **Admin Management Backend (`/admin`)**:
   - Dedicated Admin Portal for managing hardware products, editing specifications, adding new IT components, overriding store prices manually, running scraper jobs, and broadcasting push notifications to all users.
   - Default Admin Account: `admin@techprice.com` / `admin123`

3. **User Authentication & Login System**:
   - User Registration & Login with JWT access tokens and secure bcrypt password hashing.
   - User Profile management with active tracked alerts and unread notifications count.
   - Demo User Account: `gamer@demo.com` / `password123`.

4. **Real-Time Price Drop Alert & Notification Center**:
   - Set a custom **Target Price (฿)** on any hardware component (e.g. RTX 5090, Ryzen 9800X3D).
   - **In-App Notification Bell with Unread Counter**: When scraper detects a price drop below the target price, an alert is automatically dispatched with store link and price drop amount.
   - **Watchlist Dashboard (`/watchlist`)**: View, edit, pause, or remove tracked items and see the distance to target price.

5. **Multi-Product Head-to-Head Comparator (`/compare`)**:
   - Compare 2 to 4 IT components head-to-head.
   - Side-by-side technical specification matrix (VRAM, Bus Width, Clock Speeds, TDP, Cores, Socket, Warranty).

6. **Hot Tech Deals Tracker (`/deals`)**:
   - Highlights the biggest discounts and flash sales currently active across JIB, iHaveCPU, BaNANA, and Advice.

7. **REST API & Developer Explorer (`/api-explorer` & `/docs`)**:
   - Interactive Swagger API documentation at `/docs`.

---

## 💻 Running on Windows & Linux

This application is **100% cross-platform** and runs natively on **Windows (10/11)**, **Linux**, and **macOS**.

### Option A: Running on Windows (One-Click)

1. Ensure **Python 3.10+** is installed on Windows (check the box *"Add Python to PATH"* during installation).
2. Double click **`run.bat`** (or open PowerShell / CMD and run `.\run.bat` or `.\run.ps1`).

```cmd
cd techprice-aggregator
run.bat
```

Or manually on Windows:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Option B: Running on Linux / macOS

```bash
cd /home/rfg/Projects/techprice-aggregator
./run.sh
```

---

## 🌐 Quick Access URLs

- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Admin Management Portal**: [http://localhost:8000/admin](http://localhost:8000/admin) *(Login: `admin@techprice.com` / `admin123`)*
- **User Watchlist & Alerts**: [http://localhost:8000/watchlist](http://localhost:8000/watchlist)
- **Head-to-Head Compare**: [http://localhost:8000/compare](http://localhost:8000/compare)
- **Hot Deals**: [http://localhost:8000/deals](http://localhost:8000/deals)
- **Thai Scrapers Hub**: [http://localhost:8000/platforms](http://localhost:8000/platforms)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
