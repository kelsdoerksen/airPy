"""
Test run_airpy pipeline
"""

from airpy.run_airpy import *
import xarray as xr
import airpy.utils as utils
import json

config_file = 'test_config.json'

with open('{}'.format(config_file), 'r') as file:
    config_data = json.load(file)

ee.Initialize()

def test_getRequests():
    """Test function for generating list of points to query from GEE"""
    assert type(getRequests(config_data)) is list
    assert len(getRequests(config_data)) > 0

def test_getResult():
    """Test function to calculate GEE results"""
    # Don't thin this is working yet
    assert type(getResult(None, config_data)) is xr.core.dataset.Dataset