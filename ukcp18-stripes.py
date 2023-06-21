#! /usr/bin python

#------------------------------------------------------------------------------
# PROGRAM: ukcp18-stripes.py
#------------------------------------------------------------------------------
# Version 0.2
# 21 June 2023
# Michael Taylor
# https://patternizer.github.io
# michael DOT a DOT taylor AT uea DOT ac DOT uk
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------

# Dataframe libraries:
import numpy as np
import pandas as pd
import xarray as xr

# Datetime libraries:
from datetime import datetime
import nc_time_axis
import cftime
from cftime import num2date, DatetimeNoLeap

# Plotting libraries:
import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt; plt.close('all')
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable
from matplotlib import rcParams
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Statistics libraries:
from scipy import stats

# Silence library version notifications
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

fontsize = 10
barwidthfraction = 1.0
cmax_fixed = 2 # for HadCRUT5 use 0.7 for global mean air temperatures
cmin_fixed = -1 # for HadCRUT5 use 0.7 for global mean air temperatures

use_dark_theme = True
override_cmax = False
use_overlay_timeseries = True
use_overlay_colorbar = True
 
projectionstr = 'RCP26'
#projectionstr = 'RCP45'
#projectionstr = 'RCP60'
#projectionstr = 'RCP85'

#ipcc_rgb_txtfile = np.loadtxt("DATA/temp_div.txt") # IPCC AR6 temp div colormap file
#cmap = mcolors.LinearSegmentedColormap.from_list('colormap', ipcc_rgb_txtfile) # ipcc_colormap
#cmap = plt.cm.get_cmap('RdBu_r')
#cmap = plt.cm.get_cmap('bwr')

# showyourstripes.info colormap:
#------------------------------
# the colors in this colormap come originally from http://colorbrewer2.org
# the 8 more saturated colors from the 9 blues / 9 reds

#cmap = ListedColormap([
#    '#08306b', '#08519c', '#2171b5', '#4292c6',
#    '#6baed6', '#9ecae1', '#c6dbef', '#deebf7',
#    '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a',
#    '#ef3b2c', '#cb181d', '#a50f15', '#67000d',
#])        

colorlist = [
    '#08306b', '#08519c', '#2171b5', '#4292c6',
    '#6baed6', '#9ecae1', '#c6dbef', '#deebf7',
    '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a',
    '#ef3b2c', '#cb181d', '#a50f15', '#67000d',
]        
cmap = LinearSegmentedColormap.from_list('my_colormap', colorlist, N=256)

#------------------------------------------------------------------------------
# DARK THEME
#------------------------------------------------------------------------------

if use_dark_theme == True:
    
    matplotlib.rcParams['text.usetex'] = False
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['Avant Garde', 'Lucida Grande', 'Verdana', 'DejaVu Sans' ]
    plt.rc('text',color='white')
    plt.rc('lines',color='white')
    plt.rc('patch',edgecolor='white')
    plt.rc('grid',color='lightgray')
    plt.rc('xtick',color='white')
    plt.rc('ytick',color='white')
    plt.rc('axes',labelcolor='white')
    plt.rc('axes',facecolor='black')
    plt.rc('axes',edgecolor='lightgray')
    plt.rc('figure',facecolor='black')
    plt.rc('figure',edgecolor='black')
    plt.rc('savefig',edgecolor='black')
    plt.rc('savefig',facecolor='black')
    
else:

    matplotlib.rcParams['text.usetex'] = False
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['Avant Garde', 'Lucida Grande', 'Verdana', 'DejaVu Sans' ]
    plt.rc('text',color='black')
    plt.rc('lines',color='black')
    plt.rc('patch',edgecolor='black')
    plt.rc('grid',color='lightgray')
    plt.rc('xtick',color='black')
    plt.rc('ytick',color='black')
    plt.rc('axes',labelcolor='black')
    plt.rc('axes',facecolor='white')    
    plt.rc('axes',edgecolor='black')
    plt.rc('figure',facecolor='white')
    plt.rc('figure',edgecolor='white')
    plt.rc('savefig',edgecolor='white')
    plt.rc('savefig',facecolor='white')

# Calculate current time

now = datetime.now()
currentdy = str(now.day).zfill(2)
currentmn = str(now.month).zfill(2)
currentyr = str(now.year)
titletime = str(currentdy) + '/' + currentmn + '/' + currentyr
        
#-----------------------------------------------------------------------------
# LOAD: dataframes
#-----------------------------------------------------------------------------

df_ukcp18_proj = pd.read_pickle('OUT/df_ukcp18_proj_norwich.pkl', compression='bz2')    
df_ukcp18_obs = pd.read_pickle('OUT/df_ukcp18_obs_norwich.pkl', compression='bz2')    
df_cruts_obs = pd.read_pickle('OUT/df_cruts_obs_norwich.pkl', compression='bz2')    

# RESET: index to datetime

df_ukcp18_proj = df_ukcp18_proj.groupby('datetime').mean()
df_ukcp18_obs = df_ukcp18_obs.groupby('datetime').mean()
df_cruts_obs = df_cruts_obs.groupby('datetime').mean()

# RESAMPLE: to yearly

df_ukcp18_proj = df_ukcp18_proj.resample('12M').mean()
df_ukcp18_obs = df_ukcp18_obs.resample('12M').mean()
df_cruts_obs = df_cruts_obs.resample('12M').mean()

reference = np.nanmean( df_ukcp18_obs[ (df_ukcp18_obs.index.year >= 1971) & (df_ukcp18_obs.index.year <= 2000) ] )
obs = pd.Series(df_ukcp18_obs.obs.values, index=df_ukcp18_obs.index.year)

# SHOW YOUR STRIPES: colour range

if override_cmax == True:
    cmax = cmax_fixed
else:
    cmax = np.nanstd( df_ukcp18_obs[ (df_ukcp18_obs.index.year >= 1901) & (df_ukcp18_obs.index.year <= 2000) ] ) * 2.6

#------------------------------------------------------------------------------
# MERGE: dataframes
#------------------------------------------------------------------------------

x = list(df_ukcp18_obs.index) + list(df_ukcp18_proj.index)
if projectionstr == 'RCP26':
    projection = 'RCP 2.6'
    y = list(df_ukcp18_obs.obs) + list(df_ukcp18_proj['rcp2.6'])
elif projectionstr == 'RCP45':
    projection = 'RCP 4.5'
    y = list(df_ukcp18_obs.obs) + list(df_ukcp18_proj['rcp4.5'])
elif projectionstr == 'RCP60':
    projection = 'RCP 6.0'
    y = list(df_ukcp18_obs.obs) + list(df_ukcp18_proj['rcp6.0'])
elif projectionstr == 'RCP85':
    projection = 'RCP 8.5'    
    y = list(df_ukcp18_obs.obs) + list(df_ukcp18_proj['rcp8.5'])    

x = np.array( [x[i].year for i in range(len(x))] )
y = np.array(y)
z = np.array(len(y)*[1.0])
                     
proj = pd.Series(y, index=x)

#------------------------------------------------------------------------------
# RESCALE: colormap to max = cbar_max ( provide )
#------------------------------------------------------------------------------
    
y_norm_raw = ( y-np.nanmin(y) ) / ( np.nanmax(y) - np.nanmin(y) )
y_ref = list(df_ukcp18_obs.obs) + list(df_ukcp18_proj['rcp2.6'])
colorscalefactor = cmax / np.nanmax(y_ref)
y_min = np.nanmin(y_ref) * colorscalefactor
y_max = np.nanmax(y_ref) * colorscalefactor
y_norm = (y - y_min) / (y_max - y_min) 
#maxval = y_max
#minval = y_min
maxval = cmax_fixed
minval = cmin_fixed
colors = cmap( y_norm ) 
norm = mcolors.TwoSlopeNorm( vmin=minval, vcenter=0.0, vmax=maxval) 
sm = ScalarMappable( cmap=cmap, norm=norm )
sm.set_array([])

#==============================================================================
# PLOT: climate stripes
#==============================================================================
 
# PLOT: stripes (without overlays) from 1901-2022 with showyourstripes.info method
                           
figstr = 'climate-stripes' + '-' + 'A' + '.png'
titlestr = 'UKCP18 Land Observations 1884-2022 at 25km centered on Norwich'
cbarstr = 'Anomaly ( from 1971-2000 ), ' + r'$^{\circ}$C'

fig, ax = plt.subplots( figsize=(15,5) ); ax.axis('off')        
col = PatchCollection([
    Rectangle((Y, 0), 1, 1)
    for Y in range(obs.index[0], obs.index[-1] + 1)
])
col.set_array(obs)
col.set_cmap(cmap)
col.set_clim(reference - cmax, reference + cmax)
ax.add_collection(col)
ax.set_ylim(0, 1)
ax.set_xlim(obs.index[0], obs.index[-1])
plt.savefig( figstr, dpi=300, bbox_inches='tight' )
plt.close(fig)

# PLOT: stripes with colorbar and title from 1901-2022 - using my bar chart method

figstr = 'climate-stripes' + '-' + 'B' + '.png'
titlestr = 'UKCP18 Land Observations 1884-2022 at 25km centered on Norwich'
cbarstr = 'Anomaly ( from 1971-2000 ), ' + r'$^{\circ}$C'

fig, ax = plt.subplots( figsize=(15,5) ); ax.axis('off')
plt.bar( x+0.5, z, color=colors, width=1 )   
plt.ylim(0,1)        
ax.set_xlim(obs.index[0], obs.index[-1])
ax.axis('off')        
if use_overlay_timeseries == True: 
    plt.plot( np.arange( len(x) ), y_norm_raw, color='black', ls='-', lw=1 )            
if use_overlay_colorbar == True:
    cbar = plt.colorbar( sm, shrink=0.5, extend='both' )
    cbar.set_label( cbarstr, rotation=270, labelpad=25, fontsize=fontsize )
plt.title( titlestr, fontsize=fontsize )          
plt.tick_params(labelsize=fontsize)    
plt.tight_layout()
plt.savefig( figstr, dpi=300, bbox_inches='tight' )
plt.close(fig)

# PLOT: stripes with colorbar and title from 1901-2100 with RCP projection - using my bar chart method

figstr = 'climate-stripes' + '-' + projectionstr + '.png'
titlestr = 'UKCP18 Land Observations + Probabilistic Projections 1884-2100 at 25km centered on Norwich: ' + projection
cbarstr = 'Anomaly ( from 1971-2000 ), ' + r'$^{\circ}$C'

fig, ax = plt.subplots( figsize=(15,5) ); ax.axis('off')
plt.bar( x+0.5, z, color=colors, width=1 )   
plt.ylim(0,1)    
ax.set_xlim(proj.index[0], proj.index[-1])    
ax.axis('off')        
if use_overlay_timeseries == True: 
    plt.step( x, y_norm_raw, where='post', color='black', ls='-', lw=1 )            
if use_overlay_colorbar == True:
    cbar = plt.colorbar( sm, shrink=0.5, extend='both' )
    cbar.set_label( cbarstr, rotation=270, labelpad=25, fontsize=fontsize )
plt.title( titlestr, fontsize=fontsize )          
plt.tick_params(labelsize=fontsize)    
plt.tight_layout()
plt.savefig( figstr, dpi=300, bbox_inches='tight' )
plt.close(fig)

#------------------------------------------------------------------------------
print('** END')
