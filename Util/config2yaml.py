#!/usr/bin/env python

import argparse
import sys
from pprint import pprint

import numpy as np
import yaml

import config
import config_v1

"""
Script to convert old-style WrfHydroForcing .config files to new-style .yaml

Example Usage: 

export PYTHONPATH=$PYTHONPATH:~/git/WrfHydroForcing/
export PYTHONPATH=$PYTHONPATH:~/git/WrfHydroForcing/core
./config2yaml.py ../Test/template_forcing_engine_AnA_v2.config ../Test/template_forcing_engine_AnA_v2.yaml
"""


def conv_class_2_set(klass):
    """
    Returns a set containing tuples of (key,value) for each attribute in a class
    """
    klass_var_set = set()
    for item in vars(klass).items():
        if isinstance(item[1],(list,np.ndarray)):
            klass_var_set.add((item[0],tuple(item[1])))
        else:
            klass_var_set.add(item)

    return klass_var_set


def compare_old_new(config_file, yaml_file):
    """
    Returns a set containing symmetric difference between config file and yaml file
    """
    config_old = config_v1.ConfigOptions(config_file)
    config_old.read_config()
    #pprint(vars(config_old))

    config_new = config.ConfigOptions(yaml_file)
    config_new.read_config()
    #pprint(vars(config_new))

    config_new_set = conv_class_2_set(config_new)
    config_old_set = conv_class_2_set(config_old)
    #pprint(config_new_set)
    #pprint(config_old_set)
    
    return config_new_set^config_old_set


def convert(config_file, yaml_file):
    print("Converting %s -> %s" % (config_file,yaml_file))

    config_old = config_v1.ConfigOptions(config_file)
    config_old.read_config()
    config_params = vars(config_old)
    #pprint(config_params)

    out_yaml = {"Input":[],"Output":{},"Retrospective":{},"Forecast":{},"Geospatial":{},"Regridding":{}, "SuppForcing":{},"Ensembles":{}}
    for i in range(len(config_params['input_forcings'])):
        input_dict = {}
        input_dict["Forcing"] = config.ForcingEnum(config_params['input_forcings'][i]).name
        input_dict["Type"] = config_params['input_force_types'][i]
        input_dict["Dir"] = config_params['input_force_dirs'][i]
        input_dict["Mandatory"] = bool(config_params['input_force_mandatory'][i])
        input_dict["Horizon"] = config_params['fcst_input_horizons'][i]
        input_dict["Offset"] = config_params['fcst_input_offsets'][i]
        input_dict["IgnoredBorderWidths"] = config_params['ignored_border_widths'][i]
        input_dict["RegriddingOpt"] = config.RegriddingOptEnum(config_params['regrid_opt'][i]).name
        input_dict["TemporalInterp"] = config.TemporalInterpEnum(config_params['forceTemoralInterp'][i]).name
        #TODO: custom
        
        out_yaml["Input"].append(input_dict)
    print(yaml.dump(out_yaml,default_flow_style=False))

    #pprint(compare_old_new(config_file, yaml_file))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file",type=str,help="Input old-style .conf file")
    parser.add_argument("yaml_file",type=str,help="Output new-style .yaml file")
    args = parser.parse_args()
    convert(args.config_file,args.yaml_file)


if __name__ == '__main__':
    main()
