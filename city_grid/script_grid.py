import sys
sys.path.append('../')
import configparser
from subprocess import call
import logging
import datetime
import multiprocessing as mp
import os



def parallel(directory):
    try:
        logger.info(">>>>>> graphs from directory: %s" % directory)
        files = ([file for file in os.listdir(
            directory) if (file.endswith('.pkl'))])
        for file in files:
            city = file.replace('.pkl', '')
            tw_bool = False
            if(city.startswith("poi_tw")):
                tw_bool = True

            logger.info(">>>>>> Processing city: %s" % city)
            call([
                'python',
                'indepence_hash.py',
                '-p', city,
                '-d', directory,
                '-t', str(tw_bool)
            ])
           
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)

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
    cf.read("../file_path.properties")
    path = dict(cf.items("file_path"))
    workers = (3)
    logger.info(">>>>>> number of workes: %i" % workers)
    pool = mp.Pool(processes=(workers))
    _ = pool.map(parallel, path.values())