# airPy
<div align="center">
<p>
<b><a href="#-description">Description</a></b>
|
<b><a href="#-installation">Installation</a></b>
|
<b><a href="#-running-the-airpy-pipeline">Running Pipeline</a></b>
|
<b><a href="#-testing">Testing</a></b>
|
<b><a href="#-description">Citing</a></b>
|
</p>
</div>

## Description
The airPy package was developed to extract high-resolution satellite data from Google Earth Engine and generate statistical metrics with the output in the form of Machine Learning-ready features for air pollution studies.
The code in this repository performs the following tasks:

**1. Download satellite data from Google Earth Engine**
  * Per specified latitude, longitude, and AOI buffer extent, data is downloaded from Google Earth Engine. The download job is fully specified by the user-generated configuration file, which includes all details for the data to be downloaded and processed, including: collection type, latitude/longitude points, analysis period, and buffer size.
  * Data can be saved as an xarray format covering the user-specified AOI extent, or as individual images per latitude, longitude point given.

**2. Generate Machine Learning-ready features**
* Per latitude, longitude point of interest over the user-specified AOI, relevant statistical features are calculated for the following collections: [MODIS Land cover Yearly Product](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#citations), [MODIS Fire_cci Burned Area Pixel Product](https://developers.google.com/earth-engine/datasets/catalog/ESA_CCI_FireCCI_5_1#description), [Gridded Population of the World Version 4.11)](https://developers.google.com/earth-engine/datasets/catalog/CIESIN_GPWv411_GPW_Population_Density), [VIIRS Nighttime Day/Night Band Composites Version 1](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG),
[Global settlement characteristics 2018](https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_C), and [Global Human Modification](https://developers.google.com/earth-engine/datasets/catalog/CSP_HM_GlobalHumanModification#citations).
    * Features are calculated based on the temporal cadence specified.
    * Where data is unavailable due to lack of satellite coverage, data is set to NaN or filled with specified fill value to avoid calculation errors.

This package has supported the research of the following paper(s):
*  K. Doerksen*, Y. Marchetti, K. Miyazaki, K. Bowman, S. Lu, Y. J. Montgomery, Gal, F. Kalaitzis “Leveraging Deep Learning for Physical Model Bias of Global Air Quality Estimates”. NeurIPS Machine Learning and the Physical Sciences Workshop 2023

### `airPy` feature extraction
The diagram below depicts an example of the extraction process over the extent of Rwanda. Per latitude, longitude point specified by the user given buffer radius of `r`:
* Query the GEE dataset of interest
* Create a user-specified sized radius buffer around the point of interest
* Extract the data over the buffer AOI
* Process features of interest (i.e. maximum population per grid point from World Population dataset, percent of each land cover class from MODIS dataset, etc.)

![`airPy` AOI extraction process.](paper/figures/airpy_updated.png)

## Installation
Clone the repo: 
```
git clone git@github.com:kelsdoerksen/airPy.git
```
Navigate to the airPy folder and install the package using `pip`.
```
pip install airpy
```
Install package dependencies using
```
pip install -r requirements.txt  
```

To use the Google Earth Engine API, you must create and authenticate a Google Earth Engine account. Information on the Earth Engine Python API can be found [here](https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api). 

## Creating ML-ready features from GEE data with ``airPy``
#### Running the airPy pipeline
The airPy pipeline job is fully specified by a configuration dictionary generated by the `GenerateConfig` class. To create a new configuration and run the pipeline use the command
```
python run_airpy.py
```
and specify the various parameters of the data of interest. The available configurable parameters are:
* `--gee_data`: The name of the GEE dataset of interest, either modis, pop, fire, or nightlight.
    *    `modis`: MCD12Q1.061 MODIS Land Cover Type Yearly Global 500m, available 2001-01-01 to 2021-01-01
    *    `pop`: GPWv411: Population Density (Gridded Population of the World Version 4.11), available 2000-01-01 to 2020-01-01
    *    `fire`: FireCCI51: MODIS Fire_cci Burned Area Pixel Product, Version 5.1, available 2001-01-01 to 2020-12-01
    *    `nightlight`: VIIRS Nighttime Day/Night Band Composites Version 1, available 2012-04-01 to 2023-01-01
    *    `human_settlement_layer_built_up`: Global Human Settlement Layer (GHSL) built up characteristics, available 2018-01-01 –2018-12-31
    *    `global_human_modification`: global Human Modification dataset (gHM), available 2016-01-01–2016-12-31T
* `--region`: Boundary region on Earth to extract data in (latitudes), (longitudes). Must be one of:
    *   `globe`: (-90, 90),(-180, 180)
    *   `europe` (35, 65),(-10, 25)
    *   `asia`: (20, 50),(100, 145)
    *   `australia`: (-50, -10),(130, 170)
    *   `north_america`: (20, 55),(-125, -70)
    *   `west_europe`: (25, 80),(-20, 10)
    *   `east_europe`: (25, 80),(10, 40)
    *   `west_north_america`: (10, 80),(-140, -95)
    *   `east_north_america`: (10, 80), (-95, -50)
    *   `toar2`: Locations of TOAR2 stations based on TOAR2 metadata
    *   `custom`: Path to custom json file of dictionary `{lats: [], lons: []}`, respectively
* `--date`: Date of query. Must be in format 'YYYY-MM-DD'
* `--band`: Dataset band of interest.
* `--analysis_type`: Type of analysis for data extraction. Must be one of collection, images.
* `--add_time`: Specify if time component should be added to collection xarray. Useful for integrating into time series ML datasets. One of 'True' or 'False'
* `--buffer_size`: Specify region of interest (ROI) buffer extent. Units in metres.
* `--configs-dir`: Specify the output directory for the config file.
* `--save_dir`: Specify run rave directory.
* `--save_type`: Specify file type to save generated features. Must be one of csv or netcdf. Default netcdf.
Example:
```
python run_airpy.py --gee_data fire --region australia --date 2020-01-01 --band LandCover --analysis_type collection --buffer_size 55500 --configs_dir /configs --save_dir /runs --add_time False --save_type netcdf
```
Generates a config file named `config_australia_fire_2020-01-01_buffersize_55500_collection.json` and kicks of the airpy job.
To look at the help file for more information on parameters, run the command ```python run_airpy.py --help```.

#### Processor Modules
The ```processor_modules.py``` script contains the modules that query the GEE api, generate the user-specified buffer, and calculate statistical features from the GEE data product.
It steps through the following:
1. Query GEE image collection
2. Grab image from collection
3. Check if latitude, longitude point is within water bodies (oceans), the Arctic, or Antarctica, if yes, return defaultValue
4. Check that user buffer size is less than allowable buffer size according to GEE max pixel restrictions
    * If no, resample to allowable pixel limit
5. Generate buffer extent, centered on latitude, longitude point
6. Transform data to numpy array
7. Calculate statistics from array (max pixel value, min pixel value, etc.)

## Testing
Tests for each script are stored in the `airpy/tests` folder. `pytest` is used to test scripts in the `airpy` folder via the following command:
```
pytest tests/
```
## Citing
If you found this code useful in your research, please consider giving a star and citation via the following:

Doerksen, Kelsey, "airPy: Generating AI-ready datasets in python for air quality studies using Google Earth Engine", University of Oxford, NASA Jet Propulsion Laboratory, 2023.