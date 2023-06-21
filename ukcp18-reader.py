#------------------------------------------------------------------------------
# PROGRAM: ukcp18-reader.py
#------------------------------------------------------------------------------
# Version 0.2
# 13 May, 2022
# Michael Taylor
# https://patternizer.github.io
# michael DOT a DOT taylor AT uea DOT ac DOT uk
# patternizer AT gmail DOT com
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------
# Dataframe libraries:
import numpy as np
import pandas as pd
import pickle
from datetime import datetime

# Plotting libraries:
import matplotlib    
import matplotlib.pyplot as plt; plt.close('all')
from pandas.plotting import register_matplotlib_converters
from matplotlib import rcParams
register_matplotlib_converters()
import matplotlib.dates as mdates
import seaborn as sns; sns.set()

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

t_start = 1781
t_end = 2100
fontsize = 16
use_dark_theme = False

ukcp18_proj_file1 = 'DATA/plume_plot_rcp26.csv'
ukcp18_proj_file2 = 'DATA/plume_plot_rcp45.csv'
ukcp18_proj_file3 = 'DATA/plume_plot_rcp60.csv'
ukcp18_proj_file4 = 'DATA/plume_plot_rcp85.csv'
ukcp18_obs_file = 'DATA/ukcp18-25km-obs-norwich-20June2023.csv'
cruts_obs_file = 'DATA/cru-ts-norwich-4.07.txt'

#baselinestr = 'baseline_1851_1900'
#baselinestr = 'baseline_1961_1990'
baselinestr = 'baseline_1971_2000'
#baselinestr = 'baseline_1981_2000'

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

#------------------------------------------------------------------------------
# LOAD: UKCP18 Land Probabilistic Projections data --> df_ukcp18_proj (anomalies from 1981-2000)
#------------------------------------------------------------------------------

df1 = pd.read_csv( ukcp18_proj_file1, header=15 ) 
df2 = pd.read_csv( ukcp18_proj_file2, header=15  ) 
df3 = pd.read_csv( ukcp18_proj_file3, header=15  ) 
df4 = pd.read_csv( ukcp18_proj_file4, header=15  ) 

#Index(['Date', 'Mean air temperature anomaly at 1.5m (°C)(5th Percentile)',
#       'Mean air temperature anomaly at 1.5m (°C)(10th Percentile)',
#       'Mean air temperature anomaly at 1.5m (°C)(25th Percentile)',
#       'Mean air temperature anomaly at 1.5m (°C)(50th Percentile)',
#       'Mean air temperature anomaly at 1.5m (°C)(75th Percentile)',
#       'Mean air temperature anomaly at 1.5m (°C)(90th Percentile)',
#       'Mean air temperature anomaly at 1.5m (°C)(95th Percentile)'],
#      dtype='object')

# CONVERT: date strings to datetimes

dates1 = df1[ 'Date' ]
datetimes_ukcp18_proj = [ pd.to_datetime( dates1[i] ) for i in range(len(dates1)) ]

#------------------------------------------------------------------------------
# LOAD: UKCP18 Land observations 25km in Norwich grid cell --> df_ukcp18_obs
#------------------------------------------------------------------------------

f = open( ukcp18_obs_file )
lines = f.readlines()
f.close()
#lines2 = lines[13:]
lines2 = lines[11:]
dates = []
values = []
for i in range( len(lines2) ):
#    if i % 3 == 0:
#        dates.append( lines2[ i ].strip() )
#    elif i % 3 == 2:
#        values.append( float( lines2[ i ].strip().split(',')[1] ) )        
    dates.append( lines2[ i ].strip().split(',')[0] )
    values.append( float( lines2[ i ].strip().split(',')[1] ) )        
datetimes = [ pd.to_datetime( dates[i] ) for i in range(len(dates)) ]

# COMPUTE: normals

df_obs = pd.DataFrame( {'datetime':datetimes, 'obs':values } )
df_obs_baseline = df_obs[ (df_obs['datetime'].dt.year >= 1981) & (df_obs['datetime'].dt.year <= 2000) ]
normals = df_obs_baseline.groupby( df_obs_baseline['datetime'].dt.month)['obs'].mean()

#------------------------------------------------------------------------------
# ALIGN: UKCP18 projections relative to chosen baseline
# NB: projections are calculated relative to 1981-2000 and so we
# need to subtract off the difference between the selected baseline and the 1981-2000 baseline
#------------------------------------------------------------------------------

mu_1851_1900 = np.nanmean( df_obs[(df_obs['datetime'].dt.year>=1851) & (df_obs['datetime'].dt.year<=1900)]['obs'] ) 
mu_1961_1990 = np.nanmean( df_obs[(df_obs['datetime'].dt.year>=1961) & (df_obs['datetime'].dt.year<=1990)]['obs'] ) 
mu_1971_2000 = np.nanmean( df_obs[(df_obs['datetime'].dt.year>=1971) & (df_obs['datetime'].dt.year<=2000)]['obs'] ) 
mu_1981_2000 = np.nanmean( df_obs[(df_obs['datetime'].dt.year>=1981) & (df_obs['datetime'].dt.year<=2000)]['obs'] ) 

if baselinestr == 'baseline_1851_1900':
    mu = mu_1981_2000 - mu_1851_1900
    baseline_start = 1851
    baseline_end = 1900
elif baselinestr == 'baseline_1961_1990':
    mu = mu_1961_1990
    mu = mu_1981_2000 - mu_1961_1990
    baseline_start = 1961
    baseline_end = 1990
elif baselinestr == 'baseline_1971_2000':
    mu = mu_1981_2000 - mu_1971_2000
    baseline_start = 1971
    baseline_end = 2000
elif baselinestr == 'baseline_1981_2000':
    mu = 0
    baseline_start = 1981
    baseline_end = 2000
    
cbarstr = r'Anomaly, $^{\circ}$C (from ' + str(baseline_start) + '-' + str(baseline_end) +')'
ylabelstr = '1.5m Temperature Anomaly (from ' + str(baseline_start) + '-' + str(baseline_end) +'), ' + r'$^{\circ}$C'

# COMPUTE: anomalies

years = df_obs['datetime'].dt.year.unique()
values = df_obs['obs'].values.reshape( int(len(df_obs)/12), 12 )
df_anomalies = pd.DataFrame(columns=['year','1','2','3','4','5','6','7','8','9','10','11','12'])
df_anomalies['year'] = years
for i in range(12):
    df_anomalies[str(i+1)] = values[:,i] - normals.iloc[i]
    
datetimes_ukcp18_obs = df_obs['datetime']
ukcp18_obs = []    
for i in range(len(df_anomalies)):            
   monthly = df_anomalies.iloc[i,1:]
   ukcp18_obs = ukcp18_obs + monthly.to_list()    
ukcp18_obs = np.array( ukcp18_obs )  
ukcp18_obs = pd.Series( ukcp18_obs ).rolling(12).mean()

#------------------------------------------------------------------------------
# LOAD: CRU TS 4.07 Norwich extract --> df_cruts_obs
#------------------------------------------------------------------------------

f = open( cruts_obs_file )
lines = f.readlines()
f.close()
lines2 = lines[7:]
dates = []
values = []
for i in range( len(lines2) ):
    date = lines2[ i ].strip().split()[0] + '-' + lines2[ i ].strip().split()[1] + '-' + '01'
    dates.append( date )
    values.append( float( lines2[ i ].strip().split()[2] ) )        
datetimes_cruts_obs = [ pd.to_datetime( dates[i] ) for i in range(len(dates)) ]

# COMPUTE: anomalies

df_obs = pd.DataFrame( {'datetime':datetimes_cruts_obs, 'obs':values } )
years = df_obs['datetime'].dt.year.unique()
values = df_obs['obs'].values.reshape( int(len(df_obs)/12), 12 )
df_anomalies = pd.DataFrame(columns=['year','1','2','3','4','5','6','7','8','9','10','11','12'])
df_anomalies['year'] = years
for i in range(12):
    df_anomalies[str(i+1)] = values[:,i] - normals.iloc[i]

datetimes_cruts_obs = df_obs['datetime'] + + pd.to_timedelta(15, unit="D")
cruts_obs = []    
for i in range(len(df_anomalies)):            
   monthly = df_anomalies.iloc[i,1:]
   cruts_obs = cruts_obs + monthly.to_list()    
cruts_obs = np.array( cruts_obs )  
cruts_obs = pd.Series( cruts_obs ).rolling(12).mean()

#------------------------------------------------------------------------------
# CONSTRUCT: dataframes
#------------------------------------------------------------------------------

df_ukcp18_obs = pd.DataFrame( { 'datetime':list( datetimes_ukcp18_obs ), 'obs':list( ukcp18_obs ) } )    
df_ukcp18_proj = pd.DataFrame( { 'datetime':list( datetimes_ukcp18_proj ), 
                                'rcp2.6':list( df1['Mean air temperature anomaly at 1.5m (°C)(50th Percentile)'] ), 
                                'rcp4.5':list( df2['Mean air temperature anomaly at 1.5m (°C)(50th Percentile)'] ), 
                                'rcp6.0':list( df3['Mean air temperature anomaly at 1.5m (°C)(50th Percentile)'] ), 
                                'rcp8.5':list( df4['Mean air temperature anomaly at 1.5m (°C)(50th Percentile)'] ),

                                'rcp2.6_p05':list( df1['Mean air temperature anomaly at 1.5m (°C)(5th Percentile)'] ), 
                                'rcp4.5_p05':list( df2['Mean air temperature anomaly at 1.5m (°C)(5th Percentile)'] ), 
                                'rcp6.0_p05':list( df3['Mean air temperature anomaly at 1.5m (°C)(5th Percentile)'] ), 
                                'rcp8.5_p05':list( df4['Mean air temperature anomaly at 1.5m (°C)(5th Percentile)'] ),

                                'rcp2.6_p10':list( df1['Mean air temperature anomaly at 1.5m (°C)(10th Percentile)'] ), 
                                'rcp4.5_p10':list( df2['Mean air temperature anomaly at 1.5m (°C)(10th Percentile)'] ), 
                                'rcp6.0_p10':list( df3['Mean air temperature anomaly at 1.5m (°C)(10th Percentile)'] ), 
                                'rcp8.5_p10':list( df4['Mean air temperature anomaly at 1.5m (°C)(10th Percentile)'] ),

                                'rcp2.6_p90':list( df1['Mean air temperature anomaly at 1.5m (°C)(90th Percentile)'] ), 
                                'rcp4.5_p90':list( df2['Mean air temperature anomaly at 1.5m (°C)(90th Percentile)'] ), 
                                'rcp6.0_p90':list( df3['Mean air temperature anomaly at 1.5m (°C)(90th Percentile)'] ), 
                                'rcp8.5_p90':list( df4['Mean air temperature anomaly at 1.5m (°C)(90th Percentile)'] ),

                                'rcp2.6_p95':list( df1['Mean air temperature anomaly at 1.5m (°C)(95th Percentile)'] ), 
                                'rcp4.5_p95':list( df2['Mean air temperature anomaly at 1.5m (°C)(95th Percentile)'] ), 
                                'rcp6.0_p95':list( df3['Mean air temperature anomaly at 1.5m (°C)(95th Percentile)'] ), 
                                'rcp8.5_p95':list( df4['Mean air temperature anomaly at 1.5m (°C)(95th Percentile)'] ) } )
    
df_cruts_obs = pd.DataFrame( { 'datetime':list( datetimes_cruts_obs ), 'obs':list( cruts_obs ) } )    

#------------------------------------------------------------------------------
# TRIM: UKCP18 proj to start of UKCP18 proj 
#------------------------------------------------------------------------------

df_ukcp18_proj = df_ukcp18_proj[ df_ukcp18_proj.datetime >= '2023-01-16' ].reset_index(drop=True)

#------------------------------------------------------------------------------
# ALIGN: obs and proj to baseline
#------------------------------------------------------------------------------

for col in list( df_ukcp18_proj.columns[1:] ):

    df_ukcp18_proj[col] = df_ukcp18_proj[col].values + mu

df_cruts_obs['obs'] = df_cruts_obs['obs'].values + mu
df_ukcp18_obs['obs'] = df_ukcp18_obs['obs'].values + mu

#------------------------------------------------------------------------------
# PLOT: merged data
#------------------------------------------------------------------------------

fig, ax = plt.subplots( figsize=(15,10) )

plt.fill_between( df_ukcp18_proj['datetime'], 
                 df_ukcp18_proj['rcp8.5_p10'].rolling(12).mean(), 
                 df_ukcp18_proj['rcp8.5_p90'].rolling(12).mean(), color='red', alpha=0.1)
plt.fill_between( df_ukcp18_proj['datetime'], 
                 df_ukcp18_proj['rcp6.0_p10'].rolling(12).mean(), 
                 df_ukcp18_proj['rcp6.0_p90'].rolling(12).mean(), color='brown', alpha=0.1)
plt.fill_between( df_ukcp18_proj['datetime'], 
                 df_ukcp18_proj['rcp4.5_p10'].rolling(12).mean(), 
                 df_ukcp18_proj['rcp4.5_p90'].rolling(12).mean(), color='purple', alpha=0.1)
plt.fill_between( df_ukcp18_proj['datetime'], 
                 df_ukcp18_proj['rcp2.6_p10'].rolling(12).mean(), 
                 df_ukcp18_proj['rcp2.6_p90'].rolling(12).mean(), color='green', alpha=0.1)

plt.plot( df_ukcp18_proj['datetime'], df_ukcp18_proj['rcp8.5'].rolling(12).mean(), ls='-', lw=5, color='red', label='UKCP18 Projections 2023-2100: RCP 8.5 (12m MA) with 10-90% c.i.' )
plt.plot( df_ukcp18_proj['datetime'], df_ukcp18_proj['rcp6.0'].rolling(12).mean(), ls='-', lw=5, color='brown', label='UKCP18 Projections 2023-2100: RCP 6.0 (12m MA) with 10-90% c.i.' )
plt.plot( df_ukcp18_proj['datetime'], df_ukcp18_proj['rcp4.5'].rolling(12).mean(), ls='-', lw=5, color='purple', label='UKCP18 Projections 2023-2100: RCP 4.5 (12m MA) with 10-90% c.i.' )
plt.plot( df_ukcp18_proj['datetime'], df_ukcp18_proj['rcp2.6'].rolling(12).mean(), ls='-', lw=5, color='green', label='UKCP18 Projections 2023-2100: RCP 2.6 (12m MA) with 10-90% c.i.' )
plt.plot( df_ukcp18_obs['datetime'], df_ukcp18_obs['obs'].rolling(12).mean(), '.', ls='-', lw=1, color='grey', label='UKCP18 Observations 1884-2022 (12m MA)' )
#plt.plot( df_cruts_obs['datetime'], df_cruts_obs['obs'].rolling(12).mean(), '.', ls='-', lw=1, color='black', label='CRU TS 4.05 Observations 1901-2020 (12m MA)' )
plt.plot( df_cruts_obs['datetime'], df_cruts_obs['obs'].rolling(12).mean(), '.', ls='-', lw=1, color='black', label='CRU TS 4.07 Observations 1901-2022 (12m MA)' )

plt.legend(loc='upper left', fontsize=fontsize)
plt.title('Land Observations & UKCP18 Probabilistic Projections at 25 km for UK National Grid Cells centered on Norwich', fontsize=fontsize )
ax.tick_params(labelsize=fontsize)    
ax.set_xlabel('Year', fontsize=fontsize)
#ax.set_ylabel('1.5m Temperature Anomaly (from 1981-2000), $^{\circ}C$', fontsize=fontsize)
ax.set_ylabel(ylabelstr, fontsize=fontsize)
fig.tight_layout()
plt.savefig('ukcp18-projections-tg1907' + '-' + baselinestr, dpi=300)
plt.close('all')

#------------------------------------------------------------------------------
# SAVE: dataframes
#------------------------------------------------------------------------------

df_ukcp18_proj.to_pickle('df_ukcp18_proj_norwich.pkl', compression='bz2')
df_ukcp18_obs.to_pickle('df_ukcp18_obs_norwich.pkl', compression='bz2')
df_cruts_obs.to_pickle('df_cruts_obs_norwich.pkl', compression='bz2')

#------------------------------------------------------------------------------
print('** END')

