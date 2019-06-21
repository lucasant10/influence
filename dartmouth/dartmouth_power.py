import sys
sys.path.append('../')
import configparser
import os
import networkx as nx
import pandas as pd
import multiprocessing as mp
from functools import partial
import influence.power_influence as power


if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['dartmouth']
    directory = directory+"graphs/"

    H = nx.read_gml(directory+"inf_dartmouth_02-11-03.gml")
    print("computing support power")
    support = power.power_support_influence(H)
    file_name = "support_dartmouth_02-11-03.gml"
    print('saving graph %s' % file_name)
    nx.write_gml(support, directory + file_name)
    print("computing attract power")
    attract = power.power_attract_influence(H)
    file_name = "attract_dartmouth_02-11-03.gml"
    print('saving graph %s' % file_name)
    nx.write_gml(attract, directory + file_name)
    file_name = "dartmouth_02-11-03.csv"