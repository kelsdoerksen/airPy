"""
Test functions in utils
"""

from airpy import Utils
import json
import ee
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
import pandas as pd

# Defining some constants
config_file = 'test_config.json'

with open('{}'.format(config_file), 'r') as file:
    config_data = json.load(file)
utils = Utils(config_data)

test_array = np.array([[5, 5], [6, 6]])
true_ds = xr.Dataset(
        data_vars=dict(test=(["lat", "lon"], test_array)),
        coords=dict(
            lon=(["lon"], [0, 1]),
            lat=(["lat"], [2, 3])))

ee.Initialize()
cadence = config_data['dataset']['t_cadence']
month = config_data['query_month']
year = config_data['query_year']
collection = ee.ImageCollection(config_data['dataset']['collection']).\
    filterDate('{}-01-01'.format(year, '{}-01-01'.format(year + 1)))
# Select band type
data = collection.select(config_data['dataset']['band'])


def test_add_time_data():
    """Test function to add time component to xarray"""
    date_list = []
    start_date = datetime(config_data['query_year'], 1, 1)
    for i in range(365):
        d = start_date + timedelta(days=i)
        date_list.append(pd.Timestamp(d.strftime('%Y-%m-%d')))
    true_ds_with_time = true_ds.expand_dims(dim={'time': date_list}, axis=0)
    true_ds_with_time = true_ds_with_time.set_coords('time')
    true_ds_with_time = true_ds_with_time.transpose('lon', 'lat', 'time')
    assert utils.add_time_data(true_ds) == true_ds_with_time


def test_get_img_from_collect():
    """Test function to grab image from GEE collection"""
    ee.Initialize()
    assert utils.get_img_from_collect(data, cadence, month, year)


def test_get_buffer_extent():
    """Test function to get buffer extent from lat, lon point"""
    ee.Initialize()
    buffer = 500
    lat = 34
    lon = -118
    default_class = 17
    gee_img = utils.get_img_from_collect(data, cadence, month, year)
    assert utils.get_buffer_extent(lat, lon, buffer, default_class, gee_img)


def test_make_dataset():
    """Test function to make xarray dataset from array"""
    var = 'test'
    lats = [2, 3]
    lons = [0, 1]
    assert utils.make_dataset(test_array, var, lats, lons) == true_ds

def test_combine_data():
    """Test function to combine multiple xarrays"""
    arr1 = np.array([1,2])
    arr2 = np.array([3,4])
    da1 = xr.DataArray(arr1)
    da2 = xr.DataArray(arr2)
    ds_1 = da1.to_dataset(name='test1')
    ds_2 = da2.to_dataset(name='test2')
    results = [ds_1, ds_2]
    assert type(utils.combine_data(results)) is xr.core.dataset.Dataset

def test_save_collection():
    """
    Test function to save GEE collection results
    Save collection will return true if results are in format xarray dataset
    """
    # Need to update this, doesn't make sense, output of save_collection is a saved file
    assert utils.save_collection(true_ds) is True


def test_save_img():
    """
    Test function to save GEE image results
    If type is not xarray dataset, hdf save will fail
    """
    assert type(true_ds) is xr.core.dataset.Dataset