import xarray as xr

def load_dataset(file):
    """Load NetCDF dataset using Xarray"""
    ds = xr.open_dataset(file)
    return ds


def get_variables(ds):
    """Return list of climate variables"""
    return list(ds.data_vars)


def get_metadata(ds):
    """Return dataset metadata"""
    return {
        "dimensions": ds.dims,
        "coordinates": list(ds.coords),
        "variables": list(ds.data_vars)
    }