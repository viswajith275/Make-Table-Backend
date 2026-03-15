<h1 align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue.svg" alt="Python Version"/>
  <img src="https://img.shields.io/badge/FastAPI-async-green.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Docker-Compose-blue.svg" alt="Docker"/>
  <br>
  🚀 Make-Table-Backend 🚀
</h1>

<div align="center">
  <b>
    Your one-stop engine for stress-free, automated timetable creation.<br>
    Pure backend, fully Python 🐍, powered by Docker, FastAPI, Celery & OR-Tools.
  </b>
</div>

---
<br/>

## 🌟 What is Make-Table-Backend?

**Make-Table-Backend** is a Python-powered RESTful API for institutional timetable management. It takes the nightmare out of scheduling classes, teachers, labs, and subjects by using clever constraint solving and asynchronous background generation; all easily started with a single `docker-compose up`. You focus on what matters—let the backend do the organizing!

---

## 🎯 Key Features

- <span style="color:#00bfff;">**Authentication**</span> – Secure registration, login, cookies, and profile endpoints.
- <span style="color:#ff6347;">**Timetable Generator**</span> – Automated scheduling with class/teacher/subject/lab constraints, using Google OR-Tools for conflict detection and smart allocation.
- <span style="color:#6a5acd;">**CRUD Everything**</span> – Manage timetables, classes, teachers, subjects, and assignments with rich endpoints.
- <span style="color:#ffa500;">**Asynchronous**</span> – Fire-and-forget timetable builds: background tasks via Celery and Real-Time status.
- <span style="color:#2e8b57;">**Insightful Conflict Reporting**</span> – Broadcasting violations and letting you force generation anyway when needed.
- <span style="color:#008b8b;">**Modern Dev Experience**</span> – FastAPI auto Swagger docs, type validation, and clean architecture.
- <span style="color:#d2691e;">**Fully Dockerized**</span> – Run with `docker-compose up --build` and you’re set!

---

## 🎨 Tech Stack

| Layer             | Technology                           |
|-------------------|--------------------------------------|
| API & Routing     | <b>FastAPI</b>                       |
| Background Tasks  | <b>Celery</b> + <b>Redis</b>         |
| DB                | <b>PostgreSQL</b> and <b>SQLAlchemy</b> |
| Migration         | <b>Alembic</b>                       |
| Constraint Solver | <b>Google OR-Tools</b>               |
| Containerization  | <b>Docker Compose</b>                |
| Auth              | JWT in Cookies                       |
| Python Packages   | Managed with uv + pyproject.toml      |

---

## 🗂️ Project Structure (Essentials Only)

```plaintext
app/
  api/v1/...
    endpoints/
      auth.py        # login/register/me endpoints
      timetable.py   # CRUD for timetables
      class_.py      # CRUD for classes
      subject.py     # CRUD for subjects
      teacher.py     # CRUD for teachers
      teacher_assignment.py # teacher/class/subject assignment
      generation.py  # Start & check generation jobs
      timetable_entry.py # See scheduled lessons
  core/        # settings, celery config, exception handlers
  models/      # SQLAlchemy models
  schemas/     # Pydantic schemas for API
  services/    # Business rules, actual logic
  worker/      # Celery background tasks
alembic/       # DB migrations
...
docker-compose.yaml   # --- One command starts all!
Dockerfile
```

---

## 🚀 Quickstart For Humans

1. **Clone this repo.**  
   `git clone https://github.com/viswajith275/Make-Table-Backend.git`

2. **Copy `.env.example` to `.env`**  
   (or just use defaults—see below for environment keys).

3. **Fire up everything:**  
   ```bash
   docker-compose up --build
   ```

   ⏳ Wait for containers to initialize, Alembic to run migrations, and then:
   - API is at [http://localhost:8000/docs](http://localhost:8000/docs)
   - PostgreSQL is at `localhost:5433`
   - Redis is at `localhost:6371`
   - Celery worker is automatically running.

---

## ⚡ Live Demo (How You’d Use It)

1. **Register & Login:**
    - `POST /api/v1/register` with your info.
    - `POST /api/v1/login` (gets JWT cookies—no manual header pasting!).
2. **Create a Timetable:**
    - `POST /api/v1/timetables` (name, slots/days, etc.).
3. **Add Classes, Teachers, Subjects:**  
    - `POST /api/v1/timetables/{timetable_id}/classes`
    - (and similar endpoints for teachers/subjects).
4. **Make Teacher Assignments:**
    - `POST /api/v1/assignments` with your mappings.
5. **Generate the Timetable:**
    - `POST /api/v1/timetable/{timetable_id}/generate`
    - Backend does the heavy lifting _asynchronously_ (so your client/snappy frontend never hangs).
6. **Check Result & Get Schedule:**
    - `GET /api/v1/timetable/{timetable_id}/status`
    - See if generation succeeded/failed/has violations.
    - `GET /api/v1/classes/{class_id}/entries`
    - `GET /api/v1/teacher/{teacher_id}/entries`

---

## 🛠️ All Endpoints

All endpoints are versioned at `/api/v1/`.
- **Auth:** `/register`, `/login`, `/logout`, `/refresh`, `/me`
- **Timetables:** `/timetables`, `/timetables/{id}`
- **Classes, Teachers, Subjects:** `/timetables/{tid}/classes`, `/timetables/{tid}/teachers`, etc.
- **Assignments:** `/assignments`, `/teachers/{teacher_id}/assignments`
- **Timetable Generation:** `/timetable/{tid}/generate`, `/timetable/{tid}/status`
- **Timetable Entries:** `/classes/{cid}/entries`, `/teacher/{tid}/entries`

➡️ **Auto-generated Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🤖 How Does Timetable Generation Work?

1. You create all the “ingredients”: timetables, classes, teachers, subjects, assignments.
2. You POST to `/timetable/{tid}/generate`.
3. Celery picks up the job, grabs constraints (teacher availability, class/subject/lab needs), and lets Google OR-Tools do the magic. 🧙‍♂️
4. If there’s a conflict (say, a teacher double-booked or not enough time slots), it’ll surface those “violations.” You can force the timetable build if needed.
5. Success? Schedule is persisted and can be fetched per class/teacher.

---

## 💡 Fun Scenario

> Imagine you’re at a school or college. You need a perfectly optimized schedule for hundreds of classes, subjects, and teachers, with labs and breaks—oh my!  
> With Make-Table-Backend, just define your entities, assign relationships, and hit “generate.”  
> The system crunches availability, subject min/max counts, and teacher constraints, then spits out a complete, conflict-minimized schedule in seconds.

---

## ❤️ Why You'll Love It

- _Hate Excel? Use this._
- _Hate Scheduling Drama? Use this._
- _Want Powerful API-First Integration? Use this._
- _Need Fast, Repeatable, Versioned Timetabling? Use this._
- _Running complex scheduling logic with async reliability? Use this._

---

## 🔒 License

BSD 3-Clause

---

<div align="center">
  <b>Ready to make timetabling easy? <br> One backend, any frontend – go build!</b>
  <br/>
  <sub>Maintained by <a href="https://github.com/viswajith275">viswajith275</a></sub>
</div>
