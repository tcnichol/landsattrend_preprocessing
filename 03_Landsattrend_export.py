import ee#, eemont
import sys

ee.Authenticate(auth_mode="appdefault")
ee.Initialize()

import geemap
from importlib import reload
import geopandas as gpd

from modules import high_level_functions
from modules import utils_Landsat_SR as utils_LS
from modules import ms_indices as indices
from modules import configs, utils_string


def create_dem_data():
    # Create DEM data from various sources
    alosdem = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2").mosaic().select(['DSM'], ['elevation'])
    alosdem = alosdem.addBands(ee.Terrain.slope(alosdem)).select(['elevation', 'slope']).toFloat()

    nasadem = ee.Image("NASA/NASADEM_HGT/001").select(['elevation'])
    nasadem = nasadem.addBands(ee.Terrain.slope(nasadem)).select(['elevation', 'slope']).toFloat()

    arcticDEM = ee.Image("UMN/PGC/ArcticDEM/V3/2m_mosaic").select(['elevation'])
    arcticDEM = arcticDEM.addBands(ee.Terrain.slope(arcticDEM)).select(['elevation', 'slope']).toFloat()

    dem = ee.ImageCollection([arcticDEM, alosdem, nasadem]).mosaic()
    return dem

def run_preprocess(config_trend, crs=None):

    config_trend['geom'] = geom
    trend = high_level_functions.runTCTrend(config_trend)
    data = trend['data']

    #### setup data
    dem = create_dem_data()
    data_export = data.addBands(dem).toFloat().select(data_cols)

    ### Export
    task = ee.batch.Export.image.toDrive(
        image=data_export,
        description=f'trendimage_Z056-Kolyma_{X_MIN}_{Y_MIN}',
        folder='PDG_Trend_upload',
        fileNamePrefix=f'trendimage_Z056-Kolyma_{X_MIN}_{Y_MIN}',
        crs='EPSG:32656',
        region=geom,
        scale=30,
        maxPixels=1e12)
    task.start()

data_cols = ['TCB_slope',
             'TCB_offset',
             'TCG_slope',
             'TCG_offset',
             'TCW_slope',
             'TCW_offset',
             'NDVI_slope',
             'NDVI_offset',
             'NDMI_slope',
             'NDMI_offset',
             'NDWI_slope',
             'NDWI_offset',
             'elevation',
             'slope']

# PROPERTIES
# SET METADATA PARAMETERS
MAXCLOUD = 70
STARTYEAR = 2000
ENDYEAR = 2020
STARTMONTH = 7
ENDMONTH = 8
SCALE = 30
X_MIN = 150
Y_MIN = 68

# image metadata Filters
config_trend = {
  'date_filter_yr' : ee.Filter.calendarRange(STARTYEAR, ENDYEAR, 'year'),
  'date_filter_mth' : ee.Filter.calendarRange(STARTMONTH, ENDMONTH, 'month'),
  'meta_filter_cld' : ee.Filter.lt('CLOUD_COVER', MAXCLOUD),
  'select_bands_visible' : ["B1", "B2","B3","B4"],
  'select_indices' : ["TCB", "TCG", "TCW", "NDVI", "NDMI", "NDWI"],
  'select_TCtrend_bands' : ["TCB_slope", "TCG_slope", "TCW_slope"],
  'geom' : None
}

geom = ee.Geometry.Rectangle(coords=[X_MIN, Y_MIN, X_MIN+6, Y_MIN+1], proj=ee.Projection('EPSG:4326'))

config_trend['geom'] = geom
trend = high_level_functions.runTCTrend(config_trend)
data = trend['data']

dem = create_dem_data()

data_export = data.addBands(dem).toFloat().select(data_cols)

task = ee.batch.Export.image.toDrive(
    image=data_export,
    description=f'trendimage_Z056-Kolyma_{X_MIN}_{Y_MIN}',
    folder='PDG_Trend_upload',
    fileNamePrefix=f'trendimage_Z056-Kolyma_{X_MIN}_{Y_MIN}',
    crs='EPSG:32656',
    region=geom,
    scale=30,
    maxPixels=1e12)
task.start()

# PROPERTIES
# SET METADATA PARAMETERS
MAXCLOUD = 70
STARTYEAR = 2000
ENDYEAR = 2020
STARTMONTH = 7
ENDMONTH = 8
SCALE = 30

config_trend = {
  'date_filter_yr' : ee.Filter.calendarRange(STARTYEAR, ENDYEAR, 'year'),
  'date_filter_mth' : ee.Filter.calendarRange(STARTMONTH, ENDMONTH, 'month'),
  'meta_filter_cld' : ee.Filter.lt('CLOUD_COVER', MAXCLOUD),
  'select_bands_visible' : ["B1", "B2","B3","B4"],
  'select_indices' : ["TCB", "TCG", "TCW", "NDVI", "NDMI", "NDWI"],
  'select_TCtrend_bands' : ["TCB_slope", "TCG_slope", "TCW_slope"],
  'geom' : None
}

X_SIZE = 3
Y_SIZE = 1

for Y_MIN in range(62, 67):
    for X_MIN in range(150, 159, 3):
        config_trend['geom'] = geom = ee.Geometry.Rectangle(coords=[X_MIN, Y_MIN, X_MIN+X_SIZE, Y_MIN+Y_SIZE], proj=ee.Projection('EPSG:4326'))
        run_preprocess(config_trend)