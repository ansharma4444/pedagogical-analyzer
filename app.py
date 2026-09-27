"""
app.py
Streamlit UI for the Pedagogical Alignment Dashboard.

This file only handles layout and user interaction. All analysis logic
lives in analyzer.py and all persistence logic lives in storage.py, so
each piece can be tested, reused, or replaced independently.

Run with:  streamlit run app.py
"""

import streamlit as st
import plotly.express as px

from analyzer import analyze_text
from storage import load_results, save_results, append_result

st.set_page_config(page_title="Pedagogical Analyzer", layout="wide", page_icon="📊")

st.title("📊 Pedagogical Alignment Dashboard")
st.caption(
    "Checks whether a piece of lesson content matches its intended grade level "
    "(via Flesch-Kincaid readability) and its cognitive demand (via Bloom's Taxonomy)."
)
st.markdown("---")

if "results_db" not in st.session_state:
    st.session_state.results_db = load_results()

# ---------------------------------------------------------------------------
# 1. Input section
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Analyze New Content")
    app_name = st.text_input("App / Lesson Name", placeholder="e.g. Khan Academy — Fractions 101")
    target_grade = st.slider("Target Grade", 1, 12, 5)
    content_text = st.text_area("Paste lesson text here...", height=220)

    if st.button("Analyze Alignment", type="primary"):
        if app_name and content_text.strip():
            record = analyze_text(app_name, target_grade, content_text)
            st.session_state.results_db = append_result(st.session_state.results_db, record)
            st.success(f"Analysis for '{app_name}' added and saved.")
        else:
            st.warning("Please enter both a name and some lesson text.")

    st.markdown("---")
    if not st.session_state.results_db.empty:
        st.download_button(
            "⬇️ Download all results (CSV)",
            data=st.session_state.results_db.to_csv(index=False),
            file_name="pedagogical_analysis_results.csv",
            mime="text/csv",
        )
        if st.button("Clear all saved results"):
            st.session_state.results_db = st.session_state.results_db.iloc[0:0]
            save_results(st.session_state.results_db)
            st.rerun()

# ---------------------------------------------------------------------------
# 2. Results dashboard
# ---------------------------------------------------------------------------
df = st.session_state.results_db

if not df.empty:
    latest = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Reading Grade", f"Lvl {latest['Reading Grade']}")
    col2.metric("Cognitive Level", latest["Cognitive Level"])
    col3.metric("Alignment Score", f"{latest['Alignment Score']}%")

    st.markdown("---")
    st.subheader("Alignment Trends")

    fig = px.scatter(
        df,
        x="Target Grade",
        y="Reading Grade",
        size=df["Alignment Score"].astype(float),
        color=df["Cognitive Level"],
        hover_name="App Name",
        size_max=30,
        range_x=[0, 13],
        range_y=[0, 13],
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Safe,
        labels={"color": "Cognitive Level", "Reading Grade": "Actual Grade"},
    )
    fig.add_shape(type="line", x0=1, y0=1, x1=12, y1=12, line=dict(color="Red", dash="dot"))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View full research logs"):
        st.dataframe(df, use_container_width=True)
else:
    st.info("👈 Enter lesson details in the sidebar and click 'Analyze Alignment' to get started.")
