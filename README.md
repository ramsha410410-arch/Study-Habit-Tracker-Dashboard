# 🎯 Study Planner Dashboard (Streamlit)

A simple **Study Planner + Habit Tracker + Study Session Logger** built using **Python + Streamlit**.  
It helps students plan tasks, log study hours, track daily habits (streaks), and view weekly insights — all with data stored locally in a JSON file.

---

## ✨ Features

### 📌 Task Manager
- Add tasks with:
  - Title, subject, due date, priority, estimated hours
- Filter tasks by:
  - Status (All / Open / Done)
  - Priority
  - Subject keyword
- Mark tasks as done ✅
- Delete tasks 🗑️
- Quick button to log a **1-hour session** for any task

### 🕒 Study Session Logger
- Log sessions with:
  - Date, hours, topic, notes
- View last 30 sessions in a table
- Automatically calculates:
  - Total hours in last 7 days
  - Weekly goal progress %

### 🔥 Habit Tracker (Streak System)
- Default habits included (can edit)
- Add new habits
- Mark habit done today ✅
- Tracks streaks:
  - Increases streak if done on consecutive days
  - Resets if a day is missed
- Remove habits easily

### 📊 Insights / Export
- Weekly hours chart (last ~8 weeks)
- Topic-wise hours chart (last 30 days)
- Export:
  - Full data as JSON
  - Sessions as CSV

### 💾 Local Storage
All data is saved locally in a file:
- `study_data.json`

No database needed.

---

## 🧰 Tech Stack
- Python 3.8+
- Streamlit (UI framework)
- Pandas (data analysis + tables)

---


