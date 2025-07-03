from backend.trend_analysis import get_trends
from backend.pattern_detection import detect_patterns

def get_recommendations():
    trends = get_trends()
    patterns = detect_patterns()
    recs = []

    # 🟥 1. Low mood in recent days
    if trends and trends.get("rolling_mean"):
        last_3_days = trends["rolling_mean"][-3:]
        if all(score <= 3 for score in last_3_days):
            recs.append(
                "😔 Your mood has been consistently low for the past few days. "
                "It might help to talk to someone you trust or reach out to a mental health professional."
            )
        elif sum(score <= 4 for score in last_3_days) >= 2:
            recs.append(
                "📉 You've had a few low mood days recently. "
                "Try activities that lift your spirits — a walk, music, or journaling can help."
            )

    # 🗓️ 2. Pattern: Low mood on specific days
    if patterns and patterns.get("low_mood_days"):
        for day, count in patterns["low_mood_days"].items():
            if count >= 2:
                recs.append(
                    f"📅 You often feel low on **{day}s**. Consider adding something enjoyable to your routine on those days — even a small positive action can make a difference."
                )

    # 🚨 3. Anomalies in behavior
    if patterns and patterns.get("anomalies"):
        recs.append(
            "🚨 We've noticed some unusual changes in your mood recently. "
            "If something specific is bothering you, writing about it may help process the emotions."
        )

    # ✅ 4. Positive encouragement
    if not recs:
        recs.append(
            "🌟 You're doing well! Keep nurturing positive habits like journaling, mindfulness, staying active, or connecting with loved ones."
        )

    return recs
