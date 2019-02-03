import configparser
import datetime
import logging
import multiprocessing as mp
import os
import re

import networkx as nx
import numpy as np
import pandas as pd

from impact import m_haversine


def remove_trajectories(delta_t, df, t_frame, node, time_param):
    try:
        logger.info(">>>>>> Removing trajectories for node: %s" % node)
        df_list = list()
        for group in df.groupby(pd.Grouper(freq=t_frame)):
            # for each time frame
            time = group[0].strftime("%d-%m-%y")
            if time == time_param:
                time_df = group[1]
                for name in time_df.user.unique():
                    t_user = time_df[time_df.user == name]
                    # Test if the nodes i and j have a time gap less then delta_t
                    diff_t = [True] + list((t_user.iloc[1:, ].index -
                                            t_user.iloc[:-1, ].index).seconds / 3600 <= delta_t)
                    # get index for split dataframe in paths
                    split_index = [i for i, x in enumerate(diff_t) if not x]
                    for path_df in split(t_user, split_index):
                        if not node in path_df.poi_id.values:
                            df_list.append(path_df)
        return pd.concat(df_list)
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)


def split(df, splitters):
    start = 0
    for index in splitters:
        yield df[start:index]
        start = index
    yield df[start:]


def poi_remove_impact(df, node, date):
    try:
        logger.info(">>>>>> Computing impact for node neighborhood: %s" % node)
        neighbors = get_neighbors(df, node)
        df_before = df[df.poi_id.isin(neighbors)]
        tmp_b = df_before.groupby('poi_id').size().reset_index(name='before')
        df_rem = remove_trajectories(4, df, '2QS', node, date)
        df_after = df_rem[df_rem.poi_id.isin(neighbors)]
        tmp_a = df_after.groupby('poi_id').size().reset_index(name='after')
        result = pd.merge(tmp_b, tmp_a, how='outer', on="poi_id")
        result.fillna(0, inplace=True)
        result['date'] = date
        return result
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)


def get_neighbors(city_tw, node):
    try:
        logger.info(">>>>>> Getting neighborhood for node: %s" % node)
        poi_id_list = city_tw.poi_id.unique()
        selec_poi = list()
        for poi in poi_id_list:
            p1 = city_tw[city_tw.poi_id == int(node)].poi_loc.values[0]
            p2 = city_tw[city_tw.poi_id == poi].poi_loc.values[0]
            if m_haversine((p1.x, p1.y), (p2.x, p2.y)) <= 2000:
                selec_poi.append(poi)
        return selec_poi
        
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)


def get_nb_impact(file):
    try:
        # get first part of string like san_francisco_10_...
        city = re.split(r"_\d", file)[0]
        date = re.search(r"(\d+\-\d+\-\d+)", file)[0]
        df = pd.read_pickle(directory + file)
        logger.info(">>>>>> Computing start for city: %s" % city)
        # get highest power poi
        city_tw = pd.read_pickle(dataset + 'poi_tw_%s.pkl' % city)
        metrics = ['support', 'attract', 'in_dg_cen', 'out_dg_cen', 'bf_power', 'eigcen_in', 'eigcen_out', 'random']
        df_list = []
        for metric in metrics:
            tmp = poi_remove_impact(city_tw, get_highest_node(df, metric), date)
            tmp['metric'] = metric
            tmp['city'] = city
            df_list.append(tmp) 
        result = pd.concat(df_list)
        logger.info(">>>>>> Finished for city: %s" % city)
        return result
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)

def get_highest_node(df, metric):
    try:
        if metric == 'random':
            return int(df.loc[df.iter == 0].sample(random_state=1).poi_id.values[0])
        return int(df.loc[(df.iter == 0) & (df.metric == metric)].poi_id.values[0])
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('neighbors_impact_%s.log' % (
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
    dataset = path['dataset']

    directory = dataset + 'graphs/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # files = ([file for file in os.listdir(directory)
    #           if re.match(r'.*\d_metrics.pkl', file)])
    files = ([file for file in os.listdir(directory)
                if re.match(r'dallas.*\d_metrics.pkl', file)])
    
    workers = (mp.cpu_count()-1)
    logger.info(">>>>>> number of workes: %i" % workers)
    pool = mp.Pool(processes=(workers))
    logger.info(">>>>>> Call functions with multiprocessing")
    data_frames = pool.map(get_nb_impact, files)
    logger.info(">>>>>> Concatenating DF")
    df_cont = pd.concat(data_frames)
    logger.info(">>>>>> Saving DF")
    df_cont.to_pickle(dataset + 'poi_remove_impact.pkl')
