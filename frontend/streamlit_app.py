import streamlit as st
import requests
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# ===========================
# Constants & Config
# ===========================
BACKEND_URL = "http://localhost:8000"
MOOD_OPTIONS = {
    "Happy": ["productive", "excited", "energetic", "joy", "fun", "family", "relaxed"],
    "Sad": ["tired", "down", "low", "sad", "lonely", "crying"],
    "Angry": ["frustrated", "annoyed", "irritated", "upset"],
    "Anxious": ["worried", "nervous", "stressed", "overwhelmed"],
    "Calm": ["peaceful", "content", "neutral", "chill"],
    "Tired": ["sleepy", "lazy", "exhausted", "drained"],
    "Surprised": ["shocked", "amazed", "unexpected"],
    "Other": ["work", "routine", "normal", "average"]
}
MOOD_EMOJIS = {
    "Happy": "😊",
    "Sad": "😢",
    "Angry": "😡",
    "Anxious": "😱",
    "Calm": "😐",
    "Tired": "😴",
    "Surprised": "🤗",
    "Other": "😐"
}
CLUSTER_LABELS = {
    0: "Generally anxious but improving",
    1: "Highly volatile",
    2: "Calm and consistent"
}

# ===========================
# Helper Functions
# ===========================
def get_backend_data(endpoint: str):
    """Fetch data from the backend API."""
    try:
        resp = requests.get(f"{BACKEND_URL}/{endpoint}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"⚠️ Error fetching {endpoint}: {e}")
        st.stop()

def post_mood_entry(data: dict):
    """Post a new mood entry to the backend."""
    try:
        resp = requests.post(f"{BACKEND_URL}/mood_entry", json=data)
        if resp.status_code == 200:
            st.success("✅ Mood entry submitted successfully!")
        else:
            st.error("❌ Failed to submit mood entry. Please try again.")
    except Exception as e:
        st.error(f"❌ Error connecting to backend: {e}")

def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    return pd.to_datetime(date_str).strftime("%A, %Y-%m-%d")

# ===========================
# 🧠 Mental Health Mood Tracker App
# ===========================
st.set_page_config(page_title="🧠 Mental Health Mood Tracker", layout="wide")
st.title("🌤️ Mental Health Mood Tracker")

# ===========================
# 🚀 Mood Logging Section
# ===========================
with st.container():
    st.header("📝 Log Today's Mood")
    col1, col2 = st.columns(2)

    with col1:
        mood = st.selectbox("Select your mood", list(MOOD_OPTIONS.keys()))
        mood_score = st.slider("Mood Score (1 - low, 10 - high)", 1, 10, 5)
        emoji = MOOD_EMOJIS[mood]

    with col2:
        tags = st.multiselect("Select tags that fit your mood", MOOD_OPTIONS[mood])
        custom_tag = st.text_input("Add a custom tag (optional)")
        journal = st.text_area("Write a quick journal (optional)", height=150)

    if st.button("📩 Submit Entry"):
        all_tags = tags.copy()
        if custom_tag:
            all_tags.append(custom_tag)
        data = {
            "mood_score": mood_score,
            "emoji": emoji,
            "tags": ", ".join(all_tags),
            "journal_text": journal
        }
        post_mood_entry(data)

st.markdown("---")

# ===========================
# 📊 Mood Insights Dashboard
# ===========================
st.header("📊 Mood Dashboard & Insights")

entries = get_backend_data("mood_entries")
trends = get_backend_data("trends")
patterns = get_backend_data("patterns")
recs = get_backend_data("recommendations")

# Mood Trend Bar Chart
if trends and "dates" in trends:
    with st.container():
        st.subheader("📊 Mood Trend Over Time (Bar Chart)")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=trends["dates"], y=trends["mood_scores"], name='Daily Mood', marker_color='skyblue'))
        fig.add_trace(go.Scatter(x=trends["dates"], y=trends["rolling_mean"],
                                 mode='lines', name='7-Day Rolling Average', line=dict(color='orange', width=3)))
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=600,
            plot_bgcolor="#f9f9f9",
            xaxis_title="Date",
            yaxis_title="Mood Score",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

# Word Cloud from Journals
if entries and any(e.get("journal_text") for e in entries):
    with st.container():
        st.subheader("🌐 Word Cloud from Journal Entries")
        text = " ".join([e.get("journal_text", "") for e in entries if e.get("journal_text")])
        wc = WordCloud(width=400, height=150, background_color='white').generate(text)
        plt.figure(figsize=(5, 1.5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)

# Weekly Summary & Low Mood Dates
if patterns:
    with st.container():
        st.subheader("🗓️ Weekly Summary & Detected Patterns")
        # Show last 7 days' moods with cluster labels
        if patterns.get("last_7_days"):
            st.markdown("**🕖 Last 7 Days' Moods:**")
            for day in patterns["last_7_days"]:
                date_str = format_date(day["timestamp"])
                label = CLUSTER_LABELS.get(day["cluster"], "")
                st.write(f"{date_str} | Mood Score: {day['mood_score']} | {label}")
        # Existing low mood dates logic
        if entries:
            low_mood_entries = [
                e for e in entries
                if "mood_score" in e and e["mood_score"] <= 3 and "timestamp" in e
            ]
            if low_mood_entries:
                st.markdown("**😔 Low Mood Dates:**")
                for e in low_mood_entries:
                    date_obj = pd.to_datetime(e["timestamp"])
                    days_ago = (datetime.now() - date_obj).days
                    st.write(f"{date_obj.strftime('%A, %Y-%m-%d')} ({days_ago} days ago)")
            else:
                st.write("No recent low mood days.")

# Recommendations Section
if recs:
    with st.container():
        st.subheader("💡 Personalized Recommendations")
        for rec in recs:
            st.info(f"👉 {rec}") 