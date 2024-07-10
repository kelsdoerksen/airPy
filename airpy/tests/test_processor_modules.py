"""
Test functions in processor_modules
"""
from processor_modules import ProcessorModules
from utils import Utils
import xarray as xr
import ee
from functools import reduce
from gee_class_constants import MODIS_LC_Type1, FIRE_LC, GHSL_Built_Class


class TestProcessorModules():
    def setup_method(self):
        # common variables amongst tests
        self.point = {'coordinates': [-118.125, 34.205]}
        self.month = 'jan'
        self.year = 2015
        self.buffer_size = 55500
        self.utils = Utils()
        self.dims = ['lat', 'lon']
        ee.Initialize()

    def test_process_collection_for_img(self):
        """Test function for processing gee collection and saving as image"""
        # output of process collection for img should be dictionary with lat, lon, and numpy array
        collection = 'MODIS/006/MCD12Q1'
        dataset_name = 'modis'
        band = 'LC_Type1'
        cadence = 'yearly'
        resolution = '500'

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, resolution, self.buffer_size, self.utils)

    def test_process_modis(self):
        """
        Test function for processing modis land cover collection
        Output of process_modis should be xarray dataset with
        20 variables and lat, lon dimensions

        """
        # output of process fire should be xarray dataset with X variables and lat, lon dims
        band = 'LC_Type1'
        dataset_name = 'modis'
        collection = 'MODIS/006/MCD12Q1'
        cadence = 'yearly'
        resolution = '500'

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, resolution, self.buffer_size, self.utils)

        prefix = '{}.{}.'.format(dataset_name, band)
        stats_vars = ['mode', 'var']
        class_vars = []
        for k, v in MODIS_LC_Type1.items():
            class_vars.append(MODIS_LC_Type1[k]['class'])

        stats_vars.extend(class_vars)
        combined_vars = stats_vars
        true_ds_vars = reduce(lambda res, item: res + [prefix + item], combined_vars, [])
        assert type(processor_modules.process_modis()) is xr.core.dataset.Dataset
        assert sorted([i for i in processor_modules.process_modis().data_vars]) == sorted(true_ds_vars)
        assert sorted([i for i in processor_modules.process_modis().coords]) == sorted(self.dims)

    def test_process_fire(self):
        """
        Test function for processing fire collection
        Output of process_fire should be xarray dataset with
        18 variables and lat, lon dimensions
        """
        band = 'LandCover'
        dataset_name = 'fire'
        collection = 'ESA/CCI/FireCCI/5_1'
        cadence = 'monthly'
        resolution = '250'

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, resolution, self.buffer_size, self.utils)

        prefix = '{}.{}.'.format(dataset_name, band)
        stats_vars = ['mode', 'var', 'burnt']
        class_vars = []
        for k, v in FIRE_LC.items():
            class_vars.append(FIRE_LC[k]['class'])

        stats_vars.extend(class_vars)
        combined_vars = stats_vars
        true_ds_vars = reduce(lambda res, item: res + [prefix + item], combined_vars, [])
        assert type(processor_modules.process_fire()) is xr.core.dataset.Dataset
        assert sorted([i for i in processor_modules.process_fire().data_vars]) == sorted(true_ds_vars)
        assert sorted([i for i in processor_modules.process_fire().coords]) == sorted(self.dims)

    def test_process_pop(self):
        """Test function for processing population collection
        Output of process_pop should be xarray dataset with
        5 variables and lat, lon dimensions
        """
        band = 'population_density'
        dataset_name = 'pop'
        collection = 'CIESIN/GPWv411/GPW_Population_Density'
        cadence = 'yearly'
        resolution = '927.67'

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, resolution, self.buffer_size, self.utils)
        prefix = '{}.{}.'.format(dataset_name, band)
        true_ds_vars = ['var', 'max', 'min', 'mean']
        true_ds_vars = reduce(lambda res, item: res + [prefix + item], true_ds_vars, [])

        assert type(processor_modules.process_pop()) is xr.core.dataset.Dataset
        assert sorted([i for i in processor_modules.process_pop().data_vars]) == sorted(true_ds_vars)
        assert sorted([i for i in processor_modules.process_pop().coords]) == sorted(self.dims)

    def test_process_nightlight(self):
        """Test function for processing nightlight collection
        Output of process_nightlight should be xarray dataset with
        5 variables and lat, lon dimensions
        """
        band = 'avg_rad'
        dataset_name = 'nightlight'
        collection = 'NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG'
        cadence = 'monthly'
        resolution = '463.83'

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, resolution, self.buffer_size, self.utils)
        prefix = '{}.{}.'.format(dataset_name, band)
        true_ds_vars = ['var', 'mean', 'max', 'min']
        true_ds_vars = reduce(lambda res, item: res + [prefix + item], true_ds_vars, [])

        assert type(processor_modules.process_nightlight()) is xr.core.dataset.Dataset
        assert sorted([i for i in processor_modules.process_nightlight().data_vars]) == sorted(true_ds_vars)
        assert sorted([i for i in processor_modules.process_nightlight().coords]) == sorted(self.dims)

    def test_process_human_settlement_built(self):
        """
        Test function for processing GHSL collection
        Output of process_human_settlement_built should be xarray
        dataset with 5 variables and lat, lon dimensions
        """
        band = 'built_characteristics'
        dataset_name = 'human_settlement_layer_built_up'
        collection = 'JRC/GHSL/P2023A/GHS_BUILT_C/2018'
        cadence = 'yearly'
        resolution = '10'
        buffer_size = '100'

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, resolution, buffer_size, self.utils)

        prefix = '{}.{}.'.format(dataset_name, band)
        stats_vars = ['mode', 'var', 'built']
        class_vars = []
        for k, v in GHSL_Built_Class.items():
            class_vars.append(GHSL_Built_Class[k]['class'])

        stats_vars.extend(class_vars)
        combined_vars = stats_vars
        true_ds_vars = reduce(lambda res, item: res + [prefix + item], combined_vars, [])
        assert type(processor_modules.process_human_settlement_built()) is xr.core.dataset.Dataset
        assert sorted([i for i in processor_modules.process_human_settlement_built().data_vars]) == sorted(true_ds_vars)
        assert sorted([i for i in processor_modules.process_human_settlement_built().coords]) == sorted(self.dims)

    def test_process_global_human_modification(self):
        """
        Test function for processing gHM collection
        Output of process_global_human_modification should be xarray
        dataset with 5 variables and lat, lon dimensions
        """
        band = 'gHM'
        dataset_name = 'global_human_modification'
        collection = 'CSP/HM/GlobalHumanModification'
        cadence = 'yearly'
        resolution = '1000'

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, resolution, self.buffer_size, self.utils)

        prefix = '{}.{}.'.format(dataset_name, band)
        true_ds_vars = ['var', 'mean', 'max', 'min', 'mode']
        true_ds_vars = reduce(lambda res, item: res + [prefix + item], true_ds_vars, [])

        assert type(processor_modules.process_global_human_modification()) is xr.core.dataset.Dataset
        assert sorted([i for i in processor_modules.process_global_human_modification().data_vars]) == \
               sorted(true_ds_vars)
        assert sorted([i for i in processor_modules.process_global_human_modification().coords]) == \
               sorted(self.dims)

