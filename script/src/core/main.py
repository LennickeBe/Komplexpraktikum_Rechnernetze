#!/usr/bin/python3
""" This is the main module of the measurement programm containing the general
    progress structure of a measurement cycle.
"""
import sys
import os
from export.export import Exporter
import importlib                    # import with a string we can create
import inspect                      # get class names of imported modules
import traceback                    # exception handling
import json                         # input string to dict

def run_measurement_module(module_name, args, export):
    """ This function imports the given module from the modules directory
       and initializes the class the module contains with the given args.
       The exporter will be notified of a new measurement and initializes
       it with given data.
       Then the measure() method gets called and the result is returned.
    """

    # we import the lib via the name
    m_mod = importlib.import_module("modules."+module_name)

    export.initializeMeasurement(module_name, 'Measurement of ' + module_name, list(args.keys()))
    
    # one requirement for the module is the position of the test class
    # it is supposed to be the first one so we can load it as follows
    m_class = inspect.getmembers(m_mod)[0][1](**args)
    value = m_class.measure()
    export.setMeasurement(module_name, value, args)
    return value


def main():
    """ This function is the entry point for the 'messprogramm' python
        package. The given arguments are retrieved with the sys library
        as they are given via command line.
        The arguments are parsed and passed along to the measurement.
    """
    # INPUT
    # 3-4 arguments needed (len is one more bc of main.py)
    print(sys.argv)
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python3 main.py gateway_url instance job module (args)")
        sys.exit(os.EX_USAGE)

    gateway_url = sys.argv[1]
    instance = sys.argv[2]
    module = sys.argv[3]

    # if no args we want empty dict
    if len(sys.argv) != 4:
        try:
            args = json.loads(sys.argv[4])
        # json module does not take every valid json
        except json.decoder.JSONDecodeError:
            # e.g. needs " instead of ' in {'test':'bla'}
            # so we replace
            args = sys.argv[4].replace("\'", "\"")
            args = json.loads(args)
    else:
        args = dict()

    # initialize the exporter
    exporter = Exporter(gateway_url, instance, module, args)

    # run the measurement with all arguments
    try:
        print(run_measurement_module(module, args, exporter))
    except Exception as e:
        print("Error with {}".format(module))
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
