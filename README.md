# 🌍 PyClimaExplorer

> **Interactive climate data visualisation platform where no coding is required.**
> Upload any NetCDF file and instantly explore spatial patterns, temporal trends, 3D globe views, climate indices all in a stunning deep-space UI.

<br>

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00e5c8?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

---

## Preview

| Explore Page | 3D Globe | Climate Indices |
|---|---|---|
| Spatial heatmaps + temporal time series rendered side-by-side | Interactive 3D globe with country borders overlaid on climate data | Temperature, hydrology, wind & humidity indices with smart auto-detection |

---

## Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [How to Use](#-how-to-use)
- [Pages & Modules](#-pages--modules)
- [Variable Auto-Detection](#-variable-auto-detection)
- [Supported Data Formats](#-supported-data-formats)
- [Configuration](#-configuration)
- [Known Limitations](#-known-limitations)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)

---

## About the Project

Climate science data is powerful but it is locked behind complex tooling, steep learning curves, and code-heavy workflows that exclude researchers, policymakers, and students who aren't programmers.

**PyClimaExplorer** solves this by turning raw NetCDF climate files into a fully interactive, browser-based visual dashboard. Upload a `.nc` file, and within seconds you have access to:

- Side-by-side spatial heatmaps and time series charts
- A rotatable 3D globe with real country boundary overlays
- Smart climate index calculations (heat extremes, drought frequency, wind speed distribution, and more)
- A guided story mode that walks through a dataset's timeline
- One-click CSV export of any variable

It was built for climate researchers, environmental scientists, educators, and anyone who wants to understand what's in their climate data — fast.

---

## Key Features

### Spatial Visualisation
Render 2D contour heatmaps of any lat/lon variable at any time slice. Supports multiple colour palettes (RdBu_r, Turbo, Viridis, Plasma, RdBu).

### Temporal Time Series
Automatically detect and plot the time dimension of any variable with an area-fill trend overlay.

### Interactive 3D Globe
Project climate data onto a photorealistic 3D sphere using Plotly's Surface trace, with country boundary lines rendered from a Natural Earth shapefile. Fully rotatable and zoomable in-browser.

### Smart Climate Indices
Auto-detect the variable type (temperature, rainfall, wind, humidity, snow, general) and render contextually relevant indices:

| Variable Type | Available Indices |
|---|---|
| **Temperature** | Baseline vs Current vs Future · Monthly Seasonal Cycle · Extreme Values (hottest/coldest days, tropical nights) |
| **Rainfall / Hydrology** | Annual Totals · Monthly Distribution · Heavy Rainfall Days · Drought Frequency · Snowfall Days & Amounts |
| **Wind / Atmospheric** | Wind Speed Distribution · Storm Frequency & Intensity · Prevailing Direction |
| **Humidity** | Average / Max / Min · Distribution Histogram |

### Story Mode
A guided 3-step narrative explorer that walks through baseline, mid-period, and recent time slices — with a draggable timeline slider and progress indicator.

### Compare Mode
Select any two time indices and view them side-by-side on identical spatial maps for direct visual comparison.

### Export
Preview the first 50 rows of any variable and download the full dataset as a CSV with one click.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend / App** | [Streamlit](https://streamlit.io) | Web app framework |
| **Visualisation** | [Plotly](https://plotly.com/python/) | Interactive 2D charts & 3D globe |
| **Climate Data** | [xarray](https://xarray.pydata.org/) | NetCDF reading & multidimensional array handling |
| **Geospatial** | [GeoPandas](https://geopandas.org/) | Country boundary shapefile parsing |
| **Data Processing** | [NumPy](https://numpy.org/) · [Pandas](https://pandas.pydata.org/) | Array math & time series operations |
| **Styling** | Custom CSS (Deep Space / Bioluminescent theme) | UI/UX — dark theme, teal accent system |
| **Background FX** | CSS keyframe animations | Animated background image drift + hue-rotate |

---

## Project Structure

```
PyClimaExplorer/
│
├── ULTIMATE.py                                      
├── photo.jpg                                   
├── requirements.txt                            
├── README.md                                   
├── ne_110m_admin_0_countries.shp               
├── ne_110m_admin_0_countries.dbf               
├── ne_110m_admin_0_countries.prj
├── ne_110m_admin_0_countries.cpg              
└── ne_110m_admin_0_countries.shx                                  
```
---

## Installation & Setup

### Prerequisites

- Python 3.9 or higher
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/PyClimaExplorer.git
cd PyClimaExplorer
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the Natural Earth Shapefile

Download the **Admin 0 – Countries** shapefile (1:110m scale) from [Natural Earth](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/):

```
https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip
```

Extract all files (`.shp`, `.dbf`, `.prj`, `.shx`) into your project directory.

### 5. Update the Shapefile Path

Open `app.py` and update line 15 to point to your shapefile location:

```python
# Change this:
NE_COUNTRIES_PATH = r"C:\Users\HARMANMEET\OneDrive\Desktop\project\ne_110m_admin_0_countries.shp"

# To your path, for example:
NE_COUNTRIES_PATH = r"./ne_110m_admin_0_countries.shp"
# or on Linux/macOS:
NE_COUNTRIES_PATH = "/home/user/project/ne_110m_admin_0_countries.shp"
```

### 6. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## How to Use

```
1. Launch the app  ──►  2. Upload a .nc file  ──►  3. Select a variable  ──►  4. Explore
```

1. **Open the app** — the landing page greets you with an upload prompt
2. **Upload a NetCDF file** — drag and drop or click "Browse files" in the sidebar
3. **Automatic detection** — the variable type (temperature, rainfall, wind, etc.) is detected instantly
4. **Navigate** — use the top navigation bar to switch between Explore, Compare, Story, and Export pages
5. **Explore** — scroll through spatial heatmaps, time series, 3D globe, climate indices, and distribution plots
6. **Compare** — select two time slices and view them side-by-side
7. **Story Mode** — follow the guided 3-step narrative through baseline → current → recent data
8. **Export** — download any variable as CSV

---

## Pages & Modules

### Explore (Default)
The main dashboard. Renders four row sections:

| Section | Content |
|---|---|
| **Spatial Pattern & Temporal Trend** | Side-by-side heatmap + time series |
| **3D Interactive Globe** | Rotatable 3D sphere with country borders |
| **Climate Indices** | Context-aware index panels (2 columns, auto-selected by variable type) |
| **Distribution & Atmospheric Overview** | Histogram distribution + wind/atmospheric panel |

### Compare
Select two time indices with dual sliders and compare spatial maps side-by-side. Includes auto-detected time and lat/lon dimension handling.

### Story Mode
A guided 3-step explorer with:
- Draggable timeline slider
- 3-segment progress indicator
- Paired 2D heatmap + 3D globe view at the selected time

### Export
Tabular preview (first 50 rows) of any variable with one-click CSV download.

---

## Variable Auto-Detection

PyClimaExplorer automatically classifies uploaded variables using keyword matching against common CF Convention and CMIP naming standards:

```python
TEMPERATURE_KEYS = ("temp", "tas", "t2m", "tmax", "tmin", "tasmax", "tasmin", ...)
RAINFALL_KEYS    = ("pr", "precip", "rain", "prc", "prcp", "tp", ...)
WIND_KEYS        = ("uas", "vas", "u10", "v10", "wind", "sfcwind", ...)
HUMIDITY_KEYS    = ("hurs", "huss", "rh", "humid", "q2m", ...)
SNOW_KEYS        = ("snw", "snd", "snowfall", "snow_depth", ...)
```

The detected type determines which index panels are shown in Rows 3 and 4. If detection fails, the app falls back to `"general"` which renders temperature and rainfall indices by default.

You can override detection manually using the **Variable Selection** expander in the sidebar.

---

## Supported Data Formats

| Format | Support |
|---|---|
| NetCDF-4 (`.nc`) | Full support |
| NetCDF-3 Classic | Auto-fallback via `engine="netcdf4"` |
| HDF5-backed NetCDF | Auto-fallback via `engine="h5netcdf"` |
| Non-decodable time axes | Handled via `decode_times=False` |


---

```python
# Path to Natural Earth shapefile
NE_COUNTRIES_PATH = r"path/to/ne_110m_admin_0_countries.shp"

# Background photo (place photo.jpg next to app.py)
_bg_img = _get_img_b64(os.path.join(_script_dir, "photo.jpg"))
```

Sidebar controls (available after upload):

| Control | Description |
|---|---|
| **Variable Selection** | Override the auto-detected variable name |
| **Time Index** | Choose the time slice for 3D and heatmap views |
| **Color Palette** | RdBu_r · Turbo · Viridis · Plasma · RdBu |

---

---

## Roadmap

- [ ] **Animated time-lapse** — GIF/MP4 export of variable evolution across all time steps
- [ ] **Multi-variable overlay** — plot two variables on the same spatial map with dual colour axes
- [ ] **Anomaly detection** — automatic flagging of statistically significant events in time series
- [ ] **Region selection** — click-to-define bounding box for regional analysis
- [ ] **Multi-file comparison** — compare the same variable across two different model runs or scenarios

---


## Requirements

```txt
streamlit>=1.30.0
numpy>=1.24.0
pandas>=2.0.0
xarray>=2023.1.0
plotly>=5.14.0
geopandas>=0.13.0
netcdf4>=1.6.0
h5netcdf>=1.1.0
scipy>=1.10.0
```

Install all at once:

```bash
pip install streamlit numpy pandas xarray plotly geopandas netcdf4 h5netcdf scipy
```

---


## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- [Natural Earth](https://www.naturalearthdata.com/) — country boundary shapefiles
- [Streamlit](https://streamlit.io/) — the app framework that makes this possible
- [Plotly](https://plotly.com/) — 3D globe and interactive chart rendering
- [xarray](https://xarray.pydata.org/) — the backbone of NetCDF data handling in Python
- [CF Conventions](https://cfconventions.org/) — standard naming for climate variables

---

<div align="center">

**Built with 🌊 for the climate science community**

*If PyClimaExplorer helped your research or project, please consider giving it a ⭐*

</div>
