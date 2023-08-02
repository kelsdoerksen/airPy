"""
Test functions in processor_modules
"""
from airpy.processor_modules import ProcessorModules
from airpy.utils import Utils
import xarray as xr
import ee


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

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, self.buffer_size, self.utils)


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

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, self.buffer_size, self.utils)

        true_ds_vars = ['modis.evg_conif', 'modis.evg_broad', 'modis.dcd_needle', 'modis.dcd_broad',
                        'modis.mix_forest', 'modis.cls_shrub', 'modis.open_shrub', 'modis.woody_savanna',
                        'modis.savanna', 'modis.grassland', 'modis.perm_wetland', 'modis.cropland', 'modis.urban',
                        'modis.crop_nat_veg', 'modis.perm_snow', 'modis.barren', 'modis.water_bds', 'modis.mode',
                        'modis.var']

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

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, self.buffer_size, self.utils)

        true_ds_vars = ['fire.broad_decid', 'fire.broad_ever', 'fire.burnt', 'fire.crop_irr', 'fire.crop_rain',
                        'fire.crop_veg', 'fire.grassland', 'fire.herb_tree_shrub', 'fire.lichen_moss', 'fire.mode',
                        'fire.needle_decid', 'fire.needle_ever', 'fire.shrub_herb_flood', 'fire.shrubland',
                        'fire.sparse_veg', 'fire.tree_flooded', 'fire.tree_mixed', 'fire.tree_shrub_herb',
                        'fire.unburnt', 'fire.var', 'fire.veg_crop']

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

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, self.buffer_size, self.utils)

        true_ds_vars = ['pop.var', 'pop.max', 'pop.min', 'pop.mean']

        assert type(processor_modules.process_pop()) is xr.core.dataset.Dataset
        assert sorted([i for i in processor_modules.process_pop().data_vars]) == sorted(true_ds_vars)
        assert sorted([i for i in processor_modules.process_pop().coords]) == sorted(self.dims)

    def test_process_nightlight(self):
        """Test function for processing nightlight collection
        Output of process_pop should be xarray dataset with
        5 variables and lat, lon dimensions
        """
        band = 'avg_rad'
        dataset_name = 'nightlight'
        collection = 'NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG'
        cadence = 'monthly'

        processor_modules = ProcessorModules(self.point, collection, band, cadence, self.month, self.year,
                                             dataset_name, self.buffer_size, self.utils)

        true_ds_vars = ['nightlight.var', 'nightlight.mean', 'nightlight.max', 'nightlight.min']

        assert type(processor_modules.process_nightlight()) is xr.core.dataset.Dataset
        assert sorted([i for i in processor_modules.process_nightlight().data_vars]) == sorted(true_ds_vars)
        assert sorted([i for i in processor_modules.process_nightlight().coords]) == sorted(self.dims)

