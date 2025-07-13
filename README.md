# 🏢 QuickReserve 


QuickReserve is a Django-based web application designed to simplify internal room bookings and amenity management for organizations. The dashboard provides an intuitive interface for admins to manage meeting rooms, available amenities, and their respective bookings—all in one place.

---## ✨ Features


### 👨‍💼 Admin Dashboard
username = atharva@gmail.com
password = 123
- Create, update, delete **Rooms**
- Add and manage **Amenities**
- View and filter **Bookings** (Upcoming / Past / All)
- Interactive modals for room and amenity management using AJAX
- Dynamic filtering system for views
- Statistics for rooms, bookings, and amenities

### 👩‍💻 Employee Interface
- Login using **email authentication**
- Book meetings by selecting:
  - Room
  - Date & Time
  - Amenities
  - Number of participants
- View your personal booking history
- Clean, responsive UI with intuitive modals

---

## 🔐 Authentication System

- Employees log in securely using **email & password**
- Django’s authentication framework with **session-based security**
- Custom login system styled with Bootstrap
- CSRF protection and input validation included

---

## 📦 Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, Bootstrap 5, JavaScript (AJAX)
- **Database**: MySql
- **Authentication**: Django session login with **email-based validation**
- **Security**: CSRF protection, clean form handling, secure access control

## 🚀 Getting Started

### 1. Clone the Repository

```bash
-- cd quickreserve
2. Create Virtual Environment

python -m venv env
source env/bin/activate  # macOS/Linux
env\Scripts\activate     # Windows

3. Install Dependencies

pip install -r requirements.txt


4. Run the Server

python manage.py migrate
python manage.py runserver



📧 Email Authentication Flow
Custom login form accepts email & password

Upon login, user session is created

Authenticated users are redirected to dashboard

Invalid attempts return clear form errors

