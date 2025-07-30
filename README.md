# 🧾 Freelancer Invoice & Time Tracker – Backend (Django)

A full-featured freelance business tool that helps independent professionals log time, generate invoices, and manage clients—all in one clean, easy-to-use system. This project was built using Django and Django REST Framework, with PDF generation.

---

<img width="1435" height="766" alt="Screenshot 2025-07-30 at 1 19 57 PM" src="https://github.com/user-attachments/assets/e3cfe623-78a5-4131-864f-94335d7160a3" />

---

## 🚀 Overview

The **Freelancer Invoice & Time Tracker** is designed for self-employed freelancers who juggle multiple clients and projects. It simplifies the essential but tedious tasks of tracking billable hours and creating professional invoices. Users can track their time using a live timer or add time manually, generate clean invoices, and export or email them directly from the platform.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Environment Variables](#-environment-variables)
- [Installation](#-installation)
- [Core Modules](#-core-modules)
  - [Project Management](#-project-management)
  - [Time Tracking](#-time-tracking)
  - [Invoice Generation](#-invoice-generation)
  - [Invoice History](#-invoice-history)
  - [Client Management](#-client-management)
- [UI Highlights](#-ui-highlights)
- [System Goals & Benefits](#-system-goals--benefits)
- [Requirements Summary](#-requirements-summary)
  - [Functional Requirements](#functional-requirements)
  - [Non-Functional Requirements](#non-functional-requirements)
- [User Roles](#-user-roles)
- [Reports and Planning (Extended Features)](#-reports-and-planning-extended-features)
- [Status](#-status)
- [Documentation & Screens](#-documentation--screens)
- [Credits](#credits)

---

## 💼 Features

* Secure account creation and login (via Djoser)
* Dashboard for managing projects, clients, and time entries
* Real-time timer and manual time entry support
* PDF invoice generation using tracked time and hourly rate
* Invoice status tracking: Draft, Sent, Paid
* Email invoices to clients
* Invoice and project history logs
* Admin panel and user roles (planned features)

---


<img width="1094" height="525" alt="Screenshot 2025-07-30 at 1 20 17 PM" src="https://github.com/user-attachments/assets/872c851f-1606-44d1-9715-2941ce9d3187" />


---

## ⚙️ Tech Stack

* **Framework**: Django 5.2.3
* **API**: Django REST Framework
* **Authentication**: Djoser, TokenAuth, SessionAuth
* **PDF Export**: xhtml2pdf, pyHanko
* **Email**: SMTP integration
* **Deployment**: Gunicorn, Whitenoise, dj-database-url

---

## 🏗️ System Architecture

* **Frontend**: HTML, CSS (custom dashboard UI)
* **Backend**: Django (tracker app + freelancer settings)
* **Database**: SQLite for dev, PostgreSQL for production

---

## 🔐 Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1
database_url=postgres://user:pass@host:port/dbname
```

---

<img width="907" height="547" alt="Screenshot 2025-07-30 at 1 20 22 PM" src="https://github.com/user-attachments/assets/d801df50-775b-4261-9911-326aaa783e64" />

---

## 📦 Installation

```bash
git clone https://github.com/DelRiscoAriel/FreelancerWebsiteProject.git
cd FreelancerWebsiteProject/freelancer

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Core Modules

### 🔧 Project Management

* Create/edit/delete projects
* Assign hourly rates
* Status: Active/Completed

### ⏱️ Time Tracking

* Start/pause/stop timer per project
* Manual time entry support
* Time logs view/edit/delete

### 📄 Invoice Generation

* Auto-calculate total hours \* rate
* Save/export invoice as PDF
* Email invoice to client

### 📁 Invoice History

* View past invoices
* Tag status: Draft / Sent / Paid
* Search/filter by date, project, or client

### 👥 Client Management

* Store client details
* Associate clients with projects

---

## 🖼️ UI Highlights

* Sidebar-based dashboard
* Project search + filtering
* In-app notifications for saved actions
* Responsive design for use on desktop or tablet

---

## 📈 System Goals & Benefits

* Save time with automated invoicing and tracking
* Eliminate billing errors from manual calculations
* Help freelancers appear more professional
* Keep invoice history and time logs organized
* Work from anywhere: mobile/tablet-friendly design

---

<img width="958" height="472" alt="Screenshot 2025-07-30 at 1 20 28 PM" src="https://github.com/user-attachments/assets/47ac4ef3-b435-4484-b62c-c0faf62ec44b" />

---

## 📜 Requirements Summary

### Functional Requirements

* Create/edit/delete projects with hourly rates
* Start/pause/stop timers and log manual hours
* Generate/edit/export/email invoices
* View invoice status and history
* Register/login securely

### Non-Functional Requirements

* High availability (99% uptime)
* Fast response time (< 3s)
* PDF generation within 2s
* Secure data storage and session management

---

## 🧠 User Roles

* **Freelancer**: Primary user, full access to tracking/invoicing features
* **Client**: Invoice recipients (view-only)
* **Admin** (future): Manage user roles and override permissions

---

## 📃 Reports and Planning (Extended Features)

* Phase-based time breakdown (Planning, Design, Dev, Review)
* Task effort tracking by complexity (Simple/Medium/Hard)
* Cost estimations via rate \* time
* Gantt chart generation for project scheduling
* Role-based access control and user overrides (Admin panel)

---

## ✅ Status

| Module                 | Status         | Owner |
| ---------------------- | -------------- | ----- |
| User Authentication    | ✅ Done        | Ariel |
| Project Management     | ✅ Done        | Maria |
| Timer Functionality    | ✅ Done        | Maria |
| Invoice Generation     | ✅ Done        | David |
| Invoice Email Delivery | ✅ Done        | David |
| Invoice History Module | ✅ Done        | Ariel |
| Frontend Integration   | ✅ Done        | Ariel |

---

## 📚 Documentation & Screens

* Login & Registration
* Dashboard View
* Time Tracker Screen
* Invoice Creation Flow
* Role Management Panel 
* Admin Permissions & Exceptions 


---

## Credits

Built by:

* Maria Rodriguez
* David Vasquez
* Ariel Del Risco Lorenzo

Course: CEN 4021 – Florida International University
Instructor: Dr. Rehan Akbar
