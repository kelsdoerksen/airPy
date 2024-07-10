'''
Generate configuration dictionary and save as json file
airpy/configs/<config_filename> for airpy pipeline
@author: anonymous while under review
'''

import json
from datetime import datetime
import os
from utils import Utils


class GenerateConfig():
    def __init__(self, gee_data, region, date, analysis_type, add_time,
                 buffer_size, configs_dir, save_dir, band=None, save_type=None):
        self.gee_data = gee_data
        self.band = band
        self.region = region
        self.date = date
        self.analysis_type = analysis_type
        self.add_time = add_time
        self.buffer_size = buffer_size
        self.configs_dir = configs_dir
        self.save_dir = save_dir
        self.save_type = save_type

    def get_gee_collection_data(self):
        """
        Query json for GEE collection of interest
        :return: GEE collection dictionary
        """
        collection_file = '../configs/gee_collections.json'
        if not os.path.isfile(collection_file):
            raise FileNotFoundError
        else:
            with open('{}'.format(collection_file), 'r') as file:
                data_collection = json.load(file)

        if self.gee_data not in data_collection['gee_dataset'].keys():
            raise (ValueError('Dataset not supported. Please select one of modis, fire, population, nightlight,'
                              'human_settlement_layer_built_up or global_human_modification'))

        return data_collection['gee_dataset'][self.gee_data]

    def get_query_date(self):
        """
        Get year, month of query
        :return: year, month
        """
        months_dict = {'01': 'jan', '02': 'feb', '03': 'mar', '04': 'apr', '05': 'may', '06': 'june',
                       '07': 'july', '08': 'aug', '09': 'sept', '10': 'oct', '11': 'nov', '12': 'dec'}
        if self.date[5:7] not in months_dict.keys():
            raise ValueError('Invalid month entered.')
        return {'query_year': int(self.date[0:4]), 'query_month': months_dict[self.date[5:7]]}

    def check_query_date(self, collection):
        """
        Check if query date is valid for gee collection
        :param collection: gee dataset
        :return: exit script if inavlid, get month, year if valid
        """
        dt_fmt = '%Y-%m-%d'
        print(collection)
        if datetime.strptime(self.date, dt_fmt) < datetime.strptime(collection['min_date'], dt_fmt):
            raise ValueError('Start date must be later than {}'.format(collection['min_date']))

        if datetime.strptime(self.date, dt_fmt) > datetime.strptime(collection['max_date'], dt_fmt):
            raise ValueError('Start date must be earlier than {}'.format(collection['max_date']))

        return self.get_query_date()

    def get_boundary(self):
        """
        Downselect to global boundary of interest
        :param region: region on globe for analysis
        :return: regional lat,lon bounds
        """
        # Check if region is TOAR2 locations
        if self.region == 'toar2':
            with open('../configs/toar_locations.json', 'r') as file:
                toar_vals = json.load(file)
            return {'extent': '{}'.format(self.region), 'lats': toar_vals['toar2']['lats'],
                    'lons': toar_vals['toar2']['lons']}

        # get globe vals
        with open('../configs/globe_coords.json', 'r') as file:
            globe_vals = json.load(file)

        bbox_dict = {
            'globe':
                {'lats': [-90, 90], 'lons': [-180, 180]},
            'europe':
                {'lats': [35, 65], 'lons': [-10, 25]},
            'asia':
                {'lats': [20, 50], 'lons': [100, 145]},
            'australia':
                {'lats': [-50, -5], 'lons': [110, 160]},
            'north_america':
                {'lats': [20, 55], 'lons': [-125, -70]},
            'west_europe':
                {'lats': [25, 80], 'lons': [-20, 10]},
            'east_europe':
                {'lats': [25, 80], 'lons': [10, 40]},
            'west_north_america':
                {'lats': [10, 80], 'lons': [-140, -95]},
            'east_north_america':
                {'lats': [10, 80], 'lons': [-95, -50]},
            'mini_test':
                {'lats': [10, 15], 'lons': [-95, -90]},
        }

        accepted_locations = list(bbox_dict.keys())
        accepted_locations.append('toar2')

        # Check if user specified a custom region path that exists
        if self.region not in accepted_locations:
            if not os.path.isfile('{}'.format(self.region)):
                raise ValueError('Region specified must be one of: {}'.format(accepted_locations))
            else:
                print('User specified custom region at path: {}'.format(self.region))
                with open('{}'.format(self.region), 'r') as file:
                    custom_vals = json.load(file)
                return {'extent': 'custom', 'lats': custom_vals['lats'],
                        'lons': custom_vals['lons']}

        bbox = bbox_dict[self.region]

        # filter lats
        lats = [x for x in globe_vals['globe']['lats'] if (bbox['lats'][0] <= x <= bbox['lats'][1])]

        # filter lons
        lons = [x for x in globe_vals['globe']['lons'] if (bbox['lons'][0] <= x <= bbox['lons'][1])]

        return {'extent': '{}'.format(self.region), 'lats': lats, 'lons': lons}

    def get_band(self, gee_data):
        """
        Get either user-specified or default dataset band
        from GEE collection
        """
        if self.band is None:
            band = gee_data['default_band']
            print('User did not specify band, defaulting to: {}'.format(band))
            return band
        else:
            if self.band not in gee_data['supported_bands']:
                raise ValueError('Band specified must be one of: {}'.format(gee_data['supported_bands']))
            else:
                return self.band

    def generate_config_dict(self):
        """
        Generate config dictionary to use in airPy pipeline
        :return: dictionary of configuration data
        """
        config_dict = {}
        if not os.path.exists(self.configs_dir):
            os.makedirs(self.configs_dir)

        # Grab gee collection dict
        data = self.get_gee_collection_data()

        # Check that queried time is valid and return
        query_dates = self.check_query_date(data)

        # Get boundary box
        coords = self.get_boundary()

        # Get band
        band = self.get_band(data)

        config_dict['region'] = coords
        config_dict['dataset'] = data
        config_dict['band'] = band
        config_dict.update(query_dates)
        config_dict['analysis_type'] = self.analysis_type
        config_dict['buffer_size'] = self.buffer_size
        config_dict['save_dir'] = self.save_dir
        config_dict['file_type'] = self.save_type

        if self.add_time == 'True':
            config_dict['add_time'] = True
        else:
            config_dict['add_time'] = False

        # Write to json file
        with open('{}/config_{}_{}_{}_buffersize_{}_{}.json'.format(self.configs_dir, config_dict['region']['extent'],
                                                                    self.gee_data, self.date, self.buffer_size,
                                                                    self.analysis_type), 'w') as json_file:
            json.dump(config_dict, json_file, indent=4)

        return config_dict
