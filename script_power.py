import configparser
import logging
import multiprocessing as mp
import os
import networkx as nx
import power_influence as power
import datetime


def parallel(directory):
    try:
        directory = directory + 'graphs/'
        logger.info(">>>>>> graphs from directory: %s" % directory)
        files = ([file for file in os.listdir(
            directory) if (file.startswith('inf_') and file.endswith('.gml'))])
        for file in files:
            logger.info(">>>>>> loading %s" % file)
            H = nx.read_gml(directory + file)
            logger.info(">>>>>> computing support power %s" % file)
            support = power.power_support_influence(H)
            file_name = file.replace("inf", "support")
            logger.info(">>>>>> saving graph %s" % file_name)
            nx.write_gml(support, directory + file_name)
            logger.info(">>>>>> computing attract power %s" % file)
            attract = power.power_attract_influence(H)
            file_name = file.replace("inf", "attract")
            logger.info(">>>>>> saving graph %s" % file_name)
            nx.write_gml(attract, directory + file_name)
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('script_power_%s.log' % (
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
