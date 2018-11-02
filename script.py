import os
import configparser
import zipfile  
from subprocess import call
import logging


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('script.log')
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
    zip_files = path['dataset']
    
    files = ([file for file in os.listdir(zip_files) if file.endswith('.zip')])
    
    tmp_dir = zip_files + 'tmp/'
    for i, file in enumerate(files):
        logger.info(">>>>>> Processing file %i from %i " % ((i + 1), len(files)))
        logger.info(">>>>>> Extract file %s" % file )
        zipfile.ZipFile(zip_files + file).extractall(tmp_dir)
        data_file  = [f for f in os.listdir(tmp_dir) if f.endswith('.json')][0]
        city = file.replace('.zip', '').replace('_', ' ')
        
        logger.info(">>>>>> Calculating Impact for %s" % city)
        call([
            'python',
            'impact.py',
            '-d', '30',
            '-p', city,
            '-f', tmp_dir + data_file
        ])

        city = file.replace('.zip', '')
        file = 'poi_tw_%s.pkl' % city
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

        logger.info(">>>>>> Removing tmp files")
        call([
            'rm',
            '-rf',
            tmp_dir
        ])

