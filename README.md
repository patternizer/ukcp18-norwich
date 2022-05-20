![image](https://github.com/patternizer/ukcp18-norwich/blob/main/ukcp18-projections-tg1907.png)
![image](https://github.com/patternizer/ukcp18-norwich/blob/main/climate-stripes-RCP26.png)
![image](https://github.com/patternizer/ukcp18-norwich/blob/main/climate-stripes-RCP45.png)
![image](https://github.com/patternizer/ukcp18-norwich/blob/main/climate-stripes-RCP60.png)
![image](https://github.com/patternizer/ukcp18-norwich/blob/main/climate-stripes-RCP85.png)

# ukcp18-norwich

Python codebase to plot observations and RCP2.6, RCP4.5, RCP6.0 and RCP8.5 land probabilistic projections from [UKCP18](https://ukclimateprojections-ui.metoffice.gov.uk/ui/home) extracted at 25km resolution for Norwich and plot assiciated anomalies from 1981-2000 as climate stripes

## Contents

* `ukcp18-reader.py` - python data reader code that organises observations and projections extracted into a pandas dataframe and generates the associated plume plot
* `ukcp18-stripes.py` - python code to convert the observation and projection data into anomalies from 1981-2000 and generate a separate plot of climate stripes for each projection

The first step is to clone the latest ukcp18-norwich code and step into the check out directory: 

    $ git clone https://github.com/patternizer/ukcp18-norwich.git
    $ cd ukcp18-norwich

### Usage

The code was tested locally in a Python 3.8.11 virtual environment.

    $ python ukcp18-reader.py
    $ python ukcp18-stripes.py
    
Observations and projection source data extracted from UKCP18 and CRU TS 4.05 are available on request.

## License

The code is distributed under terms and conditions of the [Open Government License](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Contact information

* [Michael Taylor](michael.a.taylor@uea.ac.uk)



