from netCDF4 import Dataset
from os import listdir
import pandas as pd
import numpy as np
import warnings

# silence warnings
warnings.filterwarnings("ignore")


class netCDF4_Average:

    def __init__(self, directory):
        """ constructor """

        self.dir = directory

        # list of properties to average
        self.vars = ['accumulated_srad', 'average_10m_windspeed',
                     'maximum_10m_windspeed', 'maximum_relative_humidity',
                     'maximum_temperature', 'minimum_relative_humidity',
                     'minimum_temperature']

        # get file names and load the data to memory
        self.get_files()

        # in case a loading problem happened
        if not self.files:
            raise FileNotFoundError("No .nc file was found is this directory")

        self.loadData()

    def get_files(self):
        """ getting the paths to all netCDF4 files """

        files = []
        for folder in listdir(self.dir):

            path = f'./{self.dir}/{folder}'
            nc = [f for f in listdir(path) if '.nc' in f]

            if not nc:
                continue
            else:
                files.append(f'{path}/{nc[0]}')

        self.files = files

    def loadData(self):
        """ actually loading the files """

        self.data = [Dataset(f, 'r') for f in self.files]

    def compute_average(self, verbose=True, step=1):
        """ compute the average values of all data files """

        # assuming all files have the same shape
        sample = self.data[0]
        rows, cols = sample['latitude'].shape

        # define a csv
        df = pd.DataFrame(columns=list(sample.variables.keys()))

        # define  netCDF4
        f = f'Netcdf_Averaging_Work_Monthly_{self.dir}.nc'
        ncfile = Dataset(f, 'w', format='NETCDF4_CLASSIC')

        # create dimensions
        ncfile.createDimension('lat', rows // step + 1)
        ncfile.createDimension('lon', cols // step + 1)

        # define variables
        for var in sample.variables.keys():

            if len(sample[var].shape) == 2:
                ncfile.createVariable(var, 'd', ('lat', 'lon'))

            elif sample[var].shape == ():
                ncfile.createVariable(var, 'd', ())

        print('Total size of the map:', int(rows * cols / step ** 2))

        if verbose:
            print('\nCurrently processing:')
        else:
            print('\n[INFO] Processing...')

        for x in range(0, rows, step):
            for y in range(0, cols, step):

                # this should skip the last longitude in the ncfile file
                y = y % 360

                lat = float(sample['latitude'][x, y])
                lon = float(sample['longitude'][x, y])

                row = []

                if verbose:
                    coo = f'lat: {lat}, lon: {lon}, '
                    prg = f'progress (in %): {100 * (x*cols + y) / (rows*cols):.5f}'
                    print(coo + prg, end='\r')

                for var in sample.variables.keys():

                    # i and j are the indices inside ncfile
                    i, j = x // step, y // step

                    # populate the averaged variable
                    if var in self.vars:
                        # filter missing values
                        vals = [float(nc[var][x, y]) for nc in self.data]
                        vals = [val for val in vals if val != (-9999)]

                        # compute the mean
                        val = np.mean(vals)

                        row.append(val)
                        ncfile[var][i, j] = val

                    # populate the none averaged variables
                    else:
                        if len(sample[var].shape) == 2:
                            val = float(self.data[-1][var][x, y])
                            ncfile[var][i, j] = val
                        else:
                            val = float(self.data[-1][var].getValue())
                            ncfile[var].assignValue(val)
                        row.append(val)

                df.loc[len(df)] = row

        # save the results
        df.to_csv(f'Netcdf_Averaging_Work_Monthly_{self.dir}.csv', index=False)
        ncfile.close()

        print('\n[INFO] Done.')
