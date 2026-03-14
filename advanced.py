import streamlit as st 
import numpy as np
import pandas as pd
import xarray as xr
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import base64
import geopandas as gpd  # NEW

# Path where you unzipped Natural Earth countries  (ADJUST if different)
NE_COUNTRIES_PATH = r"C:\Users\TUSHAR SRIVASTAVA\Desktop\Project\ne_110m_admin_0_countries.shp"

WORLD_GDF = gpd.read_file(NE_COUNTRIES_PATH)
WORLD_GDF = WORLD_GDF.to_crs("EPSG:4326")  # ensure lat/lon

def make_globe_figure(lon, lat, values, title="3D Climate Globe"):
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    lon_rad = np.deg2rad(lon_grid)
    lat_rad = np.deg2rad(lat_grid)

    R = 1.0

    x = R * np.cos(lat_rad) * np.cos(lon_rad)
    y = R * np.cos(lat_rad) * np.sin(lon_rad)
    z = R * np.sin(lat_rad)

    vmin = np.nanmin(values)
    vmax = np.nanmax(values)
    if vmax == vmin:
        surfacecolor = np.zeros_like(values)
    else:
        surfacecolor = (values - vmin) / (vmax - vmin)

    fig = go.Figure()

    # Base climate globe
    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        surfacecolor=surfacecolor,
        colorscale="RdBu_r",
        cmin=0, cmax=1,
        showscale=True,
        colorbar=dict(title="Value"),
        opacity=0.9,
    ))

    # --- Add country borders from Natural Earth ---
    for _, row in WORLD_GDF.iterrows():
        geom = row.geometry
        if geom is None:
            continue

        if geom.geom_type == "Polygon":
            polys = [geom]
        elif geom.geom_type == "MultiPolygon":
            polys = list(geom.geoms)
        else:
            continue

        for poly in polys:
            xs, ys = poly.exterior.coords.xy
            lons = np.array(xs)
            lats = np.array(ys)

            lon_r = np.deg2rad(lons)
            lat_r = np.deg2rad(lats)

            x_line = (R * np.cos(lat_r) * np.cos(lon_r)).tolist()
            y_line = (R * np.cos(lat_r) * np.sin(lon_r)).tolist()
            z_line = (R * np.sin(lat_r)).tolist()

            fig.add_trace(go.Scatter3d(
                x=x_line,
                y=y_line,
                z=z_line,
                mode="lines",
                line=dict(color="black", width=1),
                showlegend=False,
                hoverinfo="none",
            ))

        fig.update_layout(
        title=title,
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            # turn off the grey cube behind the globe
            xaxis_backgroundcolor="rgba(0,0,0,0)",
            yaxis_backgroundcolor="rgba(0,0,0,0)",
            zaxis_backgroundcolor="rgba(0,0,0,0)",
        ),
        # make the plot area and outer paper fully transparent
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        # you can keep template or drop it; template won't override the rgba settings
        template="plotly_dark",
    )

    
    return fig

# -------------------------------------------------
# IMAGE LOAD (LOCAL BACKGROUND)
# -------------------------------------------------
def get_base64_of_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_base64_of_image(
    r"C:\Users\TUSHAR SRIVASTAVA\Desktop\Project\photo.jpg"
)

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="PyClimaExplorer",
    layout="wide"
)

# -------------------------------------------------
# SESSION STATE for navigation
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Explore"

# -------------------------------------------------
# CUSTOM DASHBOARD CSS
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

/* Style st.button navbar to look like original .navbtn */
div[data-testid="stHorizontalBlock"] div[data-testid="column"] button {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: Segoe UI !important;
    width: 100% !important;
    padding: 8px 16px !important;
}}
div[data-testid="stHorizontalBlock"] div[data-testid="column"] button:hover {{
    background: rgba(79,255,210,0.18) !important;
    border-color: #4fffd2 !important;
    color: #4fffd2 !important;
}}

/* Glass overlay card shown for non-Explore pages */
.glass-overlay {{
    background: rgba(0,0,0,0.52);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 70px 40px 50px 40px;
    margin-top: 14px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 8px 36px rgba(0,0,0,0.5);
    min-height: 400px;
    text-align: center;
}}
.glass-icon  {{ font-size:58px; margin-bottom:18px; }}
.glass-title {{ font-size:26px; font-weight:600; color:#4fffd2; margin-bottom:10px; }}
.glass-sub   {{ font-size:15px; color:rgba(255,255,255,0.5); max-width:500px;
                margin:0 auto 36px auto; line-height:1.7; }}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown('<div class="title">🌍 PyClimaExplorer</div>', unsafe_allow_html=True)

# -------------------------------------------------
# NAVBAR
# -------------------------------------------------
nav_cols = st.columns([1, 1.4, 1.2, 1, 6])
with nav_cols[0]:
    if st.button("Explore"):
        st.session_state.page = "Explore"
        st.rerun()
with nav_cols[1]:
    if st.button("Compare"):
        st.session_state.page = "Compare"
        st.rerun()
with nav_cols[2]:
    if st.button("Story Mode"):
        st.session_state.page = "Story Mode"
        st.rerun()
with nav_cols[3]:
    if st.button("Export"):
        st.session_state.page = "Export"
        st.rerun()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.title("Controls")
    with st.expander("📂 Dataset", expanded=True):
        uploaded_file = st.file_uploader("Upload NetCDF (.nc)", type=["nc"])
    with st.expander("🌡 Variable Selection"):
        variable_override = st.text_input("Preferred variable name (optional)", value="")
    with st.expander("⏱ Time Controls"):
        time_index = st.number_input("Time index (for 3D data)", min_value=0, value=0, step=1)
    with st.expander("🎨 Color Settings"):
        palette = st.selectbox("Color Palette", ["RdBu_r","Turbo","Viridis","Plasma","RdBu"])

    # -------------------------------------------------
# GLOBAL DATASET LOADING (available on all pages)
# -------------------------------------------------
# -------------------------------------------------
# GLOBAL DATASET LOADING (used by all pages)
# -------------------------------------------------
ds = None
if uploaded_file is not None:
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            path = tmp.name
        try:
            ds = xr.open_dataset(path)
        except ValueError:
            ds = xr.open_dataset(path, decode_times=False)
    except Exception as e:
        st.error("Error reading dataset — unsupported format or corrupted file.")
        st.write(e)
        ds = None



# -------------------------------------------------
# HELPER — glass overlay
# -------------------------------------------------
def show_glass_placeholder(icon, title, subtitle):
    st.markdown(
        f"""
        <div class="glass-overlay">
            <div class="glass-icon">{icon}</div>
            <div class="glass-title">{title}</div>
            <div class="glass-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    back_col = st.columns([2.5, 1, 2.5])
    with back_col[1]:
        if st.button("⬅ Back to Explore", key=f"back_{title}"):
            st.session_state.page = "Explore"
            st.rerun()

# -------------------------------------------------
# NON-EXPLORE PAGES
# -------------------------------------------------
if st.session_state.page == "Compare":
    if ds is None:
        show_glass_placeholder(
            "📅",
            "Compare",
            "Upload a dataset on the Explore page first."
        )

    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Compare Two Time Slices")

        col_left, col_right = st.columns(2)

        # Dataset-level time dimension
        if "time" in ds.dims:
            time_dim_ds = "time"
        elif "TIME" in ds.dims:
            time_dim_ds = "TIME"
        else:
            st.info("Dataset has no time dimension to compare.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.stop()

        times = ds[time_dim_ds].values

        with col_left:
            t1 = st.select_slider(
                "Time A",
                options=list(range(len(times))),
                key="cmp_t1"
            )
        with col_right:
            t2 = st.select_slider(
                "Time B",
                options=list(range(len(times))),
                key="cmp_t2"
            )

        # Variable selection
        var_list = list(ds.data_vars)
        variable_cmp = st.selectbox(
            "Variable to compare",
            var_list,
            index=0,
            key="cmp_var"
        )
        data_cmp = ds[variable_cmp]

        # Figure out which time dimension this variable actually has
        if "time" in data_cmp.dims:
            time_dim_var = "time"
        elif "TIME" in data_cmp.dims:
            time_dim_var = "TIME"
        else:
            st.info(f"Selected variable '{variable_cmp}' has no time dimension.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.stop()

        # Spatial dims
        if "lat" not in data_cmp.dims or "lon" not in data_cmp.dims:
            st.info(f"Selected variable '{variable_cmp}' has no lat/lon dimensions.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.stop()

        lat = ds["lat"].values
        lon = ds["lon"].values

        # Left map
        with col_left:
            st.markdown("**Time A map**")
            values_a = data_cmp.isel({time_dim_var: t1}).values
            vmax_a = np.nanmax(np.abs(values_a))
            fig_a = go.Figure(go.Contour(
                z=values_a, x=lon, y=lat,
                colorscale=palette,
                zmin=-vmax_a, zmax=vmax_a,
                contours=dict(coloring="heatmap", showlines=False),
                colorbar=dict(title=variable_cmp),
            ))
            fig_a.update_layout(
                xaxis_title="Longitude",
                yaxis_title="Latitude",
                height=450,
                template="plotly_dark"
            )
            st.plotly_chart(fig_a, use_container_width=True)

        # Right map
        with col_right:
            st.markdown("**Time B map**")
            values_b = data_cmp.isel({time_dim_var: t2}).values
            vmax_b = np.nanmax(np.abs(values_b))
            fig_b = go.Figure(go.Contour(
                z=values_b, x=lon, y=lat,
                colorscale=palette,
                zmin=-vmax_b, zmax=vmax_b,
                contours=dict(coloring="heatmap", showlines=False),
                colorbar=dict(title=variable_cmp),
            ))
            fig_b.update_layout(
                xaxis_title="Longitude",
                yaxis_title="Latitude",
                height=450,
                template="plotly_dark"
            )
            st.plotly_chart(fig_b, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)



elif st.session_state.page == "Story Mode":
    show_glass_placeholder("📖", "Story Mode", "Step through time animation coming soon.")
elif st.session_state.page == "Export":
    show_glass_placeholder("📤", "Export Data", "Download options will appear here.")

# -------------------------------------------------
# EXPLORE PAGE
# -------------------------------------------------
else:
    if uploaded_file is None:
        st.info("Upload a NetCDF file to start exploring climate data")
    else:
        try:
            # Dataset already loaded in sidebar if available
            if ds is None:
                st.error("Dataset could not be loaded.")
            else:
                st.success("Dataset loaded successfully")

                # Dataset info cards
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f'<div class="metric">📂 Dataset<br>{uploaded_file.name}</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric">📊 Variables<br>{len(ds.data_vars)}</div>', unsafe_allow_html=True)
                with col3:
                    if "time" in ds.dims:
                        try:
                            time_vals = pd.to_datetime(ds["time"].values, errors='coerce')
                            time_vals = time_vals[~pd.isna(time_vals)]
                            if len(time_vals) > 0:
                                cov = f"{time_vals[0].year}–{time_vals[-1].year}"
                            else:
                                cov = "N/A"
                        except Exception:
                            cov = "N/A"
                    else:
                        cov = "N/A"
                    st.markdown(f'<div class="metric">📅 Coverage<br>{cov}</div>', unsafe_allow_html=True)
                with col4:
                    st.markdown('<div class="metric">🌍 Resolution<br>auto</div>', unsafe_allow_html=True)

                # ---------------- Variable selection ----------------
                default_var_list = list(ds.data_vars)
                if not default_var_list:
                    st.error("No data variables found in the dataset.")
                else:
                    if variable_override and variable_override in ds.data_vars:
                        variable = variable_override
                    else:
                        variable = st.selectbox("Select Climate Variable", default_var_list, index=0)

                    data = ds[variable]
                    dims = data.dims

                    colA, colB = st.columns(2)

                    # ---------- SPATIAL MAP ----------
                    with colA:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader("Spatial Climate Heatmap")
                        if "lat" in dims and "lon" in dims:
                            lat = ds["lat"].values
                            lon = ds["lon"].values

                            if "time" in dims:
                                max_t = data.sizes["time"] - 1
                                t_idx = int(np.clip(time_index, 0, max_t))
                                values = data.isel(time=t_idx).values
                            elif "TIME" in dims:
                                max_t = data.sizes["TIME"] - 1
                                t_idx = int(np.clip(time_index, 0, max_t))
                                values = data.isel(TIME=t_idx).values
                            else:
                                values = data.values

                            # NEW: 3D globe figure for this slice
                            fig_globe = make_globe_figure(
                                lon=lon,
                                lat=lat,
                                values=values,
                                title="3D Climate Globe"
                            )

                            vmax = np.nanmax(np.abs(values))
                            fig = go.Figure(data=go.Contour(
                                z=values, x=lon, y=lat,
                                colorscale=palette,
                                zmin=-vmax, zmax=vmax,
                                contours=dict(coloring="heatmap", showlines=False),
                                colorbar=dict(title=variable),
                                hovertemplate="Lat: %{y:.2f}<br>Lon: %{x:.2f}<br>Value: %{z:.3f}<extra></extra>"
                            ))
                            fig.update_layout(xaxis_title="Longitude", yaxis_title="Latitude", height=450, template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)

                        else:
                            st.info("Selected variable has no lat/lon dimensions.")
                        st.markdown('</div>', unsafe_allow_html=True)

                    # ---------- TIME SERIES ----------
                    with colB:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader("Climate Time Series")
                        if "TIME" in dims or "time" in dims:
                            time_dim = "TIME" if "TIME" in dims else "time"
                            df_ts = data.to_dataframe().reset_index()
                            fig2 = px.line(df_ts, x=time_dim, y=variable, markers=True)
                            fig2.update_layout(template="plotly_dark", xaxis_title="Time", yaxis_title=variable, height=450)
                            st.plotly_chart(fig2, use_container_width=True)
                        else:
                            st.info("Selected variable has no time dimension.")
                        st.markdown('</div>', unsafe_allow_html=True)

                                        # ---------- 3D GLOBE VIEW ----------
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("3D Globe View")
                if "lat" in dims and "lon" in dims:
                    st.plotly_chart(fig_globe, use_container_width=True)
                else:
                    st.info("3D globe requires lat/lon dimensions.")
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error("Error reading dataset")
            st.write(e)