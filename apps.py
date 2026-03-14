import streamlit as st
import xarray as xr
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import tempfile

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="PyClimaExplorer",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM DASHBOARD GRAPHICS
# ---------------------------------------------------

st.markdown("""
<style>

.stApp {
background: radial-gradient(circle at top, #0f2027, #050607);
color:white;
font-family: 'Segoe UI';
}

.block-container{
padding-top:1rem;
}

h1{
color:#48e5c2;
font-weight:600;
}

h2,h3{
color:#d6f5ee;
}

.stButton>button {
background:rgba(255,255,255,0.08);
border-radius:12px;
border:1px solid rgba(255,255,255,0.15);
color:white;
}

[data-testid="stMetric"]{
background:rgba(255,255,255,0.05);
padding:10px;
border-radius:12px;
border:1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

st.title("🌍 PyClimaExplorer Climate Data Explorer")

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload NetCDF Dataset (.nc)",
    type=["nc"]
)

if uploaded_file is not None:

    try:

        # save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            path = tmp.name

        # ---------------------------------------------------
        # ROBUST DATASET LOADING
        # ---------------------------------------------------

        try:
            ds = xr.open_dataset(path)
        except ValueError:
            ds = xr.open_dataset(path, decode_times=False)

        st.success("Dataset loaded successfully")

        # ---------------------------------------------------
        # DATASET METADATA
        # ---------------------------------------------------

        st.subheader("Dataset Metadata")

        col1, col2 = st.columns(2)

        with col1:
            st.write("Dimensions")
            st.write(ds.dims)

        with col2:
            st.write("Coordinates")
            st.write(list(ds.coords))

        st.write("Available Variables")
        st.write(list(ds.data_vars))

        # ---------------------------------------------------
        # VARIABLE SELECTION
        # ---------------------------------------------------

        variable = st.selectbox(
            "Select Climate Variable",
            list(ds.data_vars)
        )

        data = ds[variable]
        dims = data.dims

        col_map, col_graph = st.columns(2)

        # ---------------------------------------------------
        # SPATIAL HEATMAP
        # ---------------------------------------------------

        if "lat" in dims and "lon" in dims:

            lat = ds["lat"].values
            lon = ds["lon"].values

            # FIX FOR 3D DATA (time, lat, lon)
            if "time" in dims:
                values = data.isel(time=0).values
            elif "TIME" in dims:
                values = data.isel(TIME=0).values
            else:
                values = data.values

            vmax = np.nanmax(np.abs(values))

            with col_map:

                st.subheader("Spatial Climate Heatmap")

                fig = go.Figure(
                    data=go.Contour(
                        z=values,
                        x=lon,
                        y=lat,
                        colorscale="RdBu_r",
                        zmin=-vmax,
                        zmax=vmax,
                        contours=dict(
                            coloring="heatmap",
                            showlines=False
                        ),
                        colorbar=dict(
                            title=variable
                        ),
                        hovertemplate=
                        "Lat: %{y:.2f}<br>"
                        "Lon: %{x:.2f}<br>"
                        "Value: %{z:.3f}<extra></extra>"
                    )
                )

                fig.update_layout(
                    xaxis_title="Longitude",
                    yaxis_title="Latitude",
                    height=650,
                    template="plotly_dark"
                )

                st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------
        # TIME SERIES
        # ---------------------------------------------------

        if "TIME" in dims or "time" in dims:

            time_dim = "TIME" if "TIME" in dims else "time"

            df = data.to_dataframe().reset_index()

            with col_graph:

                st.subheader("Climate Time Series")

                fig = px.line(
                    df,
                    x=time_dim,
                    y=variable,
                    markers=True
                )

                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title=variable,
                    height=650,
                    template="plotly_dark"
                )

                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:

        st.error("Error reading dataset")
        st.write(e)

else:

    st.info("Upload a NetCDF file to start exploring climate data")