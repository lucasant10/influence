import os
import configparser
import zipfile  
from subprocess import call
import logging


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('script_graphs.log')
    handler.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(consoleHandler)
    
    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    files = ([file for file in os.listdir() if file.endswith('.pkl')])

    for i, file in enumerate(files):
        logger.info(">>>>>> Processing file %i from %i " % ((i + 1), len(files)))
        city = file.replace('.pkl', '').replace('poi_tw_', '')
        logger.info(">>>>>> Creating networks for %s" % city)
        call([
            'python',
            'influence.py',
            '-p', city,
            '-f', file
        ])

        logger.info(">>>>>> Creating Plots for %s" % city)
        call([
            'python',
            'characterization_plot.py',
            '-p', city,
            '-f', file
        ])

        logger.info(">>>>>> Creating Metrics for %s" % city)
        call([
            'python',
            'metrics_power.py',
            '-p', city,
            '-i', 5
        ])

