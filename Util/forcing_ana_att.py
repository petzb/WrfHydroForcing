#!/usr/bin/env python

import os
import sys
from datetime import datetime, timedelta
from datetime import timezone

import netCDF4

def main():
    if len(sys.argv) != 9:
        print("usage: python forcing_ana_att.py input_file initial_time output_time tothr yyyy mon dd hh", file=sys.stderr)
        sys.exit(1)

    inout_file = sys.argv[1]
    initial_time = sys.argv[2]
    output_time = sys.argv[3]
    tothr = int(sys.argv[4])
    yyyy = int(sys.argv[5])
    mon = int(sys.argv[6])
    day = int(sys.argv[7])
    hh = int(sys.argv[8])
    
    if not os.path.exists(inout_file):
        print("Input file not found: {}".format(inout_file), file=sys.stderr)
        sys.exit(1)
    
    dt_beg = datetime(yyyy,mon,day,hh,tzinfo=timezone.utc)
    #minutes since 1970-01-01 00:00:00 UTC
    time_min = int(dt_beg.timestamp()/60)
    time_max = int((dt_beg + timedelta(hours = tothr)).timestamp()/60)
    reference_time = time_min
    
    try: 
       ioF = netCDF4.Dataset(inout_file,"r+", format="NETCDF4")
    except IOError as e:
       print("Could not open file {}: {}".format(inout_file, e.args[1]), file=sys.stderr)
       exit(2)
         
    ioF['reference_time'].units = "minutes since 1970-01-01 00:00:00 UTC"
    ioF['reference_time'].standard_name = "forecast_reference_time"
    ioF['reference_time'].long_name = "model initialization time"

    ioF.model_initialization_time = initial_time
    ioF.model_output_valid_time = output_time
    ioF.model_output_type = "forcing"
    ioF.model_configuration="analysis_and_assimilation"
    ioF.model_total_valid_times = tothr

    ioF.variables['time'].valid_max = time_max
    ioF.variables['time'].valid_min = time_min

    ioF.variables['reference_time'][:] = reference_time

    ioF.close()


if __name__ == '__main__':
    main()
