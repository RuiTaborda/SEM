Prerequisites to download ERA5 data through CDS API
===================================================

1 - Install the CDS API and xarray packages
-------------------------------------------

    In Anaconda Prompt execute the following commands:

    .. code-block:: bash

        conda config --add channels conda-forge
        conda install cdsapi
        conda install xarray dask netCDF4 bottleneck


2 - Install the CDS API key
---------------------------

    a.	Log in CDS (https://cds.climate.copernicus.eu/user/login)

    b.	 Go to https://cds.climate.copernicus.eu/api-how-to and create a file “.cdsapirc” using the two lines of code displayed in the page. 
    The file structure should be similar to the one below. 

    .. code-block:: bash

        url: https://cds.climate.copernicus.eu/api/v2
        key: xxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

    c. The file should be located in C:/Users/username/ for example in “C:/Users/rui”.



    .. note::
        in non english systems the folder name can be displayed in a diferent way (see figure)

        .. image:: ../_static/images/cdapirc-folder.png
        
    
