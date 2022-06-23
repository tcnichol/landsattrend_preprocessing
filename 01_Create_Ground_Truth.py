#%% md

## Landsattrend ground truth creation

#%%

import ee#, eemont
#ee.Authenticate()
ee.Initialize()

#%%

import geemap
from importlib import reload
import geopandas as gpd
import numpy as np
import tqdm
import pandas as pd

# %%

from modules import high_level_functions
from modules import utils_Landsat_SR as utils_LS
from modules import ms_indices as indices
from modules import configs, utils_string


# %%

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


#%%

# PROPERTIES
# SET METADATA PARAMETERS
MAXCLOUD = 70
STARTYEAR = 2000
ENDYEAR = 2014
STARTMONTH = 7
ENDMONTH = 8
SCALE = 30


#%%

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
#------ RUN FULL PROCESS FOR ALL REGIONS IN LOOP ------------------------------
#Map.addLayer(imageCollection, {}, 'TCVIS')

#%%

geometry = ee.FeatureCollection(ee.FeatureCollection('users/ingmarnitze/Ground_Truth/GlobPF_CCI/gt_v03'))

#%%

FC_size = geometry.size().getInfo()

#%% md

#### Filter to n features
# * get size of geom
# * necessary for reduction

#%%

geom = ee.FeatureCollection(geometry.toList(count=10, offset=100))

#%%

def get_df_from_fc_sample(fc, config_trend):
    geom_buf = fc.geometry().buffer(200)
    config_trend['geom'] = geom_buf
    trend = high_level_functions.runTCTrend(config_trend)
    im = trend['data']
    bands = im.bandNames().getInfo()[1:]
    fcout = im.select(bands).sampleRegions(collection=fc,
                                       scale=30,
                                      )
    return geemap.ee_to_pandas(fcout)

offset = np.arange(0, FC_size, 10)

#%%

df_list = []
for i in tqdm.tqdm_notebook(offset):
    # check here for loop solution
    geom = ee.FeatureCollection(geometry.toList(count=10, offset=int(i)))
    df_list.append(get_df_from_fc_sample(geom, config_trend))

#%%

df = pd.concat(df_list)

#%%

df.to_csv('train_data.csv')

#%% md

### DEM values


#%%

dem = create_dem_data()

#%%

fcel = dem.select(['elevation', 'slope']).sampleRegions(collection=geometry,
                                       scale=30,
                                      )

#%%

df_el = geemap.ee_to_pandas(fcel)

#%%

df_el.to_csv('train_dem.csv')