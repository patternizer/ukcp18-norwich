#! /usr/bin python

#------------------------------------------------------------------------------
# PROGRAM: ukcp18-stripes.py
#------------------------------------------------------------------------------
# Version 0.1
# 13 May 2022
# Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
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
cbar_max = 4.0
barwidthfraction = 1.0

use_dark_theme = True
use_data_cmax = False
use_overlay_timeseries = False
use_overlay_colorbar = True
 
projectionstr = 'RCP26'
#projectionstr = 'RCP45'
#projectionstr = 'RCP60'
#projectionstr = 'RCP85'

ipcc_rgb_txtfile = np.loadtxt("DATA/temp_div.txt") # IPCC AR6 temp div colormap file
cmap = mcolors.LinearSegmentedColormap.from_list('colormap', ipcc_rgb_txtfile) # ipcc_colormap
#cmap = plt.cm.get_cmap('RdBu_r')
#cmap = plt.cm.get_cmap('bwr')
        
#------------------------------------------------------------------------------
# DARK THEME
#------------------------------------------------------------------------------

if use_dark_theme == True:
    
    matplotlib.rcParams['text.usetex'] = False
#    rcParams['font.family'] = ['DejaVu Sans']
#    rcParams['font.sans-serif'] = ['Avant Garde']
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
#    rcParams['font.family'] = ['DejaVu Sans']
#    rcParams['font.sans-serif'] = ['Avant Garde']
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

df_ukcp18_proj = pd.read_pickle('df_ukcp18_proj_norwich.pkl', compression='bz2')    
df_ukcp18_obs = pd.read_pickle('df_ukcp18_obs_norwich.pkl', compression='bz2')    
df_cruts_obs = pd.read_pickle('df_cruts_obs_norwich.pkl', compression='bz2')    

# TRIM: to start at 1901

df_ukcp18_obs = df_ukcp18_obs[ df_ukcp18_obs.datetime.dt.year >= 1901 ]

# RESET: index to datetime

df_ukcp18_proj = df_ukcp18_proj.groupby('datetime').mean()
df_ukcp18_obs = df_ukcp18_obs.groupby('datetime').mean()
df_cruts_obs = df_cruts_obs.groupby('datetime').mean()

# RESAMPLE: to yearly

df_ukcp18_proj = df_ukcp18_proj.resample('12M').mean()
df_ukcp18_obs = df_ukcp18_obs.resample('12M').mean()
df_cruts_obs = df_cruts_obs.resample('12M').mean()

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

y = np.array(y)
z = np.array(len(y)*[1.0])

#------------------------------------------------------------------------------
# RESCALE: colormap to max = cbar_max ( provide )
#------------------------------------------------------------------------------

if use_data_cmax == True:    
    cbar_max = np.nanmax(y)
else:
    cbar_max = cbar_max
    
y_norm_raw = ( y-np.nanmin(y) ) / ( np.nanmax(y) - np.nanmin(y) )
y_ref = list(df_ukcp18_obs.obs) + list(df_ukcp18_proj['rcp2.6'])

def rescale_colormap(cbar_max):
    
    colorscalefactor = cbar_max / np.nanmax(y_ref)
    y_min = np.nanmin(y_ref) * colorscalefactor
    y_max = np.nanmax(y_ref) * colorscalefactor
    y_norm = (y - y_min) / (y_max - y_min) 
    maxval = y_max
    minval = y_min
    colors = cmap( y_norm ) 
    norm = mcolors.TwoSlopeNorm( vmin=minval, vcenter=0.0, vmax=maxval) 
    sm = ScalarMappable( cmap=cmap, norm=norm )
    sm.set_array([])

    return colors, norm, sm

colors, norm, sm = rescale_colormap(cbar_max)

#==============================================================================
# PLOT: climate stripes
#==============================================================================
                            
figstr = 'climate-stripes' + '-' + projectionstr + '.png'
titlestr = 'UKCP18 Land Observations + Probabilistic Projections 1901-2100 at 25km centered on Norwich: ' + projection
cbarstr = r'Anomaly, $^{\circ}$C ( from 1981-2000 )'
        
fig, ax = plt.subplots( figsize=(15,5) ); ax.axis('off')
plt.bar( np.arange( len(x) ), z, color=colors, width=barwidthfraction )   
plt.ylim(0,1)        
ax.axis('off')        
if use_overlay_timeseries == True: 
    plt.plot( np.arange( len(x) ), y_norm_raw, color='black', ls='-', lw=1 )            
if use_overlay_colorbar == True:
    cbar = plt.colorbar( sm, shrink=0.5, extend='both' )
    cbar.set_label( cbarstr, rotation=270, labelpad=25, fontsize=fontsize )
#fig.suptitle( titlestr, fontsize=fontsize )          
plt.title( titlestr, fontsize=fontsize )          
plt.tick_params(labelsize=fontsize)    
plt.tight_layout()
plt.savefig( figstr, dpi=300 )
plt.close(fig)

#------------------------------------------------------------------------------
print('** END')
