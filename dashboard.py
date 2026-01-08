import streamlit as st
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="PlainSight Dashboard",
    layout="wide",
)

# ---------------- SAMPLE DATA ----------------
USER = {
    "name": "Alex",
    "email": "alex@example.com",
    "privacy_mode": "Balanced",
}

HISTORY = [
    {
        "site": "amazon.com",
        "category": "Shopping",
        "risk_level": "Medium",
        "score": 5,
        "summary": "Collects device and purchase data. Shares with partners for analytics.",
        "takeaways": [
            "Device and purchase data is collected",
            "Data may be shared with third parties",
            "Retention period is not clearly stated"
        ]
    },
    
    {
        "site": "linkedin.com",
        "category": "Social",
        "risk_level": "High",
        "score": 8,
        "summary": "Extensive tracking and third-party sharing. Retention and deletion rights unclear.",
        "takeaways": [
            "Tracks user activity across sessions",
            "Shares data with advertisers and partners",
            "Deletion rights are unclear"
        ]
    },
    {
        "site": "notion.so",
        "category": "Productivity",
        "risk_level": "Low",
        "score": 2,
        "summary": "Minimal data collection with clear user controls.",
        "takeaways": [
            "Collects minimal account information",
            "No aggressive tracking detected",
            "User controls are clearly described"
        ]
    }
]

# ---------------- HELPERS ----------------
def risk_emoji(level):
    return {
        "Low": "🟢",
        "Medium": "🟡",
        "High": "🔴"
    }.get(level, "⚪")

# ---------------- HEADER ----------------
st.title("PlainSight")
st.caption("Your Privacy Risk Dashboard")

st.markdown("---")

# ---------------- OVERVIEW CARDS ----------------
total = len(HISTORY)
high = sum(1 for x in HISTORY if x["risk_level"] == "High")
medium = sum(1 for x in HISTORY if x["risk_level"] == "Medium")
low = sum(1 for x in HISTORY if x["risk_level"] == "Low")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Sites Analyzed", total)
c2.metric("High Risk", high, delta=None)
c3.metric("Medium Risk", medium, delta=None)
c4.metric("Low Risk", low, delta=None)

st.markdown("---")

# ---------------- ACTIVITY / HISTORY ----------------
st.subheader("Privacy Activity")

df = pd.DataFrame([
    {
        "Website": h["site"],
        "Category": h["category"],
        "Risk": f'{risk_emoji(h["risk_level"])} {h["risk_level"]}',
        "Score": f'{h["score"]}/10'
    }
    for h in HISTORY
])

st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("### Details")

for h in HISTORY:
    with st.expander(f'{risk_emoji(h["risk_level"])} {h["site"]} — {h["risk_level"]} ({h["score"]}/10)'):
        st.markdown(f"**Summary:** {h['summary']}")
        st.markdown("**Key Takeaways:**")
        for t in h["takeaways"]:
            st.markdown(f"- {t}")

st.markdown("---")

# ---------------- PROFILE ----------------
st.subheader("Profile")

p1, p2 = st.columns(2)
p1.write(f"**Name:** {USER['name']}")
p1.write(f"**Email:** {USER['email']}")
p2.write(f"**Privacy Mode:** {USER['privacy_mode']}")
p2.write("**Last Scan:** Today")

st.markdown("---")

# ---------------- AWARENESS ----------------
st.subheader("Privacy Awareness")

st.markdown("""
**Why does privacy risk matter?**  
Every website you sign up for collects data. Some collect more than necessary, share it with third parties, or retain it indefinitely.

**What does a High risk score mean?**
- Extensive tracking
- Third-party data sharing
- Unclear user rights

**How PlainSight helps**
- Reads privacy policies for you
- Flags risky practices
- Shows *why* a site is risky in plain English
""")

st.markdown("---")
st.caption("PlainSight • Privacy made understandable")
