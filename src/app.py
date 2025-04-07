import streamlit as st
import requests
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Custom branding configuration
BRAND_LOGO = os.path.join(os.path.dirname(__file__), "images.png")  # Relative path from script location
BRAND_COLOR = "#1E90FF"  # Default color (Dodger Blue)

# Set page configuration
st.set_page_config(
    page_title="SHL Assessment Recommendation Engine",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom styling
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: #1C2526;
            color: white;
        }}
        .stButton>button {{
            background-color: {BRAND_COLOR};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
        }}
        .stButton>button:hover {{
            background-color: #{BRAND_COLOR[:6]}CC;
        }}
        .stTable tr th {{
            background-color: {BRAND_COLOR};
            color: white;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: {BRAND_COLOR};
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #2A2F32;
        }}
        a {{
            color: {BRAND_COLOR};
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar for settings
with st.sidebar:
    try:
        st.image(BRAND_LOGO, width=200, caption="SHL Logo")
    except FileNotFoundError:
        st.warning("Logo file 'images.png' not found. Please ensure it is in the src directory.")
    st.title("Settings")
    max_duration = st.slider("Max Duration (minutes)", 10, 60, 40, key="max_duration_slider")
    mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0)
    st.markdown(f'<body class="{mode.lower()}-mode">', unsafe_allow_html=True)

# Main content
st.title("SHL Assessment Recommendation Engine")
st.write("Powered by RAG, LLM Parsing, and Real-Time Insights")
st.write("Enter your query or job description:")

query = st.text_input("Input Query", key="query_input", value="", placeholder="Enter the query")
url = st.text_input("Job Description URL", key="url_input", value="", placeholder="Enter URL (optional)")

if st.button("Get Recommendations", key="recommend_button"):
    if not query.strip() and not url.strip():
        st.write("Please enter a query or URL.")
    else:
        query_text = query
        if url.strip():
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                query_text = response.text
            except requests.RequestException as e:
                st.error(f"Failed to fetch URL: {str(e)}")
        try:
            response = requests.get(f"http://localhost:8000/recommend?query={query_text}")
            if response.status_code == 200:
                data = response.json()
                st.write("### Recommended Assessments")
                if data.get("recommendations") and len(data["recommendations"]) > 0:
                    df = pd.DataFrame(data["recommendations"])
                    # Filter by max duration
                    df["duration_min"] = df["duration"].str.extract(r"(\d+)").astype(float)
                    df = df[df["duration_min"] <= max_duration].drop(columns=["duration_min"])
                    # Ensure all required columns are present
                    required_columns = ["name", "url", "remote", "adaptive", "duration", "type", "reasoning", "confidence"]
                    for col in required_columns:
                        if col not in df.columns:
                            df[col] = "N/A"
                    # Convert URL to clickable link
                    df["url"] = df["url"].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
                    # Create HTML table
                    table_html = df[["name", "url", "remote", "adaptive", "duration", "type", "reasoning"]].to_html(escape=False, index=False)
                    st.markdown(table_html, unsafe_allow_html=True)
                    # Analytics Dashboard with Graphs
                    st.write("### Recommendation Insights")
                    total_recommendations = len(df)
                    # Bar Chart: Confidence Scores
                    fig1 = px.bar(df, x="name", y="confidence", title="Confidence", color_discrete_sequence=[BRAND_COLOR])
                    fig1.update_layout(xaxis_tickangle=45, height=150, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig1)
                    # Pie Chart: Distribution of Assessment Types
                    fig2 = px.pie(df, names="type", title="Type Distribution", hole=0.3, color_discrete_sequence=px.colors.sequential.Viridis)
                    fig2.update_layout(height=150, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig2)
                    # Bar Chart: Duration
                    fig3 = px.bar(df, x="name", y=df["duration"].str.extract(r"(\d+)").astype(float)[0], title="Duration", color_discrete_sequence=["green"])
                    fig3.update_layout(xaxis_tickangle=45, height=150, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig3)
                else:
                    st.write("No assessments meet the specified criteria.")
            else:
                st.error(f"Error fetching recommendations. Status code: {response.status_code}")
        except requests.RequestException as e:
            st.error(f"Failed to connect to the API: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")