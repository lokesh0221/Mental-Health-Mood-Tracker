import streamlit as st
import requests
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import calplot
import pandas as pd
import calendar
from datetime import datetime

# Backend API endpoint
BACKEND_URL = "http://localhost:8000"

# Page setup
st.set_page_config(page_title="🧠 Mental Health Mood Tracker", layout="wide")
st.title("🌤️ Mental Health Mood Tracker")

# ===========================
# 🚀 Mood Logging Section
# ===========================
with st.container():
    st.header("📝 Log Today's Mood")
    col1, col2 = st.columns(2)

    # Mood options and tags mapping
    mood_options = {
        "Happy": ["productive", "excited", "energetic", "joy", "fun", "family", "relaxed"],
        "Sad": ["tired", "down", "low", "sad", "lonely", "crying"],
        "Angry": ["frustrated", "annoyed", "irritated", "upset"],
        "Anxious": ["worried", "nervous", "stressed", "overwhelmed"],
        "Calm": ["peaceful", "content", "neutral", "chill"],
        "Tired": ["sleepy", "lazy", "exhausted", "drained"],
        "Surprised": ["shocked", "amazed", "unexpected"],
        "Other": ["work", "routine", "normal", "average"]
    }
    mood_emojis = {
        "Happy": "😊",
        "Sad": "😢",
        "Angry": "😡",
        "Anxious": "😱",
        "Calm": "😐",
        "Tired": "😴",
        "Surprised": "🤗",
        "Other": "😐"
    }

    with col1:
        mood = st.selectbox("Select your mood", list(mood_options.keys()))
        mood_score = st.slider("Mood Score (1 - low, 10 - high)", 1, 10, 5)
        emoji = mood_emojis[mood]

    with col2:
        tags = st.multiselect("Select tags that fit your mood", mood_options[mood])
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
        try:
            resp = requests.post(f"{BACKEND_URL}/mood_entry", json=data)
            if resp.status_code == 200:
                st.success("✅ Mood entry submitted successfully!")
            else:
                st.error("❌ Failed to submit mood entry. Please try again.")
        except Exception as e:
            st.error(f"❌ Error connecting to backend: {e}")

st.markdown("---")

# ===========================
# 📊 Mood Insights Dashboard
# ===========================
st.header("📊 Mood Dashboard & Insights")

# Fetch backend data
try:
    entries = requests.get(f"{BACKEND_URL}/mood_entries").json()
    trends = requests.get(f"{BACKEND_URL}/trends").json()
    patterns = requests.get(f"{BACKEND_URL}/patterns").json()
    recs = requests.get(f"{BACKEND_URL}/recommendations").json()
except Exception as e:
    st.error(f"⚠️ Error fetching data from backend: {e}")
    st.stop()

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