![image](https://github.com/patternizer/ukcp18-norwich/blob/main/PLOTS/ukcp18-projections-tg1907-baseline_1971_2000.png)
![image](https://github.com/patternizer/ukcp18-norwich/blob/main/PLOTS/climate-stripes-A.png)
![image](https://github.com/patternizer/ukcp18-norwich/blob/main/PLOTS/climate-stripes-B.png)

# ukcp18-norwich

Python codebase to plot land observations and RCP2.6, RCP4.5, RCP6.0 and RCP8.5 probabilistic projections from [UKCP18](https://ukclimateprojections-ui.metoffice.gov.uk/ui/home) extracted at 25km resolution for Norwich and plot associated anomalies from 1971-2000 following Professor Ed Hawkins' prescription for warming stripes at [showyourstripes.info](https://showyourstripes.info).

## Contents

* `ukcp18-reader.py` - python data reader code that organises observations and projections extracted into a pandas dataframe and generates the associated plume plot
* `ukcp18-stripes.py` - python code to convert the observation and projection data into anomalies from 1971-2000 and generate a separate plot of climate stripes for each projection

The first step is to clone the latest ukcp18-norwich code and step into the check out directory: 

    $ git clone https://github.com/patternizer/ukcp18-norwich.git
    $ cd ukcp18-norwich

### Usage

The code was tested locally in a Python 3.8.11 virtual environment.

    $ python ukcp18-reader.py
    $ python ukcp18-stripes.py
    
Observations and projection source data extracted from UKCP18 and CRU TS 4.07 for Norwich are available on request.

## License

The code is distributed under terms and conditions of the [Open Government License](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Contact information

* [Michael Taylor](michael.a.taylor@uea.ac.uk)


