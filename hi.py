import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="🧠 Timetable Generator", layout="centered")
st.title("📅 Timetable Generator with Timings, Lunch & Free Periods")

st.markdown("### ⚙ Configuration")

# Config Inputs (in main area)
col1, col2 = st.columns(2)
with col1:
    num_days = st.slider("Number of Working Days", 5, 6, 5)
    periods_per_day = st.slider("Total Periods per Day (including Lunch)", 5, 10, 7)
with col2:
    lunch_period = st.slider("Lunch Break After Which Period (1-based)", 2, periods_per_day - 1, 4)
    period_duration = st.number_input("Each Period Duration (minutes)", 30, 90, 45)

start_time_str = st.text_input("⏰ School Start Time (HH:MM)", "09:00")

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:num_days]

st.markdown("### 📚 Subject Setup")
num_subjects = st.number_input("Number of Subjects", 1, 20, 6, step=1)
subjects_data = []

for i in range(num_subjects):
    st.markdown(f"#### Subject {i + 1}")
    cols = st.columns(3)
    subject = cols[0].text_input("Subject Name", key=f"subject_{i}")
    teacher = cols[1].text_input("Teacher Name", key=f"teacher_{i}")
    weekly_slots = cols[2].number_input("Weekly Periods", 1, num_days * periods_per_day, 4, key=f"slots_{i}")
    if subject:
        subjects_data.append({
            "subject": subject,
            "teacher": teacher,
            "slots": weekly_slots
        })

# Time slot generation
def generate_time_slots(start_time_str, num_periods, duration_mins):
    start = datetime.strptime(start_time_str, "%H:%M")
    times = []
    for _ in range(num_periods):
        end = start + timedelta(minutes=duration_mins)
        times.append(f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")
        start = end
    return times

# Timetable logic
def generate_timetable(subjects, days, periods, lunch_idx, period_times):
    timetable = {day: [""] * periods for day in days}
    all_slots = [(day, i) for day in days for i in range(periods) if i != lunch_idx]

    for day in days:
        timetable[day][lunch_idx] = "🍱 Lunch Break"

    subject_slots = []
    for subj in subjects:
        subject_slots.extend([(subj["subject"], subj["teacher"])] * subj["slots"])

    random.shuffle(all_slots)
    extra = len(all_slots) - len(subject_slots)
    subject_slots.extend([("Free Period", "")] * max(0, extra))

    for (day, idx), (subj, teacher) in zip(all_slots, subject_slots):
        timetable[day][idx] = subj if not teacher else f"{subj}\n({teacher})"

    # Build DataFrame with timings
    df_data = {"Period Time": period_times}
    for day in days:
        df_data[day] = timetable[day]

    return pd.DataFrame(df_data)

# Generate timetable
if st.button("🧠 Generate Timetable"):
    if not subjects_data:
        st.warning("⚠ Please input at least one subject.")
    else:
        lunch_idx = lunch_period - 1
        time_labels = generate_time_slots(start_time_str, periods_per_day, period_duration)
        df = generate_timetable(subjects_data, days, periods_per_day, lunch_idx, time_labels)

        st.success("✅ Timetable Generated with Timings!")

        def style_cells(val):
            if "Lunch" in val:
                return "background-color: #ffe082; font-weight: bold"
            elif "Free" in val:
                return "background-color: #e0e0e0"
            elif val:
                return "background-color: #d0f0fd"
            return ""

        st.dataframe(df.style.applymap(style_cells), use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download Timetable CSV", csv, "timetable_with_timings.csv", "text/csv")
