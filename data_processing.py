import numpy as np

def select_variable(ds, variable):
    """Select climate variable"""
    return ds[variable]


def get_time_range(ds):
    """Return time values"""
    if "time" in ds.coords:
        return ds["time"].values
    return None


def extract_spatial_slice(data, time_index):
    """Get spatial slice for heatmap"""
    if "time" in data.dims:
        return data.isel(time=time_index)
    return data