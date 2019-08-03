import configparser
import logging
import multiprocessing as mp
import os
import networkx as nx
import metrics_power as mp
import datetime


def parallel(directory):
    try:
        logger.info(">>>>>> files from directory: %s" % directory)
        files = ([file for file in os.listdir(
            directory) if file.endswith('.pkl')])
        for file_name in files:
            file_name = file_name.replace('.pkl', '')
            dir_graph = directory + 'graphs/'
            dir_new = directory + file_name
            if not os.path.exists(dir_new):
                os.makedirs(dir_new)
            logger.info(">>>>>> loading graphs for %s" % file_name)
            support = nx.read_gml(dir_graph + 'support_%s.gml' % file_name)
            attract = nx.read_gml(dir_graph + 'attract_%s.gml' % file_name)
            general = nx.read_gml(dir_graph + "inf_%s.gml" % file_name)

            logger.info(">>>>>> computing support for %s" % file_name)
            df = mp.create_df(support)
            df.to_pickle(dir_new + 'support_%s.pkl' % file_name)
            logger.info(">>>>>> computing attract for %s" % file_name)
            df = mp.create_df(attract)
            df.to_pickle(dir_new + 'attract_%s.pkl' % file_name)
            logger.info(">>>>>> computing independence for %s" % file_name)
            df = mp.independence(general)
            df.to_pickle(dir_new + 'independence_%s.pkl' % file_name)
            logger.info(">>>>>> computing bf_power for %s" % file_name)
            df = mp.df_bozzo_franceschet_power(general)
            df.to_pickle(dir_new + 'bf_%s.pkl' % file_name)
            logger.info(">>>>>> computing eigcen_in for %s" % file_name)
            df = mp.df_eigenvector_centrality_in(general)
            df.to_pickle(dir_new + 'eigcen_in_%s.pkl' % file_name)
            logger.info(">>>>>> computing eigcen_out for %s" % file_name)
            df = mp.df_eigenvector_centrality_out(general)
            df.to_pickle(dir_new + 'eigcen_out_%s.pkl' % file_name)
            logger.info(">>>>>> computing in_dg for %s" % file_name)
            df = mp.df_in_degree_centrality(general)
            df.to_pickle(dir_new + 'dg_cen_in_%s.pkl' % file_name)
            logger.info(">>>>>> computing out_dg for %s" % file_name)
            df = mp.df_out_degree_centrality(general)
            df.to_pickle(dir_new + 'dg_cen_out_%s.pkl' % file_name)
            logger.info(">>>>>> computing pagerank for %s" % file_name)
            df = mp.df_pagerank(general)
            df.to_pickle(dir_new + 'pagerank_%s.pkl' % file_name)
            logger.info(">>>>>> computing betweeness for %s" % file_name)
            df = mp.df_betweenness(general)
            df.to_pickle(dir_new + 'betweeness_%s.pkl' % file_name)
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('script_power_rankings_%s.log' % (
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
