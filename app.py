import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

APP_TITLE = "🎯 Study Planner Dashboard"
DATA_FILE = "study_data.json"


# ---------------------------
# Utilities: load/save
# ---------------------------
def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def default_data():
    return {
        "profile": {
            "name": "Student",
            "weekly_goal_hours": 10,
            "preferred_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        },
        "tasks": [],      # list of dicts
        "sessions": [],   # list of dicts: {date, hours, topic, notes}
        "habits": [       # list of dicts: {name, streak, last_done}
            {"name": "Read 20 mins", "streak": 0, "last_done": None},
            {"name": "Practice coding", "streak": 0, "last_done": None},
            {"name": "Revise notes", "streak": 0, "last_done": None},
        ],
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Basic validation / fallback keys
        for k, v in default_data().items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return default_data()


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def today_str():
    return date.today().isoformat()


def parse_iso(d):
    try:
        return datetime.fromisoformat(d).date()
    except Exception:
        return None


# ---------------------------
# Task helpers
# ---------------------------
def add_task(data, title, subject, due, priority, est_hours):
    task = {
        "id": f"t_{int(datetime.now().timestamp()*1000)}",
        "title": title.strip(),
        "subject": subject.strip(),
        "due": due.isoformat(),
        "priority": priority,
        "est_hours": float(est_hours),
        "done": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    data["tasks"].append(task)


def toggle_task(data, task_id, done_value: bool):
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["done"] = done_value
            return


def delete_task(data, task_id):
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]


# ---------------------------
# Session helpers
# ---------------------------
def add_session(data, session_date, hours, topic, notes):
    sess = {
        "date": session_date.isoformat(),
        "hours": float(hours),
        "topic": topic.strip(),
        "notes": notes.strip(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    data["sessions"].append(sess)


# ---------------------------
# Habit helpers
# ---------------------------
def mark_habit_done(data, habit_name):
    today = date.today()
    for h in data["habits"]:
        if h["name"] == habit_name:
            last = parse_iso(h.get("last_done")) if h.get("last_done") else None
            if last == today:
                return  # already done today
            if last == today - timedelta(days=1):
                h["streak"] = _safe_int(h.get("streak"), 0) + 1
            else:
                h["streak"] = 1
            h["last_done"] = today.isoformat()
            return


def add_habit(data, habit_name):
    habit_name = habit_name.strip()
    if not habit_name:
        return
    if any(h["name"].lower() == habit_name.lower() for h in data["habits"]):
        return
    data["habits"].append({"name": habit_name, "streak": 0, "last_done": None})


def delete_habit(data, habit_name):
    data["habits"] = [h for h in data["habits"] if h["name"] != habit_name]


# ---------------------------
# UI
# ---------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🎯", layout="wide")

data = load_data()

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    name = st.text_input("Student name", value=data["profile"].get("name", "Student"))
    weekly_goal_hours = st.slider(
        "Weekly goal (hours)",
        min_value=1,
        max_value=60,
        value=_safe_int(data["profile"].get("weekly_goal_hours", 10), 10),
    )
    preferred_days = st.multiselect(
        "Preferred study days",
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        default=data["profile"].get("preferred_days", ["Mon", "Tue", "Wed", "Thu", "Fri"]),
    )

    if st.button("💾 Save settings", use_container_width=True):
        data["profile"]["name"] = name
        data["profile"]["weekly_goal_hours"] = weekly_goal_hours
        data["profile"]["preferred_days"] = preferred_days
        save_data(data)
        st.success("Saved!")

    st.divider()
    st.caption("Data is saved locally in `study_data.json` next to app.py")


st.title(APP_TITLE)
st.caption(f"Welcome, **{data['profile']['name']}** — build consistent study habits with a clean dashboard.")

# Top KPIs
tasks_total = len(data["tasks"])
tasks_done = sum(1 for t in data["tasks"] if t.get("done"))
tasks_open = tasks_total - tasks_done

# sessions summary for last 7 days
sessions_df = pd.DataFrame(data["sessions"]) if data["sessions"] else pd.DataFrame(columns=["date", "hours", "topic", "notes"])
if not sessions_df.empty:
    sessions_df["date"] = pd.to_datetime(sessions_df["date"]).dt.date
    last_7 = date.today() - timedelta(days=6)
    recent = sessions_df[sessions_df["date"] >= last_7]
    hours_last_7 = float(recent["hours"].sum()) if not recent.empty else 0.0
else:
    hours_last_7 = 0.0

goal = float(data["profile"].get("weekly_goal_hours", 10))
progress = min(hours_last_7 / goal, 1.0) if goal > 0 else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("✅ Tasks done", f"{tasks_done}/{tasks_total}")
k2.metric("📌 Open tasks", f"{tasks_open}")
k3.metric("🕒 Hours (last 7 days)", f"{hours_last_7:.1f}")
k4.metric("🎯 Weekly goal progress", f"{int(progress*100)}%")

st.progress(progress)

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📌 Tasks", "🕒 Study Sessions", "🔥 Habits", "📊 Insights / Export"])


# ---------------------------
# TAB 1: Tasks
# ---------------------------
with tab1:
    left, right = st.columns([1, 1])

    with left:
        st.subheader("Add a task")
        with st.form("add_task_form", clear_on_submit=True):
            title = st.text_input("Task title", placeholder="e.g., Finish Streamlit chapter 3")
            subject = st.text_input("Subject / Track", placeholder="e.g., Python, Data Structures, ML")
            due = st.date_input("Due date", value=date.today() + timedelta(days=3))
            priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
            est_hours = st.number_input("Estimated hours", min_value=0.5, max_value=50.0, value=2.0, step=0.5)
            submitted = st.form_submit_button("➕ Add task", use_container_width=True)
        if submitted:
            if not title.strip():
                st.error("Please enter a task title.")
            else:
                add_task(data, title, subject, due, priority, est_hours)
                save_data(data)
                st.success("Task added!")

    with right:
        st.subheader("Task list")
        if not data["tasks"]:
            st.info("No tasks yet. Add one on the left.")
        else:
            # filters
            f1, f2, f3 = st.columns(3)
            status_filter = f1.selectbox("Status", ["All", "Open", "Done"])
            pr_filter = f2.selectbox("Priority", ["All", "High", "Medium", "Low"])
            subj_filter = f3.text_input("Subject contains", placeholder="e.g., Python")

            tasks = data["tasks"][:]
            # apply filters
            if status_filter == "Open":
                tasks = [t for t in tasks if not t.get("done")]
            elif status_filter == "Done":
                tasks = [t for t in tasks if t.get("done")]

            if pr_filter != "All":
                tasks = [t for t in tasks if t.get("priority") == pr_filter]

            if subj_filter.strip():
                s = subj_filter.strip().lower()
                tasks = [t for t in tasks if s in (t.get("subject", "").lower())]

            # sort by due date
            def due_key(t):
                d = parse_iso(t.get("due", "")) or date.max
                return (t.get("done", False), d)

            tasks.sort(key=due_key)

            for t in tasks:
                due_d = parse_iso(t["due"]) or date.today()
                days_left = (due_d - date.today()).days
                status_emoji = "✅" if t.get("done") else "📌"
                urgency = ""
                if not t.get("done"):
                    if days_left < 0:
                        urgency = "🔴 Overdue"
                    elif days_left == 0:
                        urgency = "🟠 Due today"
                    elif days_left <= 2:
                        urgency = "🟡 Due soon"

                with st.container(border=True):
                    c1, c2, c3 = st.columns([6, 2, 2])
                    new_done = c1.checkbox(
                        f"{status_emoji} **{t['title']}**  \n"
                        f"_{t.get('subject','')} • Priority: {t.get('priority')} • Est: {t.get('est_hours')}h • Due: {t['due']}_  \n"
                        f"{urgency}",
                        value=bool(t.get("done")),
                        key=f"done_{t['id']}",
                    )
                    if new_done != bool(t.get("done")):
                        toggle_task(data, t["id"], new_done)
                        save_data(data)
                        st.rerun()

                    if c2.button("🗑️ Delete", key=f"del_{t['id']}"):
                        delete_task(data, t["id"])
                        save_data(data)
                        st.rerun()

                    if c3.button("⏳ Add 1h session", key=f"quick_{t['id']}"):
                        add_session(data, date.today(), 1.0, t.get("subject", "Study"), f"Worked on: {t['title']}")
                        save_data(data)
                        st.success("Logged a 1h session for today!")


# ---------------------------
# TAB 2: Sessions
# ---------------------------
with tab2:
    st.subheader("Log a study session")
    c1, c2, c3 = st.columns([2, 1, 3])
    with c1:
        sess_date = st.date_input("Date", value=date.today(), key="sess_date")
    with c2:
        hours = st.number_input("Hours", min_value=0.25, max_value=12.0, value=1.0, step=0.25, key="sess_hours")
    with c3:
        topic = st.text_input("Topic", placeholder="e.g., Streamlit UI, OOP, Pandas", key="sess_topic")

    notes = st.text_area("Notes (optional)", placeholder="What did you learn? Any blockers?", key="sess_notes")

    if st.button("🕒 Log session", use_container_width=True):
        if not topic.strip():
            st.error("Please enter a topic.")
        else:
            add_session(data, sess_date, hours, topic, notes)
            save_data(data)
            st.success("Session saved!")
            st.rerun()

    st.divider()
    st.subheader("Recent sessions")

    if sessions_df.empty:
        st.info("No sessions logged yet.")
    else:
        # show last 30 sessions
        display_df = sessions_df.copy()
        display_df["date"] = pd.to_datetime(display_df["date"]).dt.date
        display_df = display_df.sort_values("date", ascending=False).head(30)
        st.dataframe(display_df, use_container_width=True, hide_index=True)


# ---------------------------
# TAB 3: Habits
# ---------------------------
with tab3:
    st.subheader("Habits & streaks")

    # Add new habit
    colA, colB = st.columns([3, 1])
    new_habit = colA.text_input("Add a habit", placeholder="e.g., Solve 3 problems", key="new_habit")
    if colB.button("➕ Add", use_container_width=True):
        add_habit(data, new_habit)
        save_data(data)
        st.rerun()

    if not data["habits"]:
        st.info("No habits yet.")
    else:
        for h in data["habits"]:
            last_done = h.get("last_done")
            streak = _safe_int(h.get("streak"), 0)

            with st.container(border=True):
                a, b, c = st.columns([5, 2, 2])
                a.markdown(f"**{h['name']}**  \nStreak: 🔥 **{streak}** day(s)  \nLast done: `{last_done or '—'}`")
                if b.button("✅ Done today", key=f"habit_done_{h['name']}"):
                    mark_habit_done(data, h["name"])
                    save_data(data)
                    st.rerun()
                if c.button("🗑️ Remove", key=f"habit_del_{h['name']}"):
                    delete_habit(data, h["name"])
                    save_data(data)
                    st.rerun()


# ---------------------------
# TAB 4: Insights / Export
# ---------------------------
with tab4:
    st.subheader("Insights")

    # Weekly hours chart (last 8 weeks)
    if sessions_df.empty:
        st.info("Log sessions to unlock charts and exports.")
    else:
        df = sessions_df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["week"] = df["date"].dt.to_period("W").astype(str)
        weekly = df.groupby("week", as_index=False)["hours"].sum().sort_values("week").tail(8)

        left, right = st.columns([1, 1])
        with left:
            st.markdown("**Weekly hours (last ~8 weeks)**")
            st.bar_chart(weekly.set_index("week")["hours"])

        with right:
            st.markdown("**Hours by topic (last 30 days)**")
            last_30 = datetime.now().date() - timedelta(days=29)
            df2 = df[df["date"].dt.date >= last_30].copy()
            if df2.empty:
                st.info("No sessions in the last 30 days.")
            else:
                topic_sum = df2.groupby("topic", as_index=False)["hours"].sum().sort_values("hours", ascending=False)
                st.bar_chart(topic_sum.set_index("topic")["hours"])

    st.divider()
    st.subheader("Export")

    # Export JSON
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    st.download_button(
        "⬇️ Download data as JSON",
        data=json_bytes,
        file_name="study_data_export.json",
        mime="application/json",
        use_container_width=True,
    )

    # Export CSV sessions
    if sessions_df.empty:
        st.download_button(
            "⬇️ Download sessions as CSV",
            data="date,hours,topic,notes\n",
            file_name="sessions.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=True,
        )
    else:
        csv_bytes = sessions_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download sessions as CSV",
            data=csv_bytes,
            file_name="sessions.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()
    st.subheader("Danger zone")
    c1, c2 = st.columns(2)
    if c1.button("🧹 Reset ALL data", use_container_width=True):
        data = default_data()
        save_data(data)
        st.success("All data reset.")
        st.rerun()
    if c2.button("🗑️ Delete local JSON file", use_container_width=True):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.success("Deleted JSON file.")
        st.rerun()