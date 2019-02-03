import sys
sys.path.append('../')
import configparser
import os
import networkx as nx
import pandas as pd
import influence.influence as inf
import multiprocessing as mp
from functools import partial

if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['dartmouth']
    df = pd.read_pickle(directory + 'dartmouth.pkl')
    delta_t = 4
    t_frame = '2QS'
    place ="dartmouth"
    graphs = directory + 'graphs'
    if not os.path.exists(graphs):
        os.makedirs(graphs)

    workers = (mp.cpu_count()-1)
    pool = mp.Pool(processes=(workers))
    part_func = partial(inf.generate_graphs_from_group, delta_t=delta_t) 
    print('processing groups')
    g_tuples = pool.map(part_func,  df.groupby(pd.Grouper(freq=t_frame)))   
    print('Saving graphs')
    for g_tuple in g_tuples:
        nx.write_gml(g_tuple[0], graphs + "inf_%s_%s.gml" % (place, g_tuple[1]))
