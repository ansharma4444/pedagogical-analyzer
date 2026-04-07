
import streamlit as st
import textstat
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Pedagogical Analyzer", layout="wide")

st.title("🎓 Pedagogical Alignment Analyzer")
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Data")
    app_name = st.text_input("Learning App Name", placeholder="e.g., Duolingo")
    target_grade = st.slider("Target Student Grade Level", 1, 12, 5)
    sample_text = st.text_area("Paste Sample Content/Lesson Text Here", height=200)
    analyze_button = st.button("Run Alignment Analysis")

# Main Logic
if analyze_button and sample_text:
    # 1. Calculate Readability
    actual_grade = textstat.flesch_kincaid_grade(sample_text)
    ease_score = textstat.flesch_reading_ease(sample_text)
    
    # 2. Simple Alignment Logic
    diff = abs(actual_grade - target_grade)
    alignment_score = max(0, 100 - (diff * 10))

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Alignment Score", f"{alignment_score}%")
    col2.metric("Reading Level", f"Grade {actual_grade}")
    col3.metric("Ease Score", ease_score)

    # 3. Data Visualization (The Analytics Part)
    st.subheader("Data Visualization")
    chart_data = pd.DataFrame({
        "Category": ["Target Grade", "Actual Grade"],
        "Grade Level": [target_grade, actual_grade]
    })
    
    fig = px.bar(chart_data, x="Category", y="Grade Level", color="Category", 
                 title=f"Gap Analysis for {app_name}")
    st.plotly_chart(fig)

    # 4. Pedagogical Feedback
    if alignment_score < 70:
        st.error(f"⚠️ **Misalignment Detected:** The content is likely too difficult for a Grade {target_grade} student.")
    else:
        st.success("✅ **Good Alignment:** The content complexity matches the target audience's cognitive level.")
else:
    st.info("👈 Enter app details in the sidebar and click 'Run' to see the analysis.")


