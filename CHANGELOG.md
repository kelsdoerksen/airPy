# Changelog

## v1.1.0 (09/07/2024)

### Features
- Added support for Global Human Settlement Layer dataset
- Added support for Global Human Modification dataset
- Added functionality to specify band of interest
- Added functionality to calculate built percentage for GHSL
- Added support to provide custom lat, lon points for querying
- Added functionality to save features as CSV
- Added functionality to check for allowable buffer size based on data resolution
- Added functionality to calculate new resampling resolution if buffer size > allowable
- Added functionality to check for point over open oceans or within Arctic/Antarctica

### Tests
- Added new tests to support GHSL and GHM modules
- Added new tests to support ocean, arctic, antarctica query
- Added new test to check allowable buffer size
- Added new test to check resampling resolution

### Fixes
- Updated FIRE_LC to have corrected dictionary representing classes defined in FireCCI51: MODIS Fire_cci Burned Area Pixel Product, Version 5.1  GEE for crop_rain, mosaic_crop and mosaic_veg