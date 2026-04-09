
import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config for a professional look
st.set_page_config(page_title="Pedagogical Analyzer", layout="wide")

st.title("📊 Pedagogical Alignment Dashboard")
st.markdown("---")

# 1. Input Section
with st.sidebar:
    st.header("Analyze New Content")
    app_name = st.text_input("App Name", placeholder="e.g. Khan Academy")
    target_grade = st.slider("Target Grade", 1, 12, 5)
    content_text = st.text_area("Paste Lesson Text here...", height=200)
    
    if st.button("Analyze Alignment"):
        # Placeholder for your analysis logic (Readability + Bloom's)
        # In your real code, replace these with your NLP functions
        reading_grade = 5.2  # Result from Flesch-Kincaid
        cog_level = "Understanding" # Result from keyword/LLM check
        
        # Alignment Score: 100% minus the absolute gap between Reading and Target
        alignment_score = max(0, 100 - abs(target_grade - reading_grade) * 10)
        
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
    
    # 3. Visualization (The fix for your previous error)
    st.subheader("Alignment Trends")
    
    # We pass the 'df' directly to Plotly to avoid Narwhals type errors
    fig = px.scatter(
    df, 
    x="Target Grade", 
    y="Reading Grade",
    size=df["Alignment Score"].astype(float).tolist(), # Convert to standard list
    color=df["Cognitive Level"].tolist(),             # Convert to standard list
    hover_name="App Name",
    size_max=30,
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
    st.info("👈 Enter app details in the sidebar to begin analysis.")