import streamlit as st
import numpy as np
import pandas as pd
import xarray as xr
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import base64
import geopandas as gpd

# -------------------------------------------------
# SHAPEFILE PATH
# -------------------------------------------------
NE_COUNTRIES_PATH = r"C:\Users\TUSHAR SRIVASTAVA\Desktop\Project\ne_110m_admin_0_countries.shp"

WORLD_GDF = gpd.read_file(NE_COUNTRIES_PATH)
WORLD_GDF = WORLD_GDF.to_crs("EPSG:4326")

# -------------------------------------------------
# 3D GLOBE FUNCTION
# -------------------------------------------------
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

    # Solid globe with realistic lighting
    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        surfacecolor=surfacecolor,
        colorscale="RdBu_r",
        cmin=0, cmax=1,
        showscale=True,
        colorbar=dict(title="Value"),
        opacity=1.0,  # solid globe

        lighting=dict(
            ambient=0.3,   # base light; higher = flatter
            diffuse=0.85,  # main shading
            specular=0.4,  # highlight strength
            roughness=0.4, # lower = sharper highlights
            fresnel=0.2,   # edge brightening
        ),
        lightposition=dict(
            x=200,  # "sun" position relative to globe
            y=0,
            z=100,
        ),
    ))

    # Country borders
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
                x=x_line, y=y_line, z=z_line,
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
            xaxis_backgroundcolor="rgba(0,0,0,0)",
            yaxis_backgroundcolor="rgba(0,0,0,0)",
            zaxis_backgroundcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        template="plotly_dark",
    )

    return fig


# -------------------------------------------------
# IMAGE LOAD
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
st.set_page_config(page_title="PyClimaExplorer", layout="wide")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Explore"
if "dataset_loaded" not in st.session_state:
    st.session_state.dataset_loaded = False

# -------------------------------------------------
# CSS
# -------------------------------------------------
st.markdown(f"""
<style>

/* ── APP BACKGROUND ── */
.stApp {{
    background:
        linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.85)),
        url("data:image/jpg;base64,{img}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: white;
    font-family: Segoe UI;
}}

/* ── CENTERED LANDING ── */
.landing-wrapper {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 65vh;
    text-align: center;
    padding-top: 60px;
}}
.landing-title {{
    font-size: 62px;
    font-weight: 700;
    color: #4fffd2;
    letter-spacing: 2px;
    margin-bottom: 12px;
    text-shadow: 0 0 40px rgba(79,255,210,0.35);
}}
.landing-sub {{
    font-size: 19px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 10px;
    letter-spacing: 0.5px;
}}
.landing-hint {{
    font-size: 14px;
    color: rgba(255,255,255,0.28);
    margin-top: 24px;
    animation: pulse 2.2s infinite;
}}
@keyframes pulse {{
    0%   {{ opacity: 0.25; }}
    50%  {{ opacity: 0.75; }}
    100% {{ opacity: 0.25; }}
}}

/* ── TOP NAVBAR BAR (title + buttons on same row) ── */
.topbar {{
    display: flex;
    align-items: center;
    gap: 0px;
    padding: 6px 0 10px 0;
    margin-bottom: 4px;
}}
.topbar-title {{
    font-size: 22px;
    font-weight: 700;
    color: #4fffd2;
    white-space: nowrap;
    margin-right: 18px;
    text-shadow: 0 0 20px rgba(79,255,210,0.25);
    flex-shrink: 0;
}}

/* ── NAV BUTTONS — evenly spaced across full width ── */
div[data-testid="stHorizontalBlock"] div[data-testid="column"] button {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: Segoe UI !important;
    width: 100% !important;
    padding: 10px 4px !important;
    font-size: 14px !important;
    letter-spacing: 0.3px;
}}
div[data-testid="stHorizontalBlock"] div[data-testid="column"] button:hover {{
    background: rgba(79,255,210,0.18) !important;
    border-color: #4fffd2 !important;
    color: #4fffd2 !important;
}}

/* ── VARIABLE TYPE BADGES ── */
.type-badge {{
    display: inline-block; font-size: 13px; font-weight: 600;
    padding: 3px 12px; border-radius: 20px; margin-bottom: 6px;
    letter-spacing: 0.5px; vertical-align: middle;
}}
.badge-temperature {{ background:rgba(255,100,80,0.18);  color:#ff7c6e; border:1px solid rgba(255,100,80,0.3);   }}
.badge-rainfall    {{ background:rgba(80,160,255,0.18);  color:#60b4ff; border:1px solid rgba(80,160,255,0.3);   }}
.badge-wind        {{ background:rgba(79,255,210,0.14);  color:#4fffd2; border:1px solid rgba(79,255,210,0.3);   }}
.badge-humidity    {{ background:rgba(180,120,255,0.18); color:#c89bff; border:1px solid rgba(180,120,255,0.3);  }}
.badge-general     {{ background:rgba(255,255,255,0.08); color:#ccc;    border:1px solid rgba(255,255,255,0.15); }}

/* ── VAR HEADER ── */
.var-header {{
    font-size: 22px; font-weight: 600; color: #4fffd2;
    margin: 24px 0 10px 0; padding: 10px 18px;
    border-left: 4px solid #4fffd2;
    background: rgba(79,255,210,0.06);
    border-radius: 0 10px 10px 0;
}}

/* ── SECTION DIVIDER ── */
.section-divider {{
    font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.55);
    margin: 28px 0 8px 0; padding: 6px 14px;
    border-left: 3px solid rgba(255,255,255,0.18);
    background: rgba(255,255,255,0.03);
    border-radius: 0 8px 8px 0;
    letter-spacing: 0.5px;
}}

/* ── CARDS ── */
.card {{
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
}}

/* ── METRIC CARDS ── */
.metric {{
    text-align: center;
    padding: 12px;
    border-radius: 12px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
}}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {{
    background: #0c1518;
}}

/* ── GLASS OVERLAY ── */
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
.glass-icon  {{ font-size: 58px; margin-bottom: 18px; }}
.glass-title {{ font-size: 26px; font-weight: 600; color: #4fffd2; margin-bottom: 10px; }}
.glass-sub   {{ font-size: 15px; color: rgba(255,255,255,0.5);
                max-width: 500px; margin: 0 auto 36px auto; line-height: 1.7; }}

/* ── HIDE STREAMLIT BRANDING ── */
#MainMenu {{ visibility: hidden; }}
footer     {{ visibility: hidden; }}

</style>
""", unsafe_allow_html=True)

# =================================================================
# VARIABLE CLASSIFIER
# =================================================================
TEMPERATURE_KEYS = ("temp","tas","t2m","tmax","tmin","tasmax","tasmin",
                    "air_temp","t_ref","2m_temperature")
RAINFALL_KEYS    = ("pr","precip","rain","prc","prcp","tp","precipitation")
WIND_KEYS        = ("uas","vas","u10","v10","wind","wnd","sfcwind",
                    "u_wind","v_wind","ws")
HUMIDITY_KEYS    = ("hurs","huss","rh","humid","q2m","specific_humidity",
                    "relative_humidity")
SNOW_KEYS        = ("snw","snd","snowfall","snow_depth","snc","snowcover","snow")

def classify_variable(name: str) -> str:
    n = name.lower().strip()
    if any(k in n for k in TEMPERATURE_KEYS): return "temperature"
    if any(k in n for k in RAINFALL_KEYS):    return "rainfall"
    if any(k in n for k in WIND_KEYS):        return "wind"
    if any(k in n for k in HUMIDITY_KEYS):    return "humidity"
    if any(k in n for k in SNOW_KEYS):        return "snow"
    return "general"

CATEGORY_META = {
    "temperature": ("🌡️","Temperature","badge-temperature"),
    "rainfall":    ("🌧️","Rainfall",   "badge-rainfall"),
    "wind":        ("💨","Wind",        "badge-wind"),
    "humidity":    ("💧","Humidity",    "badge-humidity"),
    "snow":        ("❄️","Snow",        "badge-general"),
    "general":     ("📊","General",     "badge-general"),
}

def auto_find(ds_vars, keys):
    for v in ds_vars:
        if any(k in v.lower() for k in keys):
            return v
    return None

# =================================================================
# CHART HELPERS
# =================================================================

def _spatial_mean(xr_da):
    if "lat" in xr_da.dims and "lon" in xr_da.dims:
        return xr_da.mean(dim=["lat","lon"])
    return xr_da


def render_heatmap(data, ds, variable, palette, time_index, card_key):
    dims = data.dims
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Spatial Climate Heatmap")
    if "lat" in dims and "lon" in dims:
        try:
            lat   = ds["lat"].values
            lon   = ds["lon"].values
            t_idx = int(np.clip(time_index, 0, data.sizes.get("time",0)-1))
            vals  = data.isel(time=t_idx).values if "time" in dims else data.values
            vmax  = np.nanmax(np.abs(vals))
            fig = go.Figure(data=go.Contour(
                z=vals, x=lon, y=lat, colorscale=palette,
                zmin=-vmax, zmax=vmax,
                contours=dict(coloring="heatmap", showlines=False),
                colorbar=dict(title=variable),
                hovertemplate="Lat: %{y:.2f}<br>Lon: %{x:.2f}<br>Value: %{z:.3f}<extra></extra>"
            ))
            fig.update_layout(xaxis_title="Longitude", yaxis_title="Latitude",
                              height=400, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True, key=f"heatmap_{card_key}")
        except Exception:
            st.info("Could not render heatmap for this variable.")
    else:
        st.info("No lat/lon dimensions found for this variable.")
    st.markdown('</div>', unsafe_allow_html=True)


def render_timeseries(data, variable, card_key):
    dims = data.dims
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Climate Time Series")
    time_dim = "time" if "time" in dims else ("TIME" if "TIME" in dims else None)
    if time_dim:
        try:
            df_ts = data.to_dataframe().reset_index()
            fig   = px.line(df_ts, x=time_dim, y=variable, markers=True)
            fig.update_layout(template="plotly_dark", xaxis_title="Time",
                              yaxis_title=variable, height=400)
            st.plotly_chart(fig, use_container_width=True, key=f"ts_{card_key}")
        except Exception:
            st.info("Could not render time series for this variable.")
    else:
        st.info("No time dimension found.")
    st.markdown('</div>', unsafe_allow_html=True)


def render_globe(data, ds, variable, time_index, card_key):
    dims = data.dims
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("3D Globe View")
    if "lat" in dims and "lon" in dims:
        try:
            lat   = ds["lat"].values
            lon   = ds["lon"].values
            t_idx = int(np.clip(time_index, 0, data.sizes.get("time", 0) - 1))
            vals  = data.isel(time=t_idx).values if "time" in dims else data.values
            fig_globe = make_globe_figure(lon=lon, lat=lat, values=vals,
                                          title=f"3D Globe — {variable}")
            st.plotly_chart(fig_globe, use_container_width=True, key=f"globe_{card_key}")
        except Exception as e:
            st.info(f"Could not render 3D globe: {e}")
    else:
        st.info("3D globe requires lat/lon dimensions.")
    st.markdown('</div>', unsafe_allow_html=True)


def render_distribution(data, variable, card_key):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Distribution Plot")
    try:
        vals = data.values.flatten()
        vals = vals[~np.isnan(vals)]
        if len(vals) > 0:
            fig = px.histogram(pd.DataFrame({"value": vals}), x="value",
                               nbins=40, template="plotly_dark")
            fig.update_layout(height=400, xaxis_title=variable)
            st.plotly_chart(fig, use_container_width=True, key=f"dist_{card_key}")
        else:
            st.info("No numerical data available.")
    except Exception:
        st.info("Distribution plot cannot be generated.")
    st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------
# INDEX PANELS
# ----------------------------------------------------------------

def render_temperature_indices(data, variable, card_key):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Temperature Indices")
    opt = st.selectbox(
        "Choose Temperature Metric",
        ["Baseline vs Current vs Future", "Monthly Seasonal Cycle", "Extreme Values"],
        key=f"temp_opt_{card_key}"
    )
    if "time" not in data.dims:
        st.info("No time dimension found.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    ts = _spatial_mean(data)
    df = ts.to_dataframe().reset_index()

    if opt == "Baseline vs Current vs Future":
        try:
            df["year"] = pd.to_datetime(df["time"], errors="coerce").dt.year
            yearly  = df.groupby("year")[variable].mean().reset_index().dropna()
            base    = yearly[yearly["year"] <= 2010]
            current = yearly[(yearly["year"] > 2010) & (yearly["year"] <= 2040)]
            future  = yearly[yearly["year"] > 2040]
            fig = go.Figure()
            if not base.empty:
                fig.add_trace(go.Scatter(x=base["year"], y=base[variable],
                    mode="lines+markers", name="Baseline", line=dict(color="#4fffd2")))
            if not current.empty:
                fig.add_trace(go.Scatter(x=current["year"], y=current[variable],
                    mode="lines+markers", name="Current",  line=dict(color="#ffa500")))
            if not future.empty:
                fig.add_trace(go.Scatter(x=future["year"], y=future[variable],
                    mode="lines+markers", name="Future",   line=dict(color="#ff4444")))
            if base.empty and current.empty and future.empty:
                st.info("No data spans the baseline/current/future split.")
            else:
                fig.update_layout(template="plotly_dark", height=400,
                                  xaxis_title="Year", yaxis_title=variable)
                st.plotly_chart(fig, use_container_width=True, key=f"bcf_{card_key}")
        except Exception:
            st.info("Cannot generate this chart.")

    elif opt == "Monthly Seasonal Cycle":
        try:
            df["month"] = pd.to_datetime(df["time"], errors="coerce").dt.month
            monthly = df.groupby("month")[variable].mean().reset_index()
            fig = px.line(monthly, x="month", y=variable, markers=True,
                          template="plotly_dark")
            fig.update_layout(height=400, xaxis_title="Month", yaxis_title=variable)
            st.plotly_chart(fig, use_container_width=True, key=f"seasonal_{card_key}")
        except Exception:
            st.info("Cannot generate this chart.")

    elif opt == "Extreme Values":
        try:
            df["date"] = pd.to_datetime(df["time"], errors="coerce")
            df = df.dropna(subset=[variable])
            if not df.empty:
                hot  = df.loc[df[variable].idxmax()]
                cold = df.loc[df[variable].idxmin()]
                st.write(f"🌡️ **Hottest day observed:** {hot['date'].date()} ({hot[variable]:.2f})")
                st.write(f"❄️ **Coldest day observed:** {cold['date'].date()} ({cold[variable]:.2f})")
                st.write(f"☀️ **Hot days count (>30°C):** {int((df[variable]>30).sum())}")
                st.write(f"🌙 **Tropical nights count (>20°C):** {int((df[variable]>20).sum())}")
            else:
                st.info("No valid data found.")
        except Exception:
            st.info("Cannot compute extreme values.")

    st.markdown('</div>', unsafe_allow_html=True)


def render_rainfall_indices(data, variable, card_key):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Rainfall & Hydrology Indices")
    opt = st.selectbox(
        "Choose Rainfall Metric",
        ["Annual Rainfall Total", "Monthly Distribution",
         "Heavy Rainfall Days", "Drought Frequency", "Snowfall Days/Amounts"],
        key=f"rain_opt_{card_key}"
    )
    if "time" not in data.dims and opt != "Snowfall Days/Amounts":
        st.info("No time dimension found.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    ts = _spatial_mean(data)
    df = ts.to_dataframe().reset_index()

    if opt == "Annual Rainfall Total":
        try:
            df["year"] = pd.to_datetime(df["time"], errors="coerce").dt.year
            yearly = df.groupby("year")[variable].sum().reset_index()
            fig = px.bar(yearly, x="year", y=variable, template="plotly_dark")
            fig.update_layout(height=400, xaxis_title="Year",
                              yaxis_title=f"Total {variable}")
            st.plotly_chart(fig, use_container_width=True, key=f"ann_{card_key}")
        except Exception:
            st.info("Cannot generate Annual Rainfall Total chart.")

    elif opt == "Monthly Distribution":
        try:
            df["month"] = pd.to_datetime(df["time"], errors="coerce").dt.month
            monthly = df.groupby("month")[variable].sum().reset_index()
            fig = px.bar(monthly, x="month", y=variable, template="plotly_dark")
            fig.update_layout(height=400, xaxis_title="Month",
                              yaxis_title=f"Total {variable}")
            st.plotly_chart(fig, use_container_width=True, key=f"mondist_{card_key}")
        except Exception:
            st.info("Cannot generate Monthly Distribution chart.")

    elif opt == "Heavy Rainfall Days":
        threshold = st.number_input("Threshold (mm/day)", min_value=1.0, value=20.0,
                                    key=f"thresh_{card_key}")
        try:
            heavy = int((df[variable] > threshold).sum())
            st.write(f"🌧️ **Heavy rainfall days (> {threshold} mm/day):** {heavy}")
        except Exception:
            st.info("Cannot compute heavy rainfall days.")

    elif opt == "Drought Frequency":
        try:
            df = df.dropna(subset=[variable])
            dry    = (df[variable] < 1).astype(int)
            groups = (dry != dry.shift()).cumsum()
            consec = dry.groupby(groups).sum()
            st.write(f"🏜️ **Longest drought (consecutive dry days):** {int(consec.max())}")
        except Exception:
            st.info("Cannot compute drought frequency.")

    elif opt == "Snowfall Days/Amounts":
        try:
            snow_days   = int((df[variable] > 0).sum())
            snow_amount = float(df[variable].sum())
            st.write(f"❄️ **Snowfall days:** {snow_days}")
            st.write(f"❄️ **Total snowfall amount:** {snow_amount:.2f}")
        except Exception:
            st.info("Cannot compute snowfall data.")

    st.markdown('</div>', unsafe_allow_html=True)


def render_wind_indices(ds, u_var, v_var, fallback_data, fallback_var, card_key):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Atmospheric & Wind Indices")
    opt = st.selectbox(
        "Choose Atmospheric Metric",
        ["Wind Speed Distribution", "Storm Frequency/Intensity", "Humidity Extremes"],
        key=f"wind_opt_{card_key}"
    )
    has_uv = (u_var is not None and v_var is not None)

    if opt == "Wind Speed Distribution":
        if has_uv:
            try:
                u_vals = ds[u_var].values.flatten()
                v_vals = ds[v_var].values.flatten()
                spd    = np.sqrt(u_vals**2 + v_vals**2)
                spd    = spd[~np.isnan(spd)]
                mean_u = float(np.nanmean(u_vals))
                mean_v = float(np.nanmean(v_vals))
                deg    = float(np.degrees(np.arctan2(mean_u, mean_v)) % 360)
                dirs   = ["N","NE","E","SE","S","SW","W","NW"]
                dlbl   = dirs[int((deg+22.5)/45) % 8]
                st.caption(f"ℹ️ Using wind components: **`{u_var}`** + **`{v_var}`**")
                st.write(f"💨 **Average wind speed:** {float(np.mean(spd)):.2f} m/s")
                st.write(f"💨 **Max wind speed:** {float(np.max(spd)):.2f} m/s")
                st.write(f"🧭 **Prevailing direction:** {dlbl} ({deg:.1f}°)")
                fig = px.histogram(pd.DataFrame({"Wind Speed (m/s)": spd}),
                                   x="Wind Speed (m/s)", nbins=40, template="plotly_dark")
                fig.update_layout(height=320, yaxis_title="Frequency")
                st.plotly_chart(fig, use_container_width=True, key=f"wdist_{card_key}")
            except Exception:
                st.info("Cannot compute wind speed distribution.")
        elif fallback_data is not None:
            try:
                vals = fallback_data.values.flatten()
                vals = vals[~np.isnan(vals)]
                st.write(f"💨 **Average {fallback_var}:** {float(np.mean(vals)):.2f} m/s")
                st.write(f"💨 **Max {fallback_var}:** {float(np.max(vals)):.2f} m/s")
                fig = px.histogram(pd.DataFrame({fallback_var: vals}),
                                   x=fallback_var, nbins=40, template="plotly_dark")
                fig.update_layout(height=320, xaxis_title=fallback_var,
                                  yaxis_title="Frequency")
                st.plotly_chart(fig, use_container_width=True, key=f"wdist_fb_{card_key}")
            except Exception:
                st.info("Cannot compute wind distribution.")
        else:
            st.info("Wind data (uas/vas or u10/v10) not available in this dataset.")

    elif opt == "Storm Frequency/Intensity":
        if has_uv:
            try:
                u_vals = ds[u_var].values.flatten()
                v_vals = ds[v_var].values.flatten()
                spd    = np.sqrt(u_vals**2 + v_vals**2)
                spd    = spd[~np.isnan(spd)]
                st.caption(f"ℹ️ Using wind components: **`{u_var}`** + **`{v_var}`**")
                st.write(f"⛈️ **Storm days (wind > 20 m/s):** {int((spd>20).sum())}")
                st.write(f"🌪️ **Severe storm days (wind > 32 m/s):** {int((spd>32).sum())}")
                st.write(f"📊 **Max recorded wind speed:** {float(np.max(spd)):.2f} m/s")
            except Exception:
                st.info("Cannot compute storm frequency/intensity.")
        else:
            st.info("Storm analysis requires both u-component and v-component wind variables.")

    elif opt == "Humidity Extremes":
        st.info("Select a humidity variable (e.g. `hurs`) for this metric, "
                "or switch to Humidity Extremes from the Humidity section below.")

    st.markdown('</div>', unsafe_allow_html=True)


def render_humidity_indices(data, variable, card_key):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Humidity Extremes")
    try:
        h = data.values.flatten()
        h = h[~np.isnan(h)]
        st.write(f"💧 **Average humidity:** {float(np.nanmean(h)):.2f}%")
        st.write(f"💧 **Max humidity:** {float(np.nanmax(h)):.2f}%")
        st.write(f"🌵 **Min humidity:** {float(np.nanmin(h)):.2f}%")
        fig = px.histogram(pd.DataFrame({"Relative Humidity (%)": h}),
                           x="Relative Humidity (%)", nbins=40, template="plotly_dark")
        fig.update_layout(height=320, yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True, key=f"hum_{card_key}")
    except Exception:
        st.info("Cannot compute humidity extremes.")
    st.markdown('</div>', unsafe_allow_html=True)


def section_label(text):
    st.markdown(f'<div class="section-divider">{text}</div>', unsafe_allow_html=True)


def show_glass_placeholder(icon, title, subtitle):
    st.markdown(f"""
        <div class="glass-overlay">
            <div class="glass-icon">{icon}</div>
            <div class="glass-title">{title}</div>
            <div class="glass-sub">{subtitle}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    back_col = st.columns([2.5, 1, 2.5])
    with back_col[1]:
        if st.button("← Back to Explore", key=f"back_{title}"):
            st.session_state.page = "Explore"
            st.rerun()

# =================================================================
# SIDEBAR
# =================================================================
with st.sidebar:
    st.markdown("### 🌍 PyClimaExplorer")
    st.markdown("---")
    st.title("Controls")

    with st.expander("📂 Dataset", expanded=True):
        uploaded_file = st.file_uploader(
            "Upload NetCDF (.nc)", type=["nc"],
            key=f"nc_uploader_{st.session_state.get('_file_uploader_key', 0)}"
        )

    if uploaded_file is not None:
        st.session_state.dataset_loaded = True
    else:
        st.session_state.dataset_loaded = False

    if st.session_state.dataset_loaded:
        with st.expander("🌡 Variable Selection"):
            variable_override = st.text_input("Preferred variable name (optional)", value="")
        with st.expander("⏱ Time Controls"):
            time_index = st.number_input("Time index (for 3D data)",
                                         min_value=0, value=0, step=1)
        with st.expander("🎨 Color Settings"):
            palette = st.selectbox("Color Palette",
                                   ["RdBu_r", "Turbo", "Viridis", "Plasma", "RdBu"])
    else:
        variable_override = ""
        time_index        = 0
        palette           = "RdBu_r"

    ds = None
    if uploaded_file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                path = tmp.name
            try:
                ds = xr.open_dataset(path)
            except ValueError:
                try:
                    ds = xr.open_dataset(path, decode_times=False, engine="netcdf4")
                except Exception:
                    try:
                        ds = xr.open_dataset(path, decode_times=False, engine="h5netcdf")
                    except Exception:
                        st.error("Error reading dataset — unsupported format or corrupted file.")
                        ds = None
        except Exception:
            st.error("Error reading dataset")
            ds = None

        if ds is not None:
            with st.expander("📊 Dataset Metadata", expanded=True):
                st.write("Dimensions:",  ds.dims)
                st.write("Coordinates:", list(ds.coords))
                st.write("Variables:",   list(ds.data_vars))

# =================================================================
# LANDING PAGE — no dataset uploaded yet
# =================================================================
if not st.session_state.dataset_loaded:
    st.markdown("""
    <div class="landing-wrapper">
        <div class="landing-title">🌍 PyClimaExplorer</div>
        <div class="landing-sub">
            Interactive climate data visualization — no coding required
        </div>
        <div class="landing-hint">← Upload a NetCDF (.nc) file from the sidebar to begin</div>
    </div>
    """, unsafe_allow_html=True)

# =================================================================
# FULL DASHBOARD — dataset is loaded
# =================================================================
else:

    # ── TOP BAR: title inline with nav buttons ──
    # Title rendered as HTML floated left, then buttons fill the rest
    st.markdown(
        '<div style="font-size:26px; font-weight:700; color:#4fffd2; '
        'letter-spacing:1px; text-align:center; '
        'padding:10px 0 6px 0; margin-bottom:4px; '
        'text-shadow:0 0 20px rgba(79,255,210,0.25);">'
        '🌍 PyClimaExplorer</div>',
        unsafe_allow_html=True
    )

    # ── NAVBAR: 5 equal columns spanning full width, no gaps ──
    nav_cols = st.columns([1, 1, 1, 1, 1])

    with nav_cols[0]:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.dataset_loaded = False
            st.session_state.page = "Explore"
            st.session_state["_file_uploader_key"] = st.session_state.get(
                "_file_uploader_key", 0) + 1
            st.rerun()

    with nav_cols[1]:
        if st.button("Explore", use_container_width=True):
            st.session_state.page = "Explore"
            st.rerun()

    with nav_cols[2]:
        if st.button("Compare Years", use_container_width=True):
            st.session_state.page = "Compare Years"
            st.rerun()

    with nav_cols[3]:
        if st.button("Story Mode", use_container_width=True):
            st.session_state.page = "Story Mode"
            st.rerun()

    with nav_cols[4]:
        if st.button("Export", use_container_width=True):
            st.session_state.page = "Export"
            st.rerun()

    st.markdown("---")

    # ── NON-EXPLORE PAGES ──
    if st.session_state.page == "Compare Years":
        show_glass_placeholder("📅", "Compare Years",
                               "Year-over-year comparison coming soon.")

    elif st.session_state.page == "Story Mode":
        show_glass_placeholder("📖", "Story Mode",
                               "Step through time animation coming soon.")

    elif st.session_state.page == "Export":
        show_glass_placeholder("📤", "Export Data",
                               "Download options will appear here.")

    # ================================================================
    # EXPLORE PAGE
    # ================================================================
    else:
        if ds is None:
            st.error("Dataset could not be loaded.")
        else:
            st.success("Dataset loaded successfully")
            all_vars = list(ds.data_vars)

            if variable_override and variable_override in ds.data_vars:
                variable = variable_override
            else:
                variable = st.selectbox("Select Climate Variable", all_vars, index=0)

            data     = ds[variable]
            dims     = data.dims
            var_type = classify_variable(variable)
            icon, label, badge_cls = CATEGORY_META[var_type]

            u_var         = auto_find(all_vars, ("uas","u10","u_wind"))
            v_var         = auto_find(all_vars, ("vas","v10","v_wind"))
            hum_var       = auto_find(all_vars, HUMIDITY_KEYS)
            rain_var_auto = auto_find(all_vars, RAINFALL_KEYS)

            st.markdown(
                f'<div class="var-header">'
                f'{icon} Variable: <code>{variable}</code>&nbsp;&nbsp;'
                f'<span class="type-badge {badge_cls}">{label}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            # ── ROW 1 — Heatmap + Time Series ──
            section_label("📍 Spatial Pattern & Temporal Trend")
            col1, col2 = st.columns([1, 1])
            with col1:
                render_heatmap(data, ds, variable, palette, time_index, "row1_l")
            with col2:
                render_timeseries(data, variable, "row1_r")

            # ── ROW 2 — 3D Globe (full width) ──
            section_label("🌐 3D Interactive Globe")
            render_globe(data, ds, variable, time_index, "row2_globe")

            # ── ROW 3 — Climate Indices ──
            section_label("📊 Climate Indices")
            col3, col4 = st.columns([1, 1])

            if var_type in ("temperature", "general", "snow"):
                with col3:
                    render_temperature_indices(data, variable, "row3_l")
                with col4:
                    rain_target = rain_var_auto if rain_var_auto else variable
                    rain_data   = ds[rain_target]
                    if rain_target != variable:
                        st.markdown(
                            f'<p style="color:rgba(255,255,255,0.4); font-size:13px;'
                            f' margin:0 0 6px 4px;">ℹ️ Rainfall section using '
                            f'auto-detected variable: <code>{rain_target}</code></p>',
                            unsafe_allow_html=True
                        )
                    render_rainfall_indices(rain_data, rain_target, "row3_r")

            elif var_type == "rainfall":
                with col3:
                    render_rainfall_indices(data, variable, "row3_l")
                with col4:
                    render_temperature_indices(data, variable, "row3_r")

            elif var_type == "wind":
                with col3:
                    render_wind_indices(ds, u_var, v_var,
                                        fallback_data=data, fallback_var=variable,
                                        card_key="row3_l")
                with col4:
                    render_temperature_indices(data, variable, "row3_r")

            elif var_type == "humidity":
                with col3:
                    render_humidity_indices(data, variable, "row3_l")
                with col4:
                    render_wind_indices(ds, u_var, v_var,
                                        fallback_data=None, fallback_var=None,
                                        card_key="row3_r")

            # ── ROW 4 — Distribution + Atmospheric Overview ──
            section_label("📈 Distribution & Atmospheric Overview")
            col5, col6 = st.columns([1, 1])
            with col5:
                render_distribution(data, variable, "row4_l")
            with col6:
                fallback      = data if var_type == "wind" else None
                fallback_name = variable if var_type == "wind" else None
                render_wind_indices(ds, u_var, v_var,
                                    fallback_data=fallback, fallback_var=fallback_name,
                                    card_key="row4_r")