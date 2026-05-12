# SmartSchedule AI — Smart Classroom & Timetable Scheduler

AI-powered timetable generator using Google OR-Tools CP-SAT constraint solver.  
Built by **Team FUTURE DEVELOPER** for WE Hub Incubation.

> 🎯 PoC submission deadline: **May 16, 2026**

---

## ✨ Features (v2.0)

- ✅ Conflict-free scheduling — no teacher/room double-booking
- ✅ **Multi-section support** — schedule Section A, B, C simultaneously
- ✅ **Offline demo mode** — works without backend (built-in JS solver)
- ✅ CSV export — download timetable as spreadsheet
- ✅ Print-ready — clean print layout for notice boards
- ✅ Faculty workload analytics
- ✅ REST API for ERP integration
- 🔜 Phase 2: RL agent for teacher preference learning

---

## 📁 Project Structure

```
smart-scheduler/
├── app.py              ← Flask API + OR-Tools solver (v2)
├── index.html          ← Full web app (open in browser)
├── requirements.txt    ← Python dependencies
├── Procfile            ← For Railway/Render deployment
├── railway.json        ← Railway config
└── README.md
```

---

## 🚀 Quick Start

### Local Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start backend
python app.py
# API runs at: http://localhost:5000

# 3. Open frontend
# Just open index.html in your browser
```

### Deploy Backend (Railway — free)

1. Push this folder to a GitHub repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your repo → Railway auto-detects Python
4. Copy your deployment URL (e.g. `https://smartschedule.up.railway.app`)
5. In `index.html` line 1, update: `const API = 'YOUR_RAILWAY_URL';`
6. Deploy frontend on [Netlify](https://netlify.com) (drag & drop `index.html`)

---

## 🔗 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Health check |
| GET | `/api/demo` | Demo timetable (2 sections) |
| POST | `/api/generate` | Custom timetable |
| POST | `/api/validate` | Validate for clashes |

### POST /api/generate

```json
{
  "teachers": [{ "name": "Dr. Priya" }],
  "subjects": [{
    "name": "Mathematics",
    "teacher": "Dr. Priya",
    "hours_per_week": 5
  }],
  "rooms": [{ "name": "Room 101", "capacity": 60 }],
  "sections": [{ "name": "Section A" }, { "name": "Section B" }],
  "slots_per_day": 6,
  "days": 5
}
```

---

## 🧠 How the Solver Works

1. **Variables**: Boolean variable for every (section, teacher, subject, room, day, slot) combination
2. **Hard constraints**:
   - No teacher in two places at once (across all sections)
   - No room double-booked
   - Each section has at most one class per slot
   - Each subject gets its required hours per week per section
3. **Objective**: Maximize total scheduled classes
4. **Solver**: Google OR-Tools CP-SAT (15s time limit)

### Phase 2 — Reinforcement Learning Layer
- Agent learns teacher preferences (preferred timings, room types)
- Reward: balanced workload + preferred slots
- Penalty: back-to-back classes, room mismatch

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| ML / Solver | Python + Google OR-Tools CP-SAT |
| Backend API | Flask + Flask-CORS |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Offline solver | JavaScript (greedy) |
| Deployment | Railway (backend) + Netlify (frontend) |

---

## 👩‍💻 Team FUTURE DEVELOPER
N. Shivani · K. Hansika · B. Sai Roshini · V. Sravanthi · G. Varshitha · G. Varuna
