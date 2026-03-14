import numpy as np
import pandas as pd
import xarray as xr

# -----------------------------
# Define coordinates
# -----------------------------
lats = np.linspace(-90, 90, 37)        # 5-degree grid
lons = np.linspace(-180, 180, 73)      # 5-degree grid
times = pd.date_range("1980-01-01", periods=20, freq="YS")  # 20 yearly steps

# -----------------------------
# Create synthetic data
# -----------------------------
# Base temperature pattern: warmer at equator, colder at poles
lat2d, lon2d = np.meshgrid(lats, lons, indexing="ij")
base = 15.0 - 0.03 * np.abs(lat2d)  # degC

# Warming trend over time
trend = np.linspace(0, 2.0, len(times))  # +2°C over 20 years

data = np.zeros((len(times), len(lats), len(lons)), dtype="float32")
for t_idx, dt in enumerate(trend):
    noise = np.random.normal(scale=0.3, size=lat2d.shape)
    data[t_idx, :, :] = base + dt + noise

# -----------------------------
# Build xarray Dataset
# -----------------------------
ds_demo = xr.Dataset(
    {
        "tas": (("time", "lat", "lon"), data)
    },
    coords={
        "time": times,
        "lat": lats,
        "lon": lons,
    },
    attrs={"title": "Demo climate dataset: surface temperature"},
)

ds_demo["tas"].attrs["units"] = "degC"
ds_demo["tas"].attrs["long_name"] = "Near-surface air temperature"

# -----------------------------
# Write to NetCDF
# -----------------------------
out_path = "demo_climate_tas.nc"
ds_demo.to_netcdf(out_path)
print(f"Written {out_path}")
