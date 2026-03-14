import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import base64

# -------------------------------------------------
# IMAGE LOAD (LOCAL BACKGROUND)
# -------------------------------------------------

def get_base64_of_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_base64_of_image(r"C:\Users\amanr\Downloads\hailey-climate-main\hailey-climate-main\project\pyclimax expolorer\304765158-615003676989374-3689670236967468275-n.jpg")

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="PyClimaExplorer",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM DASHBOARD CSS (BACKGROUND ADDED)
# -------------------------------------------------

st.markdown(f"""
<style>

.stApp{{
background:
linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.85)),
url("data:image/jpg;base64,{img}");
background-size:cover;
background-position:center;
background-attachment:fixed;
color:white;
font-family:Segoe UI;
}}

.title{{
font-size:34px;
font-weight:600;
color:#4fffd2;
}}

.navbar{{
display:flex;
gap:15px;
margin-top:10px;
margin-bottom:20px;
}}

.navbtn{{
padding:8px 16px;
border-radius:10px;
background:rgba(255,255,255,0.08);
border:1px solid rgba(255,255,255,0.12);
}}

.card{{
background:rgba(255,255,255,0.05);
padding:20px;
border-radius:16px;
border:1px solid rgba(255,255,255,0.08);
box-shadow:0px 6px 20px rgba(0,0,0,0.3);
}}

.metric{{
text-align:center;
padding:12px;
border-radius:12px;
background:rgba(255,255,255,0.06);
border:1px solid rgba(255,255,255,0.08);
}}

section[data-testid="stSidebar"]{{
background:#0c1518;
}}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.markdown('<div class="title">🌍 PyClimaExplorer</div>', unsafe_allow_html=True)

st.markdown("""
<div class="navbar">
<span class="navbtn">Explore</span>
<span class="navbtn">Compare Years</span>
<span class="navbtn">Story Mode</span>
<span class="navbtn">Export</span>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

with st.sidebar:

    st.title("Controls")

    with st.expander("📂 Dataset", expanded=True):
        st.file_uploader("Upload NetCDF (.nc)")

    with st.expander("🌡 Variable Selection"):
        variable = st.selectbox(
            "Variable",
            ["Temperature", "Precipitation", "Pressure"]
        )

    with st.expander("⏱ Time Controls"):
        time_step = st.slider("Time Step",0,365,120)

    with st.expander("📍 Coordinates"):
        lat = st.number_input("Latitude", value=28.6)
        lon = st.number_input("Longitude", value=77.2)

    with st.expander("🎨 Color Settings"):
        palette = st.selectbox(
            "Color Palette",
            ["Turbo","Viridis","Plasma","RdBu"]
        )

# -------------------------------------------------
# DATASET INFO CARDS
# -------------------------------------------------

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric">📂 Dataset<br>era5_temp_2020.nc</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric">📊 Variables<br>4</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric">📅 Coverage<br>2020</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric">🌍 Resolution<br>0.25°</div>', unsafe_allow_html=True)

st.write("")

# -------------------------------------------------
# FAKE DATA (DEMO)
# -------------------------------------------------

lat_vals = np.linspace(-90,90,60)
lon_vals = np.linspace(-180,180,120)

heat = np.random.normal(15,8,(60,120))

time = np.arange(0,365)
temp = np.sin(time/40)*10 + 20 + np.random.normal(0,1,365)

# -------------------------------------------------
# MAIN DASHBOARD
# -------------------------------------------------

colA,colB = st.columns(2)

with colA:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("Spatial Heatmap")

    fig = px.imshow(
        heat,
        x=lon_vals,
        y=lat_vals,
        color_continuous_scale=palette,
        labels=dict(color=variable)
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        height=450
    )

    st.plotly_chart(fig,use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with colB:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("Climate Time Series")

    df = pd.DataFrame({
        "day":time,
        "temperature":temp
    })

    fig2 = px.line(
        df,
        x="day",
        y="temperature",
        markers=True
    )

    fig2.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title=variable,
        height=450
    )

    st.plotly_chart(fig2,use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)