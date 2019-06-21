import sys
sys.path.append('../')
import datetime
import logging
import os
import configparser
import networkx as nx
import pandas as pd
import influence.metrics_power as mp


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('metrics_power_%s.log' % (
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
    directory = path['dartmouth'] + "graphs/"


    support = nx.read_gml(directory + 'support_dartmouth_02-11-03.gml')
    attract = nx.read_gml(directory + 'attract_dartmouth_02-11-03.gml')
    general = nx.read_gml(directory + "inf_dartmouth_02-11-03.gml")

    df = mp.create_df(support)
    df.to_pickle(directory + 'support_dartmouth_02-11-03.pkl')
    df = mp.create_df(attract)
    df.to_pickle(directory + 'attract_dartmouth_02-11-03.pkl')
    df = mp.independence(general)
    df.to_pickle(directory + 'independence_dartmouth_02-11-03.pkl')
    # df = mp.df_bozzo_franceschet_power(general)
    # df.to_pickle(directory + 'bf_dartmouth_02-11-03.pkl')
    # df = mp.df_eigenvector_centrality_in(general)
    # df.to_pickle(directory + 'eigcen_in_dartmouth_02-11-03.pkl')
    # df = mp.df_eigenvector_centrality_out(general)
    # df.to_pickle(directory + 'eigcen_out_dartmouth_02-11-03.pkl')
    # df = mp.df_in_degree_centrality(general)
    # df.to_pickle(directory + 'dg_cen_in_dartmouth_02-11-03.pkl')
    # df = mp.df_out_degree_centrality(general)
    # df.to_pickle(directory + 'dg_cen_out_dartmouth_02-11-03.pkl')
    