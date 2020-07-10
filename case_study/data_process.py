import sys
sys.path.append('../')
import metrics_power
import datetime
import networkx as nx
import influence
import pandas as pd
import multiprocessing as mp
import logging
import os
import configparser

def parallel(graph):
    try:
        logger.info(">>>>>> loading graphs for %s" % graph)
        filename = graph.replace('inf', 'df').replace('gml', 'pkl')
        G = nx.read_gml(graph)
        metrics_list = list()
        logger.info(">>>>>> computing support for %s" % graph)
        metrics_list.append(metrics_power.df_support(G))
        logger.info(">>>>>> computing attract for %s" % graph)
        metrics_list.append(metrics_power.df_attract(G))
        logger.info(">>>>>> computing bf_power for %s" % graph)
        metrics_list.append(metrics_power.df_bozzo_franceschet_power(G))
        logger.info(">>>>>> computing eigcen_in for %s" % graph)
        metrics_list.append(metrics_power.df_eigenvector_centrality_in(G))
        logger.info(">>>>>> computing eigcen_out for %s" % graph)
        metrics_list.append(metrics_power.df_eigenvector_centrality_out(G))
        logger.info(">>>>>> computing in_dg for %s" % graph)
        metrics_list.append(metrics_power.df_in_degree_centrality(G))
        logger.info(">>>>>> computing out_dg for %s" % graph)
        metrics_list.append(metrics_power.df_out_degree_centrality(G))
        logger.info(">>>>>> computing pagerank for %s" % graph)
        metrics_list.append(metrics_power.df_pagerank(G))
        logger.info(">>>>>> computing betweeness for %s" % graph)
        metrics_list.append(metrics_power.df_betweenness(G))
        df = pd.concat(metrics_list)
        df.to_pickle(filename)
    except Exception as e:
            print("Unexpected error: {}".format(e))
            logger.exception(e)


def create_graphs(samples, dir_name):
    list_df = list()
    delta_t = 6
    last_date = None
    for i in range(len(samples)):
        list_df.append(samples[i][1])
        last_date = samples[i][0]
    df = pd.concat(list_df)
    M, time = influence.generate_graphs_from_group(
        df, delta_t, last_date.strftime("%d-%m-%y"))
    nx.write_gml(M, os.path.join(dir_name, "inf_%s.gml" % time))


if __name__ == "__main__":

    logger=logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler=logging.FileHandler('data_process_%s.log' % (
        datetime.datetime.now().strftime('%d_%m_%y')))
    handler.setLevel(logging.INFO)
    consoleHandler=logging.StreamHandler()
    # create a logging format
    formatter=logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(consoleHandler)

    cf=configparser.ConfigParser()
    cf.read("../file_path.properties")
    path=dict(cf.items("file_path"))
    directory=path['gowalla']
    window='2W'

    try:
        dir_path=os.path.join(directory, 'case_study')
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)

    # files=([file for file in os.listdir(directory) if file.endswith('.pkl')])
    files = ['Dallas.pkl']
    for filename in files:
        # load df
        df=pd.read_pickle(os.path.join(directory, filename))
        # remove pois less than 10 visits
        df_tmp=df.groupby('poi_id').count()
        df=df[df.poi_id.isin(df_tmp[df_tmp.city > 10].index.unique())]
        # resample by time window
        sampled_list=list(df.resample(window))
        dir_name=os.path.join(dir_path, filename.replace('.pkl', ''))
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        for index in range(2, len(sampled_list)):
            create_graphs(sampled_list[(index-2):index], dir_name)

        graphs=([os.path.join(dir_name, file) for file in os.listdir(dir_name)
                if file.startswith('inf') and file.endswith('.gml')])

        workers=(mp.cpu_count()-1)
        logger.info(">>>>>> number of workes: %i" % workers)
        pool=mp.Pool(processes=(workers))
        _=pool.map(parallel, graphs)
