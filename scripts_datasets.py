import configparser
import os
import networkx as nx
import pandas as pd
from . import influence
import multiprocessing as mp
from functools import partial
import logging

def parallel(directory):
    try:
        logger.info(">>>>>> files from directory: %s" % directory)
        files = ([file for file in os.listdir(directory) if file.endswith('.pkl')])
        for file in files:
            logger.info(">>>>>> processing file: %s" % file)
            df = pd.read_pickle(directory + file)
            delta_t = 6
            place = file.split('.pkl')[0]
            dir_graphs = directory + 'graphs/'
            if not os.path.exists(dir_graphs):
                os.makedirs(dir_graphs)
            graph  = influence.generate_graphs(df,delta_t)
            logger.info(">>>>>> saving graph for: %s" % place)
            nx.write_gml(graph, dir_graphs + "inf_%s.gml" % place)
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('script_datasets_%s.log' % (
        datetime.datetime.now().strftime('%d_%m_%y')))
    handler.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    # create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(consoleHandler)

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    
    workers = (mp.cpu_count()-1)
    logger.info(">>>>>> number of workes: %i" % workers)
    pool = mp.Pool(processes=(workers))
    _ = pool.map(parallel, path.values())   