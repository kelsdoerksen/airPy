'''
Creates airypy config, queries GEE dataset of interest, process and return .nc file
@author: kdoerksen
'''

import ee
import argparse
import multiprocessing
from retry import retry
import logging
import time
from utils import Utils
from processor_modules import ProcessorModules
from generate_config import GenerateConfig
import datetime


# Initialize ee
ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')

# Argparse arguments for CLI
parser = argparse.ArgumentParser(description='pyaq pipeline',
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--gee_data",
                    help='''
                    Google Earth Engine Dataset of interest. 
                    Must be one of: 
                    modis, population, fire, or nightlight
                    ''',
                    required=True),
parser.add_argument("--region",
                    help='''
                    Boundary region on Earth to extract data
                    Must be one of: 
                    globe, europe, asia, australia, north_america, west_europe, 
                    east_europe, west_north_america, east_north_america.
                    ''',
                    required=True),
parser.add_argument("--date",
                    help='''
                    Date of query. Must be format YYYY-MM-DD
                    ''',
                    required=True)
parser.add_argument("--analysis_type",
                    help='''
                    Type of analysis. Must be one of: 
                    collection, images, collection_toar
                    ''',
                    required=True)
parser.add_argument("--add_time",
                    help='''
                    Specify if time component added to file.
                    Useful for integrating into time series
                    ML datasets. Specify y or n
                    ''',
                    required=True)
parser.add_argument("--buffer_size",
                            help='''
                            Specify roi buffer extent. 
                            Units in metres.
                            ''')
parser.add_argument("--configs_dir",
                    help='''
                    Specify config file directory
                    ''',
                    required=True)
parser.add_argument("--save_dir",
                    help='''
                    Specify run save directory
                    ''',
                    required=True)


def getRequests(config_data):
    """
    Generate a list of work items to be downloaded from GEE
    :param: confg_data: config data read from file
    :return: list of coordinates with gee data
    """
    dataset_name = config_data['dataset']['name']
    gee_data = config_data['dataset']['collection']
    year = config_data['query_year']
    month = config_data['query_month']
    cadence = config_data['dataset']['t_cadence']
    band = config_data['dataset']['band']
    buffer = config_data['buffer_size']
    analysis_type = config_data['analysis_type']
    save_dir = config_data['save_dir']

    points = []

    if config_data['region']['extent'] == 'toar2':
        lats = config_data['region']['lats']
        lons = config_data['region']['lons']
        for k in range(len(lats)):
            points.append({
                    'dataset_name': dataset_name,
                    'gee_data': gee_data,
                    'query_year': year,
                    'query_month': month,
                    't_cadence': cadence,
                    'band': band,
                    'buffer': buffer,
                    'analysis_type': analysis_type,
                    'save_dir': save_dir,
                    'coordinates': [lons[k], lats[k]]})
        return points

    lats = config_data['region']['lats']
    lons = config_data['region']['lons']
    for i in range(len(lons)):
        for j in range(len(lats)):
            points.append({
                'dataset_name': dataset_name,
                'gee_data': gee_data,
                'query_year': year,
                'query_month': month,
                't_cadence': cadence,
                'band': band,
                'buffer': buffer,
                'analysis_type': analysis_type,
                'save_dir': save_dir,
                'coordinates': [lons[i], lats[j]]})
    return points


@retry(tries=10, delay=1, backoff=2)
def getResult(index, point):
    """
    Handle HTTP requests to download GEE image
    :param: point: lat, lon point with config information
    :return: extracted GEE dataset features
    """
    # Generate img from given point
    collection = point['gee_data']
    c_band = point['band']
    c_cadence = point['t_cadence']
    c_month = point['query_month']
    c_year = point['query_year']
    dataset_name = point['dataset_name']
    buffer_size = point['buffer']
    analysis_type = point['analysis_type']

    utils = Utils(point)
    processor_modules = ProcessorModules(point, collection, c_band, c_cadence, c_month, c_year,
                                         dataset_name, buffer_size, utils)

    if analysis_type == 'images':
        return processor_modules.process_collection_for_img()

    # If not analyzing images, let's check which GEE type and process for xarray dataset
    if dataset_name == 'modis':
        return processor_modules.process_modis()

    if dataset_name == 'fire':
        return processor_modules.process_fire()

    if dataset_name == 'pop':
        return processor_modules.process_pop()

    if dataset_name == 'nightlight':
        return processor_modules.process_nightlight()


def saveResults(config_data, results_list):
    """
    Save final results
    :param config_data: config file data for saving
    :param results_list: list of results generated by pyaq
    :return: saved xarray or .npy files
    """
    # initialize utils to save and format with config data params
    utils = Utils(config_data)
    if config_data['analysis_type'] == 'collection':
        # format
        results_xr = utils.combine_data(results_list)
        # add time if specified by user
        if config_data['add_time']:
            results_xr = utils.add_time_data(results_xr)
        # save results_xr
        if utils.save_collection(results_xr):
            return
        else:
            print('Save was unsuccesful!')

    if config_data['analysis_type'] == 'images':
        if utils.save_imgs(results_list):
            return
        else:
            print('Save was unsuccesful!')


if __name__ == '__main__':
    st = time.time()
    print('Start time: {}'.format(datetime.datetime.fromtimestamp(st).strftime('%Y-%m-%d %H:%M:%S')))
    logging.basicConfig()

    args = parser.parse_args()

    # Generate config file from user inputs to run through pipeline
    generate_config = GenerateConfig(args.gee_data, args.region, args.date, args.analysis_type,
                                     args.add_time, args.buffer_size, args.configs_dir, args.save_dir)
    data = generate_config.generate_config_dict()
    items = getRequests(data)
    pool = multiprocessing.Pool(25)
    results = []
    for result in pool.starmap(getResult, enumerate(items)):
        results.append(result)
    pool.close()
    pool.join()

    # Save results
    saveResults(data, results)

    # get the end time of program
    et = time.time()
    # get the execution time
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
