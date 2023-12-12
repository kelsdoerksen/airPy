"""
Module for utility functions for pyaq
"""

import xarray as xr
from datetime import datetime, timedelta
import pandas as pd
import ee
import h5py
import os

class Utils():
    def __init__(self, config_data=None):
        self.config_data = config_data

    def add_time_data(self, ds):
        """
        Add time component to xarray dataset
        depending on time cadence (yearly, monthly)
        :param ds: xarray dataset
        :param config_file: user-specified config file
        :return:
        """
        ds_cadence = self.config_data['dataset']['t_cadence']
        ds_year = self.config_data['query_year']
        ds_month = self.config_data['query_month']

        startdate = datetime(ds_year, 1, 1)
        date_list = []

        mon_31_days = ['jan', 'mar', 'may', 'july', 'aug', 'oct', 'dec']
        mon_30_days = ['apr', 'june', 'sept', 'nov']

        leap_years = [2000, 2004, 2008, 2012, 2016, 2020, 2024]
        if int(ds_year) in leap_years:
            year_len = 366
        else:
            year_len = 365
        if ds_cadence == 'yearly':
            for i in range(year_len):
                d = startdate + timedelta(days=i)
                date_list.append(pd.Timestamp(d.strftime('%Y-%m-%d')))
        elif ds_cadence == 'monthly':
            if ds_month in mon_31_days:
                mon_len = 31
            elif ds_month in mon_30_days:
                mon_len = 30
            elif ds_month == 'feb':
                if int(ds_year) in leap_years:
                    mon_len = 29
                else:
                    mon_len = 28
            for i in range(mon_len):
                d = startdate + timedelta(days=i)
                date_list.append(pd.Timestamp(d.strftime('%Y-%m-%d')))

        ds = ds.expand_dims(dim={'time': date_list}, axis=0)
        ds = ds.set_coords('time')
        # remove dim_0 artifact
        if 'dim_0' in [i for i in ds.dims]:
            ds = ds.squeeze('dim_0')
        ds = ds.transpose('lon', 'lat', 'time')

        return ds

    def get_img_from_collect(self, data, collect_cadence, analysis_month, analysis_year):
        """
        Get img of interest from collection. Currently supports monthly, yearly cadence.
        If yearly cadence, grab first img in collection
        If monthly, query over that month and grab first
        :param data: GEE data collection
        :param collect_cadence: GEE collection cadence
        :param analysis_month: config-specified query_month
        :param analysis_year: config-specified query_year
        :return: GEE image
        """

        months_dict = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'june': '06',
                       'july': '07', 'aug': '08', 'sept': '09', 'oct': '10', 'nov': '11', 'dec': '12'}

        if collect_cadence == 'yearly':
            img = data.first()
            return img
        if collect_cadence == 'monthly':
            mon = months_dict[analysis_month]
            if analysis_month in ['jan', 'feb', 'mar', 'apr', 'may', 'june' ,'july', 'aug']:
                im = data.filterDate('{}-{}-01'.format(analysis_year, mon),
                                     '{}-0{}-01'.format(analysis_year, int(mon[1]) + 1))
                img = im.first()
                return img
            elif analysis_month == 'sept':
                im = data.filterDate('{}-{}-01'.format(analysis_year, mon),
                                     '{}-{}-01'.format(analysis_year, int(mon[1]) + 1))
                img = im.first()
                return img
            elif analysis_month in ['oct', 'nov']:
                im = data.filterDate('{}-{}-01'.format(analysis_year, mon),
                                     '{}-{}-01'.format(analysis_year, int(mon)+1))
                img = im.first()
                return img
            elif analysis_month == 'dec':
                im = data.filterDate('{}-{}-01'.format(analysis_year, mon),
                                     '{}-01-01'.format(int(analysis_year+1)))
                img = im.first()
                return img

    def get_buffer_extent(self, lat, lon, buffer_size, default_class, gee_img):
        """
        :param lat: latitude point
        :param lon: longitude point
        :param buffer_size: config-specified buffer extent
        :param default_class: default class according to GEE dataset
        :param gee_img: GEE data
        :return:
        """
        point = ee.Geometry.Point([lon, lat])
        # Create buffer to match whatever grid size desired
        roi = point.buffer(int(buffer_size))
        # Sample img over roi
        sq_extent = gee_img.sampleRectangle(region=roi, defaultValue=default_class)
        return sq_extent

    def make_dataset(self, array, var, lats, lons):
        """
        :param array:
        :param array:
        :return:
        Makes an xarray dataset from an array with given
        lat, lon for specified variable
        """
        xr_data = xr.DataArray(array, coords={'lat': lats, 'lon': lons})
        xr_dataset = xr_data.to_dataset(name='{}'.format(var))
        return xr_dataset

    def combine_data(self, results_list):
        """
        Combine data into xarray format
        :param results_list: list of xarray datasets to combine
        :return: xarray of results
        """
        new_results = []
        for i in range(len(results_list)):
            new_results.append(results_list[i].expand_dims(dim={'lat': 1, 'lon': 1}))

        data_xr = new_results[0].merge(new_results[1])
        for n in range(len(new_results)-2):
            data_xr = data_xr.merge(new_results[n+2])

        return data_xr

    def save_collection(self, results_data):
        """
        Save xarray of features from collection to netcdf
        :param config_file: user specified config
        :param results_data: xarray of calculated GEE features
        """
        save_dir = self.config_data['save_dir']
        name = self.config_data['dataset']['name']
        year = self.config_data['query_year']
        month = self.config_data['query_month']
        buffer = self.config_data['buffer_size']
        cadence = self.config_data['dataset']['t_cadence']
        region = self.config_data['region']['extent']

        # Create save directory if it does not already exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        if 'add_time' in self.config_data:
            add_time = 'with_time'
        else:
            add_time = 'no_time'

        if cadence == 'yearly':
            save_name = '{}_{}_{}_buffersize_{}_{}'.format(name, year, region, buffer, add_time)
        if cadence == 'monthly':
            save_name = '{}_{}_{}_{}_buffersize_{}_{}'.format(name, month, year, region, buffer, add_time)

        if type(results_data) is xr.core.dataset.Dataset:
            results_data.to_netcdf('{}/{}.nc'.format(save_dir, save_name))
            return True
        else:
            return False


    def save_img(self, results_data):
        """
        Save individual images
        :param config_file: user-specified config file
        :param results_data: array of GEE extracted data
        :return:
        """
        # Save to hdf file
        with h5py.File('{}/{}_{}_data.hdf'.format(self.config_data['save_dir'],
                                                  results_data['lat'], results_data['lon']), 'w') as outfile:
            h5_dataset = outfile.create_dataset('gee data', data=results_data['data_array'])
            h5_dataset.attrs['lat'] = results_data['lat']
            h5_dataset.attrs['lon'] = results_data['lon']
            h5_dataset.attrs['year'] = self.config_data['year']


    def save_custom_df(self, results_data):
        """
        If custom lat, lon json list specified, save as
        a dataframe of lat, lon and variables respectively
        """
        save_dir = self.config_data['save_dir']
        name = self.config_data['dataset']['name']
        year = self.config_data['query_year']
        month = self.config_data['query_month']
        buffer = self.config_data['buffer_size']
        cadence = self.config_data['dataset']['t_cadence']
        region = self.config_data['region']['extent']
        band = self.config_data['dataset']['band']

        # Create save directory if it does not already exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        if 'add_time' in self.config_data:
            add_time = 'with_time'
        else:
            add_time = 'no_time'

        if cadence == 'yearly':
            save_name = '{}_{}_{}_{}_buffersize_{}_{}'.format(name, band, year, region, buffer, add_time)
        if cadence == 'monthly':
            save_name = '{}_{}_{}_{}_{}_buffersize_{}_{}'.format(name, band, month, year, region, buffer, add_time)

        # Get list of variables and make df column names
        column_names = ['lat', 'lon']
        for i in results_data[0].data_vars:
            column_names.append(i)

        data = []
        for result in results_data:
            data_list = [float(result.lat.values), float(result.lon.values)]
            for i in result.data_vars:
                data_list.append(float(result[i].values))
            data.append(data_list)

        df = pd.DataFrame(data, columns=column_names)
        df.to_csv('{}/{}.csv'.format(save_dir, save_name))
