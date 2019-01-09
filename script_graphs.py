import os
import configparser
import zipfile  
from subprocess import call
import logging
import datetime
import multiprocessing as mp


def call_functions(file):
    logger.info(">>>>>> Processing file %s" % file)
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
    logger.info(">>>>>> Finished for %s"  % city)
    # logger.info(">>>>>> Creating Metrics for %s" % city)
    # call([
    #     'python',
    #     'metrics_power.py',
    #     '-p', city,
    #     '-i', '5'
    # ])


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('script_graphs_%s.log' %(datetime.datetime.now().strftime('%d_%m_%y')))
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
    logger.info(">>>>>> start processing")
    workers = (mp.cpu_count()-1)
    logger.info(">>>>>> number of workes: %i" % workers)
    pool = mp.Pool(processes=(workers))
    logger.info(">>>>>> Call functions with multiprocessing")
    _ = pool.map(call_functions, files)
    
        

