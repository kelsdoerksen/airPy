"""
Module for processing GEE datasets
"""

from metric_utils import MetricUtils
import numpy as np
import ee
from gee_class_constants import MODIS_LC_Type1, FIRE_LC, GHSL_Built_Class


class ProcessorModules:
    def __init__(self, point, collection, band, cadence, month, year,
                 dataset_name, resolution, buffer_size, utils):
        self.point = point
        self.collection = collection
        self.band = band
        self.cadence = cadence
        self.month = month
        self.year = year
        self.dataset_name = dataset_name
        self.resolution = resolution
        self.buffer_size = buffer_size
        self.utils = utils

    def process_collection_for_img(self):
        """
        Processes GEE dataset
        :return: numpy array of raw data from GEE
        """
        lat, lon = self.point['coordinates'][1], self.point['coordinates'][0]
        collection = ee.ImageCollection(self.collection). \
            filterDate('{}-01-01'.format(self.year), '{}-01-01'.format(self.year + 1))
        # Select band type
        data = collection.select(self.band)
        # Get img from collection based on temporal cadence
        img = self.utils.get_img_from_collect(data, self.cadence, self.month, self.year)

        # Check if resampling needed
        if float(self.buffer_size) > self.utils.get_allowable_buffer_size(self.resolution):
            # Resample
            crs = 'EPSG:4326'
            new_resolution = self.utils.get_resampled_resolution_size(self.buffer_size)
            print('Max buffer size exceeded, resampling to {}m to match GEE requirements'.format(new_resolution))
            img = img.resample('bilinear').reproject(crs=crs, scale=new_resolution)

        if self.dataset_name == 'modis':
            default_value = 17

        elif self.dataset_name == 'fire':
            default_value = 160

        elif self.dataset_name in ['population', 'human_settlement_layer_built_up', 'global_human_modification']:
            default_value = 0

        # Get square extent based on buffer
        sq_extent = self.utils.get_buffer_extent(lat, lon, self.buffer_size, default_value, img)

        # Get band of interest
        band_arr = sq_extent.get(self.band)
        np_arr = np.array(band_arr.getInfo())

        save_file = {'lat': lat,
                     'lon': lon,
                     'data_array': np_arr}

        return save_file

    def process_modis(self):
        """
        Processes modis GEE data
        :return: xarray of MODIS GEE features
        """
        default_value = 17
        lat, lon = self.point['coordinates'][1], self.point['coordinates'][0]
        print('Processing lat, lon: {}, {}'.format(lat, lon))

        collection = ee.ImageCollection(self.collection). \
            filterDate('{}-01-01'.format(self.year), '{}-01-01'.format(self.year + 1))
        # Select band type
        data = collection.select(self.band)
        # Get img from collection based on temporal cadence
        img = self.utils.get_img_from_collect(data, self.cadence, self.month, self.year)

        # Check if resampling needed
        if float(self.buffer_size) > self.utils.get_allowable_buffer_size(self.resolution):
            # Resample
            crs = 'EPSG:4326'
            new_resolution = self.utils.get_resampled_resolution_size(self.buffer_size)
            print('Max buffer size exceeded, resampling to {}m to match GEE requirements'.format(new_resolution))
            img = img.resample('bilinear').reproject(crs=crs, scale=new_resolution)

        # Get square extent based on buffer
        sq_extent = self.utils.get_buffer_extent(lat, lon, self.buffer_size, default_value, img)

        # Get band of interest
        band_arr = sq_extent.get(self.band)
        np_arr = np.array(band_arr.getInfo())

        metric_utils = MetricUtils(np_arr)

        lc_pct_cov = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        mode = metric_utils.get_mode()
        var = np.nanvar(np_arr)
        pct_cov_all = metric_utils.get_perc_cov(self.dataset_name)
        for i in range(len(lc_pct_cov)):
            lc_pct_cov[i].append(pct_cov_all[i+1]['pct_cov'])

        lc = 'modis'
        mode_xr = self.utils.make_dataset(mode, '{}.{}.mode'.format(lc, self.band), lat, lon)
        var_xr = self.utils.make_dataset(var, '{}.{}.var'.format(lc, self.band), lat, lon)
        combo_xr = mode_xr.merge(var_xr)

        pct_all_xr = []
        for i in range(len(lc_pct_cov)):
            pct_all_xr.append(self.utils.make_dataset(lc_pct_cov[i][0], lc + '.' + self.band + '.' +
                                                      MODIS_LC_Type1[i+1]['class'], lat, lon))

        combined_xr = combo_xr.merge(pct_all_xr[0]).merge(pct_all_xr[1]).merge(pct_all_xr[2]). \
            merge(pct_all_xr[3]).merge(pct_all_xr[4]).merge(pct_all_xr[5]).merge(pct_all_xr[6]). \
            merge(pct_all_xr[7]).merge(pct_all_xr[8]).merge(pct_all_xr[9]).merge(pct_all_xr[10]). \
            merge(pct_all_xr[11]).merge(pct_all_xr[12]).merge(pct_all_xr[13]).merge(pct_all_xr[14]). \
            merge(pct_all_xr[15]).merge(pct_all_xr[16])

        return combined_xr

    def process_fire(self):
        """
        Processes fire GEE data
        :return: xarray of fire GEE features
        """
        default_value = 160
        lat, lon = self.point['coordinates'][1], self.point['coordinates'][0]
        print('Processing lat, lon: {}, {}'.format(lat, lon))

        collection = ee.ImageCollection(self.collection). \
            filterDate('{}-01-01'.format(self.year), '{}-01-01'.format(self.year + 1))
        # Select band type
        data = collection.select(self.band)
        # Get img from collection based on temporal cadence
        img = self.utils.get_img_from_collect(data, self.cadence, self.month, self.year)

        # Check if in Arctic/Antarctica
        if self.utils.check_in_arctic_or_antarctic(lat):
            np_arr = np.zeros((2, 2))+160
        elif self.utils.check_water_bodies(lat, lon):
            np_arr = np.zeros((2, 2))+160
        else:
            if float(self.buffer_size) > self.utils.get_allowable_buffer_size(self.resolution):
                # Resample
                crs = 'EPSG:4326'
                new_resolution = self.utils.get_resampled_resolution_size(self.buffer_size)
                print('Max buffer size exceeded, resampling to {}m to match GEE requirements'.format(new_resolution))
                img = img.resample('bilinear').reproject(crs=crs, scale=new_resolution)

            # Select band type
            data = img.select(self.band)
            # Get square extent based on buffer
            try:
                sq_extent = self.utils.get_buffer_extent(lat, lon, self.buffer_size, default_value, data)
                # Convert to array
                band_arr = sq_extent.get(self.band)
                np_arr = np.array(band_arr.getInfo())
            except Exception as e:
                if 'Image.sampleRectangle' in str(e):
                    # If exception occurred, this is due to GEE error of too many pixels due to curvature of Earth,
                    # Set to 40% of buffer and calculate
                    print("type error: " + str(e) + " Manually setting buffer size to 40% of specified.")
                    new_buffer = int(self.buffer_size) * 0.4
                    sq_extent = self.utils.get_buffer_extent(lat, lon, new_buffer, default_value, data)
                    # Convert to array
                    band_arr = sq_extent.get(self.band)
                    np_arr = np.array(band_arr.getInfo())
                else:
                    np_arr = np.nan
        metric_utils = MetricUtils(np_arr)

        pct_cov_1, pct_cov_2, pct_cov_3, pct_cov_4 = [], [], [], []
        pct_cov_5, pct_cov_6, pct_cov_7, pct_cov_8 = [], [], [], []
        pct_cov_9, pct_cov_10, pct_cov_11, pct_cov_12 = [], [], [], []
        pct_cov_13, pct_cov_14, pct_cov_15, pct_cov_16 = [], [], [], []
        pct_cov_17, pct_unburnt, pct_burnt = [], [], []

        # Get basic stats
        mode = metric_utils.get_mode()
        var = np.nanvar(np_arr)

        pct_cov_all = metric_utils.get_perc_cov(self.dataset_name)
        pct_cov_1.append(pct_cov_all[10]['pct_cov'])
        pct_cov_2.append(pct_cov_all[20]['pct_cov'])
        pct_cov_3.append(pct_cov_all[30]['pct_cov'])
        pct_cov_4.append(pct_cov_all[40]['pct_cov'])
        pct_cov_5.append(pct_cov_all[50]['pct_cov'])
        pct_cov_6.append(pct_cov_all[60]['pct_cov'])
        pct_cov_7.append(pct_cov_all[70]['pct_cov'])
        pct_cov_8.append(pct_cov_all[80]['pct_cov'])
        pct_cov_9.append(pct_cov_all[90]['pct_cov'])
        pct_cov_10.append(pct_cov_all[100]['pct_cov'])
        pct_cov_11.append(pct_cov_all[110]['pct_cov'])
        pct_cov_12.append(pct_cov_all[120]['pct_cov'])
        pct_cov_13.append(pct_cov_all[130]['pct_cov'])
        pct_cov_14.append(pct_cov_all[140]['pct_cov'])
        pct_cov_15.append(pct_cov_all[150]['pct_cov'])
        pct_cov_16.append(pct_cov_all[170]['pct_cov'])
        pct_cov_17.append(pct_cov_all[180]['pct_cov'])
        pct_unburnt.append(pct_cov_all[160]['pct_cov'])
        pct_burnt.append(metric_utils.calc_burnt_pct())

        # Make xarray dataset
        lc = 'fire'
        mode_xr = self.utils.make_dataset(mode, '{}.{}.mode'.format(lc, self.band), lat, lon)
        var_xr = self.utils.make_dataset(var, '{}.{}.var'.format(lc, self.band), lat, lon)
        combo_xr = mode_xr.merge(var_xr)

        pct_1_xr = self.utils.make_dataset(pct_cov_1, lc + '.' + self.band + '.' + FIRE_LC[10]['class'], lat, lon)
        pct_2_xr = self.utils.make_dataset(pct_cov_2, lc + '.' + self.band + '.' + FIRE_LC[20]['class'], lat, lon)
        pct_3_xr = self.utils.make_dataset(pct_cov_3, lc + '.' + self.band + '.' + FIRE_LC[30]['class'], lat, lon)
        pct_4_xr = self.utils.make_dataset(pct_cov_4, lc + '.' + self.band + '.' + FIRE_LC[40]['class'], lat, lon)
        pct_5_xr = self.utils.make_dataset(pct_cov_5, lc + '.' + self.band + '.' + FIRE_LC[50]['class'], lat, lon)
        pct_6_xr = self.utils.make_dataset(pct_cov_6, lc + '.' + self.band + '.' + FIRE_LC[60]['class'], lat, lon)
        pct_7_xr = self.utils.make_dataset(pct_cov_7, lc + '.' + self.band + '.' + FIRE_LC[70]['class'], lat, lon)
        pct_8_xr = self.utils.make_dataset(pct_cov_8, lc + '.' + self.band + '.' + FIRE_LC[80]['class'], lat, lon)
        pct_9_xr = self.utils.make_dataset(pct_cov_9, lc + '.' + self.band + '.' + FIRE_LC[90]['class'], lat, lon)
        pct_10_xr = self.utils.make_dataset(pct_cov_10, lc + '.' + self.band + '.' + FIRE_LC[100]['class'], lat, lon)
        pct_11_xr = self.utils.make_dataset(pct_cov_11, lc + '.' + self.band + '.' + FIRE_LC[110]['class'], lat, lon)
        pct_12_xr = self.utils.make_dataset(pct_cov_12, lc + '.' + self.band + '.' + FIRE_LC[120]['class'], lat, lon)
        pct_13_xr = self.utils.make_dataset(pct_cov_13, lc + '.' + self.band + '.' + FIRE_LC[130]['class'], lat, lon)
        pct_14_xr = self.utils.make_dataset(pct_cov_14, lc + '.' + self.band + '.' + FIRE_LC[140]['class'], lat, lon)
        pct_15_xr = self.utils.make_dataset(pct_cov_15, lc + '.' + self.band + '.' + FIRE_LC[150]['class'], lat, lon)
        pct_16_xr = self.utils.make_dataset(pct_cov_16, lc + '.' + self.band + '.' + FIRE_LC[170]['class'], lat, lon)
        pct_17_xr = self.utils.make_dataset(pct_cov_17, lc + '.' + self.band + '.' + FIRE_LC[180]['class'], lat, lon)
        punburnt_xr = self.utils.make_dataset(pct_unburnt, lc + '.' + self.band + '.' + FIRE_LC[160]['class'], lat, lon)
        pburnt_xr = self.utils.make_dataset(pct_burnt, lc + '.' + self.band + '.' + 'burnt', lat, lon)

        # Combine datasets
        combined_xr = combo_xr.merge(pct_1_xr).merge(pct_2_xr).merge(pct_3_xr).merge(pct_4_xr).merge(
            pct_5_xr).merge(pct_6_xr).merge(pct_7_xr).merge(pct_8_xr).merge(pct_9_xr).merge(pct_10_xr).merge(
            pct_11_xr).merge(pct_12_xr).merge(pct_13_xr).merge(pct_14_xr).merge(pct_15_xr).merge(pct_16_xr).merge(
            pct_17_xr).merge(punburnt_xr).merge(pburnt_xr)

        return combined_xr

    def process_pop(self):
        """
        Processes population GEE data
        :return: xarray of population GEE features
        """
        default_value = 0
        lat, lon = self.point['coordinates'][1], self.point['coordinates'][0]
        print('Processing lat, lon: {}, {}'.format(lat, lon))
        collection = ee.ImageCollection(self.collection). \
            filterDate('{}-01-01'.format(self.year), '{}-01-01'.format(self.year + 1))
        # Select band type
        data = collection.select(self.band)
        # Get img from collection based on temporal cadence
        img = self.utils.get_img_from_collect(data, self.cadence, self.month, self.year)

        # Check if resampling needed
        if float(self.buffer_size) > self.utils.get_allowable_buffer_size(self.resolution):
            # Resample
            crs = 'EPSG:4326'
            new_resolution = self.utils.get_resampled_resolution_size(self.buffer_size)
            print('Max buffer size exceeded, resampling to {}m to match GEE requirements'.format(new_resolution))
            img = img.resample('bilinear').reproject(crs=crs, scale=new_resolution)

        # Get square extent based on buffer
        sq_extent = self.utils.get_buffer_extent(lat, lon, self.buffer_size, default_value, img)

        # Get band of interest
        band_arr = sq_extent.get(self.band)
        np_arr = np.array(band_arr.getInfo())

        # Get basic stats
        mean_val = np.nanmean(np_arr)
        max_val = np.max(np_arr)
        min_val = np.min(np_arr)
        var_val = np.nanvar(np_arr)

        var_xr = self.utils.make_dataset(var_val, '{}.{}.var'.format(self.dataset_name, self.band), lat, lon)
        mean_xr = self.utils.make_dataset(mean_val, '{}.{}.mean'.format(self.dataset_name, self.band), lat, lon)
        max_xr = self.utils.make_dataset(max_val, '{}.{}.max'.format(self.dataset_name, self.band), lat, lon)
        min_xr = self.utils.make_dataset(min_val, '{}.{}.min'.format(self.dataset_name, self.band), lat, lon)

        combined_xr = var_xr.merge(mean_xr).merge(max_xr).merge(min_xr)

        return combined_xr

    def process_nightlight(self):
        """
        Processes nightlight GEE data
        :return: xarray of nightlight GEE features
        """
        default_value = 0
        lat, lon = self.point['coordinates'][1], self.point['coordinates'][0]
        print('Processing lat, lon: {}, {}'.format(lat, lon))

        # Skipping if over the arctic/antarctica, causes issues for nightlights sampling and can assume data is 0
        if self.utils.check_in_arctic_or_antarctic(lat):
            np_arr = np.zeros((2, 2))
        else:
            collection = ee.ImageCollection(self.collection). \
                filterDate('{}-01-01'.format(self.year), '{}-01-01'.format(self.year + 1))
            # Select band type
            data = collection.select(self.band)

            # Get img from collection based on temporal cadence
            img = self.utils.get_img_from_collect(data, self.cadence, self.month, self.year)

            # First resample to 500m, edge case for 55500m buffer extent with original resolution
            crs = 'EPSG:4326'
            img = img.resample('bilinear').reproject(crs=crs, scale=500)

            # Check if resampling needed
            if float(self.buffer_size) > self.utils.get_allowable_buffer_size(self.resolution):
                # Resample
                new_resolution = self.utils.get_resampled_resolution_size(self.buffer_size)
                print('Max buffer size exceeded, resampling to {}m to match GEE requirements'.format(new_resolution))
                img.resample('bilinear').reproject(crs=crs, scale=new_resolution)

            # Get square extent based on buffer
            sq_extent = self.utils.get_buffer_extent(lat, lon, self.buffer_size, default_value, img)

            # Get band of interest
            band_arr = sq_extent.get(self.band)
            np_arr = np.array(band_arr.getInfo())

        # Get basic stats
        mean_val = np.nanmean(np_arr)
        var_val = np.nanvar(np_arr)
        max_val = np.max(np_arr)
        min_val = np.min(np_arr)

        var_xr = self.utils.make_dataset(var_val, '{}.{}.var'.format(self.dataset_name, self.band), lat, lon)
        mean_xr = self.utils.make_dataset(mean_val, '{}.{}.mean'.format(self.dataset_name, self.band), lat, lon)
        max_xr = self.utils.make_dataset(max_val, '{}.{}.max'.format(self.dataset_name, self.band), lat, lon)
        min_xr = self.utils.make_dataset(min_val, '{}.{}.min'.format(self.dataset_name, self.band), lat, lon)

        combined_xr = var_xr.merge(mean_xr).merge(max_xr).merge(min_xr)

        return combined_xr

    def process_human_settlement_built(self):
        """
        Processes Human Settlement Built Up Layer GEE data
        :return: xarray of GHSL GEE features
        """
        default_value = 0
        lat, lon = self.point['coordinates'][1], self.point['coordinates'][0]
        print('Processing lat, lon: {}, {}'.format(lat, lon))
        # Get img
        img = ee.Image(self.collection)

        # Check if in Arctic/Antarctica
        if self.utils.check_in_arctic_or_antarctic(lat):
            np_arr = np.zeros((2, 2))
        elif self.utils.check_water_bodies(lat, lon):
            np_arr = np.zeros((2, 2))
        else:
            # Check if resampling needed
            if float(self.buffer_size) > self.utils.get_allowable_buffer_size(self.resolution):
                # Resample
                crs = 'EPSG:4326'
                new_resolution = self.utils.get_resampled_resolution_size(self.buffer_size)
                print('Max buffer size exceeded, resampling to {}m to match GEE requirements'.format(new_resolution))
                img = img.resample('bilinear').reproject(crs=crs, scale=new_resolution)

            # Select band type
            data = img.select(self.band)
            # Get square extent based on buffer
            try:
                sq_extent = self.utils.get_buffer_extent(lat, lon, self.buffer_size, default_value, data)
                # Convert to array
                band_arr = sq_extent.get(self.band)
                np_arr = np.array(band_arr.getInfo())
            except Exception as e:
                if 'Image.sampleRectangle' in str(e):
                    # If exception occurred, this is due to GEE error of too many pixels due to curvature of Earth,
                    # Set to 40% of buffer and calculate
                    print("type error: " + str(e) + " Manually setting buffer size to 40% of specified.")
                    new_buffer = int(self.buffer_size)*0.4
                    sq_extent = self.utils.get_buffer_extent(lat, lon, new_buffer, default_value, data)
                    # Convert to array
                    band_arr = sq_extent.get(self.band)
                    np_arr = np.array(band_arr.getInfo())
                else:
                    np_arr = np.nan

        metric_utils = MetricUtils(np_arr)

        pct_cov_1, pct_cov_2, pct_cov_3, pct_cov_4, pct_cov_5 = [], [], [], [], []
        pct_cov_11, pct_cov_12, pct_cov_13, pct_cov_14, pct_cov_15 = [], [], [], [], []
        pct_cov_21, pct_cov_22, pct_cov_23, pct_cov_24, pct_cov_25 = [], [], [], [], []
        pct_built = []

        # Get basic stats
        mode = metric_utils.get_nonzero_mode()
        var = metric_utils.get_nonzero_var()

        pct_cov_all = metric_utils.get_perc_cov(self.dataset_name)
        pct_cov_1.append(pct_cov_all[1]['pct_cov'])
        pct_cov_2.append(pct_cov_all[2]['pct_cov'])
        pct_cov_3.append(pct_cov_all[3]['pct_cov'])
        pct_cov_4.append(pct_cov_all[4]['pct_cov'])
        pct_cov_5.append(pct_cov_all[5]['pct_cov'])
        pct_cov_11.append(pct_cov_all[11]['pct_cov'])
        pct_cov_12.append(pct_cov_all[12]['pct_cov'])
        pct_cov_13.append(pct_cov_all[13]['pct_cov'])
        pct_cov_14.append(pct_cov_all[14]['pct_cov'])
        pct_cov_15.append(pct_cov_all[15]['pct_cov'])
        pct_cov_21.append(pct_cov_all[21]['pct_cov'])
        pct_cov_22.append(pct_cov_all[22]['pct_cov'])
        pct_cov_23.append(pct_cov_all[23]['pct_cov'])
        pct_cov_24.append(pct_cov_all[24]['pct_cov'])
        pct_cov_25.append(pct_cov_all[25]['pct_cov'])
        pct_built.append(metric_utils.calc_built_pct())

        # Make xarray dataset
        mode_xr = self.utils.make_dataset(mode, '{}.{}.mode'.format(self.dataset_name, self.band), lat, lon)
        var_xr = self.utils.make_dataset(var, '{}.{}.var'.format(self.dataset_name, self.band), lat, lon)
        combo_xr = mode_xr.merge(var_xr)

        pct_1_xr = self.utils.make_dataset(pct_cov_1, self.dataset_name + '.' + self.band + '.' +
                                           GHSL_Built_Class[1]['class'], lat, lon)
        pct_2_xr = self.utils.make_dataset(pct_cov_2, self.dataset_name + '.' + self.band + '.' +
                                           GHSL_Built_Class[2]['class'], lat, lon)
        pct_3_xr = self.utils.make_dataset(pct_cov_3, self.dataset_name + '.' + self.band + '.' +
                                           GHSL_Built_Class[3]['class'], lat, lon)
        pct_4_xr = self.utils.make_dataset(pct_cov_4, self.dataset_name + '.' + self.band + '.' +
                                           GHSL_Built_Class[4]['class'], lat, lon)
        pct_5_xr = self.utils.make_dataset(pct_cov_5, self.dataset_name + '.' + self.band + '.' +
                                           GHSL_Built_Class[5]['class'], lat, lon)
        pct_11_xr = self.utils.make_dataset(pct_cov_11, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[11]['class'], lat, lon)
        pct_12_xr = self.utils.make_dataset(pct_cov_12, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[12]['class'], lat, lon)
        pct_13_xr = self.utils.make_dataset(pct_cov_13, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[13]['class'], lat, lon)
        pct_14_xr = self.utils.make_dataset(pct_cov_14, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[14]['class'], lat, lon)
        pct_15_xr = self.utils.make_dataset(pct_cov_15, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[15]['class'], lat, lon)
        pct_21_xr = self.utils.make_dataset(pct_cov_11, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[21]['class'], lat, lon)
        pct_22_xr = self.utils.make_dataset(pct_cov_12, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[22]['class'], lat, lon)
        pct_23_xr = self.utils.make_dataset(pct_cov_13, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[23]['class'], lat, lon)
        pct_24_xr = self.utils.make_dataset(pct_cov_14, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[24]['class'], lat, lon)
        pct_25_xr = self.utils.make_dataset(pct_cov_15, self.dataset_name + '.' + self.band + '.' +
                                            GHSL_Built_Class[25]['class'], lat, lon)
        pct_built_xr = self.utils.make_dataset(pct_built, self.dataset_name + '.' + self.band + '.' + 'built', lat, lon)

        # Combine datasets
        combined_xr = combo_xr.merge(pct_1_xr).merge(pct_2_xr).merge(pct_3_xr).merge(pct_4_xr).merge(
            pct_5_xr).merge(pct_11_xr).merge(pct_12_xr).merge(pct_13_xr).merge(pct_14_xr).merge(pct_15_xr).\
            merge(pct_21_xr).merge(pct_22_xr).merge(pct_23_xr).merge(pct_24_xr).merge(pct_25_xr).merge(pct_built_xr)

        return combined_xr

    def process_global_human_modification(self):
        """
        Processes Global Human Modification GEE data
        :return: xarray of GHSL GEE features
        """
        default_value = 0
        lat, lon = self.point['coordinates'][1], self.point['coordinates'][0]
        print('Processing lat, lon: {}, {}'.format(lat, lon))
        collection = ee.ImageCollection(self.collection)
        # Select band type
        data = collection.select(self.band)
        # Get img from collection
        img = data.first()

        # Check if in Arctic/Antarctica
        if self.utils.check_in_arctic_or_antarctic(lat):
            np_arr = np.zeros((2, 2))
        elif self.utils.check_water_bodies(lat, lon):
            np_arr = np.zeros((2, 2))
        else:
            # Check if resampling needed
            if float(self.buffer_size) > self.utils.get_allowable_buffer_size(self.resolution):
                # Resample
                crs = 'EPSG:4326'
                new_resolution = self.utils.get_resampled_resolution_size(self.buffer_size)
                print('Max buffer size exceeded, resampling to {}m to match GEE requirements'.format(new_resolution))
                img = img.resample('bilinear').reproject(crs=crs, scale=new_resolution)

            # Get square extent based on buffer
            sq_extent = self.utils.get_buffer_extent(lat, lon, self.buffer_size, default_value, img)

            # Convert to array
            band_arr = sq_extent.get(self.band)
            np_arr = np.array(band_arr.getInfo())
        metric_utils = MetricUtils(np_arr)

        # Get basic stats
        mode_val = metric_utils.get_mode()
        mean_val = np.nanmean(np_arr)
        max_val = np.max(np_arr)
        min_val = np.min(np_arr)
        var_val = np.nanvar(np_arr)

        mode_xr = self.utils.make_dataset(mode_val, '{}.{}.mode'.format(self.dataset_name, self.band), lat, lon)
        var_xr = self.utils.make_dataset(var_val, '{}.{}.var'.format(self.dataset_name, self.band), lat, lon)
        mean_xr = self.utils.make_dataset(mean_val, '{}.{}.mean'.format(self.dataset_name, self.band), lat, lon)
        max_xr = self.utils.make_dataset(max_val, '{}.{}.max'.format(self.dataset_name, self.band), lat, lon)
        min_xr = self.utils.make_dataset(min_val, '{}.{}.min'.format(self.dataset_name, self.band), lat, lon)

        combined_xr = mode_xr.merge(var_xr).merge(mean_xr).merge(max_xr).merge(min_xr)

        return combined_xr