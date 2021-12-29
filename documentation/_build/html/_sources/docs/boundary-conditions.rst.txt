####################
Boundary conditions
####################


**************
Offshore waves
**************

Offshore wave conditions should be given as a wavetimeseries objet. Data sources include offshore wave buoys and model data. To simulate relative long periods, hindcast data are one of the best options, so the procedure is detailed below.

Using ERA5 based ocean wave hindcast
====================================

`ERA5 <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5>`_ is the fifth generation ECMWF (European Centre for Medium-Range Weather Forecasts) atmospheric reanalysis of the global climate and have a horizontal resolution of 0.5 :math:`^{\circ}` x 0.5 :math:`^{\circ}` for waves.

.. warning::

   Prior to download the wave data make sure that the CDS API and xarray package are properly installed.

   See :doc:`/docs/ERA5-prerequisites` for details.


1 - Data selection and downloading
----------------------------------

   The best way to navigate to the available data is to open `ERA5 download page <https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form>`_ and in the *download tab* select the desired data. In the bottom of the same panel click on the *Show API request* button and copy the code to a python file. 
   
.. topic:: Example

   Example of a code for downloading a grib file with wave significant height, peak wave period period and mean direction, for a region offshore mainland Portugal, from 1979 to 2021 at 0 and 12 hours. Data will be download to a file named *download.grib*.

   .. code-block:: python

      c = cdsapi.Client()

      c.retrieve(
         'reanalysis-era5-single-levels',
         {
            'product_type': 'reanalysis',
            'variable': [
                  'mean_wave_direction', 'peak_wave_period', 'significant_height_of_combined_wind_waves_and_swell',
            ],
            'year': [
                  '1979', '1980', '1981',
                  '1982', '1983', '1984',
                  '1985', '1986', '1987',
                  '1988', '1989', '1990',
                  '1991', '1992', '1993',
                  '1994', '1995', '1996',
                  '1997', '1998', '1999',
                  '2000', '2001', '2002',
                  '2003', '2004', '2005',
                  '2006', '2007', '2008',
                  '2009', '2010', '2011',
                  '2012', '2013', '2014',
                  '2015', '2016', '2017',
                  '2018', '2019', '2020',
                  '2021',
            ],
            'month': [
                  '01', '02', '03',
                  '04', '05', '06',
                  '07', '08', '09',
                  '10', '11', '12',
            ],
            'day': [
                  '01', '02', '03',
                  '04', '05', '06',
                  '07', '08', '09',
                  '10', '11', '12',
                  '13', '14', '15',
                  '16', '17', '18',
                  '19', '20', '21',
                  '22', '23', '24',
                  '25', '26', '27',
                  '28', '29', '30',
                  '31',
            ],
            'time': [
                  '00:00', '12:00',
            ],
            'area': [
                  40, -10, 38,
                  -9,
            ],
            'format': 'netcdf',
         },
         'download.nc')
  
   Output on pyton console

   .. code-block:: bash

      2020-05-15 19:26:36,562 INFO Welcome to the CDS
      2020-05-15 19:26:36,567 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/reanalysis-era5-single-levels
      2020-05-15 19:26:39,209 INFO Request is queued
      2020-05-15 19:26:44,134 INFO Request is running
      2020-05-15 19:26:52,695 INFO Request is completed
      2020-05-15 19:26:52,697 INFO Downloading http://136.156.133.25/cache-compute-0008/cache/data5/adaptor.mars.internal-1589567202.6668167-11772-35-ea112760-394c-4211-a63e-bdfd778e233c.grib to download.grib (33.8K)
      2020-05-15 19:26:52,876 INFO Download rate 190.7K/s

2  - Loading and converting the data to a wavetimeseries

