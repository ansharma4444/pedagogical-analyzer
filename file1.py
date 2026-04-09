
import streamlit as st
import textstat
import pandas as pd
import plotly.express as px

# Set page config for a professional look
st.set_page_config(page_title="Pedagogical Analyzer", layout="wide")

st.title("📊 Pedagogical Alignment Dashboard")
st.markdown("---")

def get_cognitive_level(text):
    """
    Analyzes text for Bloom's Taxonomy verbs to determine the cognitive level.
    """
    taxonomy = {
        "Creating": ["design", "construct", "develop", "formulate", "investigate"],
        "Evaluating": ["judge", "select", "critique", "justify", "recommend"],
        "Analyzing": ["compare", "contrast", "examine", "question", "test"],
        "Applying": ["calculate", "solve", "illustrate", "use", "demonstrate", "induction"],
        "Understanding": ["describe", "explain", "identify", "locate", "report"],
        "Remembering": ["list", "memorize", "state", "define", "repeat"]
    }
    
    text_lower = text.lower()
    for level, verbs in taxonomy.items():
        if any(verb in text_lower for verb in verbs):
            return level
    return "Understanding"  # Default level if no verbs match

# 1. Input Section
with st.sidebar:
    st.header("Analyze New Content")
    app_name = st.text_input("App Name", placeholder="e.g. Khan Academy")
    target_grade = st.slider("Target Grade", 1, 12, 5)
    content_text = st.text_area("Paste Lesson Text here...", height=200)
    
    if st.button("Analyze Alignment"):
        if app_name and content_text:
            # 1. REAL Readability Analysis with Capping at 12.0 and Rounding
            raw_grade = textstat.flesch_kincaid_grade(content_text)
            reading_grade = round(min(12.0, raw_grade), 1)
            
            # 2. REAL Cognitive Level Analysis
            cog_level = get_cognitive_level(content_text)
        
            # 3. Alignment Score Calculation
            alignment_score = round(max(0, 100 - abs(target_grade - reading_grade) * 10), 1)
            
            new_data = {
                "App Name": app_name,
                "Target Grade": target_grade,
                "Reading Grade": reading_grade,
                "Cognitive Level": cog_level,
                "Alignment Score": alignment_score
            }
            
            # Save to session state
            if 'results_db' not in st.session_state:
                st.session_state.results_db = pd.DataFrame(columns=new_data.keys())
            
            st.session_state.results_db = pd.concat([
                st.session_state.results_db, 
                pd.DataFrame([new_data])
            ], ignore_index=True)
            st.success(f"Analysis for {app_name} added!")
        else:
            st.warning("Please enter both an App Name and Lesson Text.")

# 2. Results Dashboard
if 'results_db' in st.session_state and not st.session_state.results_db.empty:
    df = st.session_state.results_db
    
    # Summary Metrics for the latest entry
    latest = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Reading Grade", f"Lvl {latest['Reading Grade']}")
    col2.metric("Cognitive Level", latest['Cognitive Level'])
    col3.metric("Alignment Score", f"{latest['Alignment Score']}%")
    
    st.markdown("---")
    
    # 3. Visualization
    st.subheader("Alignment Trends")
    
    fig = px.scatter(
        df, 
        x="Target Grade", 
        y="Reading Grade",
        size=df["Alignment Score"].astype(float).tolist(),
        color=df["Cognitive Level"].tolist(),
        hover_name="App Name",
        size_max=30,
        range_x=[0, 13], # Keeps the chart scale consistent
        range_y=[0, 13],
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Safe,
        labels={"color": "Cognitive Level", "Reading Grade": "Actual Grade"}
    )
    
    # Add a diagonal 'Perfect Alignment' line
    fig.add_shape(type="line", x0=1, y0=1, x1=12, y1=12, 
                  line=dict(color="Red", dash="dot"))
    
    st.plotly_chart(fig, use_container_width=True)

    # 4. Raw Data Logs
    with st.expander("View Full Research Logs"):
        st.dataframe(df, use_container_width=True)
else:
    # This is the hint message you wanted
    st.info("👈 Enter app details in the sidebar and click 'Analyze Alignment' to see the analysis.")