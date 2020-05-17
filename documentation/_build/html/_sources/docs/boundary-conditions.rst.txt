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

   Example of a code for downloading a grib file with wave significant height, mean period and mean direction, for a region offshore mainland Portugal, for all available hours of day 01-April-2020. Data will be download to a file named *download.grib*.

   .. code-block:: python

      import cdsapi
      c = cdsapi.Client()
      c.retrieve(
         'reanalysis-era5-single-levels',
         {
            'product_type': 'reanalysis',
            'format': 'grib',
            'variable': [
                  'mean_wave_direction', 'mean_wave_period', 'significant_height_of_combined_wind_waves_and_swell',
            ],
            'year': '2020',
            'month': '04',
            'day': '01',
            'time': [
                  '00:00', '01:00', '02:00',
                  '03:00', '04:00', '05:00',
                  '06:00', '07:00', '08:00',
                  '09:00', '10:00', '11:00',
                  '12:00', '13:00', '14:00',
                  '15:00', '16:00', '17:00',
                  '18:00', '19:00', '20:00',
                  '21:00', '22:00', '23:00',
            ],
            'area': [
                  43, -13, 36,
                  -7,
            ],
         },
         'download.grib')
  
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

