"""
Test run_airpy pipeline
"""
from run_airpy import *
import xarray as xr
import json

config_file = 'test_config.json'

with open('../airpy/tests/{}'.format(config_file), 'r') as file:
    config_data = json.load(file)

ee.Initialize()

def test_getRequests():
    """Test function for generating list of points to query from GEE"""
    assert type(getRequests(config_data)) is list
    assert len(getRequests(config_data)) > 0

def test_getResult():
    """Test function to calculate GEE results"""
    items = getRequests(config_data)
    assert type(getResult(0, items[0])) is xr.core.dataset.Dataset